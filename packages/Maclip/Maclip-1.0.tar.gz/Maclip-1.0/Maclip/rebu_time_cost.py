# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 18:31:56 2025

@author: h'p
"""
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 14:32:48 2025

@author: Administrator
"""
import os
import torch
import torch.nn as nn
import clip
from clip_model import load
from torch import randint

import json, random
from tqdm import tqdm
import numpy as np

import sys
import torch.nn.functional as F
from scipy.stats import spearmanr, pearsonr
from scipy.stats import kendalltau

from PIL import Image, ImageFilter
import pyiqa
import ipdb
from torchvision.transforms import Compose as torchcompose
from torchvision.transforms import Resize, CenterCrop, ToTensor, Normalize
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
import cv2
import matplotlib.pyplot as plt
from plcc_srcc_cal import correlation_evaluation

import pandas as pd
from utils import get_logger, log_and_print

OPENAI_CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
OPENAI_CLIP_STD = (0.26862954, 0.26130258, 0.27577711)

from torchvision.transforms.functional import InterpolationMode

def nrm_process(img, size=224):
    process = torchcompose([
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])
    return process(img)

def agiqa1k_nrm_process(img, size=224):
    process = torchcompose([
        # Resize(size),
        Resize((size, size), interpolation=InterpolationMode.BICUBIC),
        # CenterCrop(size),
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])
    return process(img)


class CLIPIQA(nn.Module):

    def __init__(self,
                 model_type='clipiqa',
                #  backbone='ViT-B/32',
                 backbone='RN50',
                 pretrained=True,
                 pos_embedding=False) -> None:
        super().__init__()

        self.clip_model = load(backbone, 'cpu')  # avoid saving clip weights
        # Different from original paper, we assemble multiple prompts to improve performance
        self.prompt_pairs = clip.tokenize([
            'Good image', 'bad image',
            'Sharp image', 'blurry image',
            'sharp edges', 'blurry edges',
            'High resolution image', 'low resolution image',
            'Noise-free image', 'noisy image',
        ])

        self.default_mean = torch.Tensor(OPENAI_CLIP_MEAN).view(1, 3, 1, 1)
        self.default_std = torch.Tensor(OPENAI_CLIP_STD).view(1, 3, 1, 1)

        self.model_type = model_type
        self.pos_embedding = pos_embedding
        # self.clip_model = self.clip_model.cuda()
   
        for p in self.clip_model.parameters():
            p.requires_grad = False
 
    def forward(self, x):
        clip_model = self.clip_model.to(x.device)
        prompts = self.prompt_pairs.to(x.device)
        logits_per_image, logits_per_text,nrm_score = clip_model(x, prompts, pos_embedding=self.pos_embedding)
        probs = logits_per_image.reshape(logits_per_image.shape[0], -1, 2).softmax(dim=-1)

        return probs[..., 0].mean(dim=1, keepdim=True), nrm_score
    

def perceptual_box_cox_transform3(x, lam=0.5, alpha=0.2, epsilon=1e-6):
    # 3. Perceptual transformation
    # x = (x - x.mean(dim=1, keepdim=True)) / (x.std(dim=1, keepdim=True) + epsilon)  # [B, D]
    # x = torch.abs(x) # [B, D]
    x = (x) / (x.std(dim=1, keepdim=True) + epsilon)  # [B, D]
    # box-cox
    transformed = ((x + 1) ** lam - 1) / lam

    return transformed

def dynamic_weighted_metric(cos, norm, base_cos=1.0, base_norm=0.6, alpha=1.0):
    d = cos - norm # 差值
    # 生成权重参数：d越大，cos权重越高；d越小，norm权重越高
    # d = torch.sigmoid(d)
    cos_param = base_cos + alpha * d
    norm_param = base_norm - alpha * d
    # 应用softmax归一化
    weights = F.softmax(torch.stack([cos_param, norm_param], dim=-1), dim=-1)  # [B, 2]
    w_cos, w_norm = weights.unbind(dim=-1)  # [B], [B]
    # 计算加权指标
    weighted_metric = w_cos * cos + w_norm * norm
    return weighted_metric, w_cos, w_norm

def plot_fig(x, file_name):
    features = x.flatten()
    # 绘制直方图
    plt.figure(figsize=(10, 6))
    plt.hist(features, bins=30, color='skyblue', edgecolor='black')
    plt.title("Distribution of 512-Dimensional Features")
    plt.xlabel("Feature Value")
    plt.ylabel("Frequency")
    # plt.show()
    plt.savefig(file_name)
    plt.close()


import time  # 添加时间模块
# -----------------------------主函数-------------------------------
def main(image_paths, jsons, datasets):

    iqa_metric = pyiqa.create_metric('clipiqa').cuda()
    iqamodel = CLIPIQA().cuda()
    # test_len =1000
    unfold = nn.Unfold(kernel_size=(224, 224), stride=128)
    
    # 添加时间记录变量
    total_clip_time = 0.0
    total_boxcox_time = 0.0
    total_fusion_time = 0.0
    total_images = 0
    org_clipiqa_time = 0.0
    
    with torch.set_grad_enabled(False):
        for image_path, input_json in zip(image_paths, jsons):
            with open(input_json) as f:
                all_data = json.load(f)
                gts = [float(di["gt_score"]) for di in all_data]
                # all_data = all_data[0:test_len]
                # gts = gts[0:test_len]
            
            prs0 = []
            prs1 = []
            prs2 = []
            prs3 = []
            prs4 = []
            w1_list = []
            w2_list = []
            
            # ref_nrm = []
            # ref_clip = []

            for llddata in tqdm(all_data):
                name = llddata["img_path"]
                raw_image_ini = Image.open(image_path + name).convert("RGB")
                raw_image = nrm_process(raw_image_ini).unsqueeze(0)

                X_sub = unfold(raw_image).view(1, 3, 224, 224, -1)[0]
                X_sub = X_sub.permute(3,0,1,2).cuda()

                I_resized = F.interpolate(raw_image, size=(224, 224), mode='bilinear', align_corners=False).to('cuda')
                X_sub = torch.cat([X_sub, I_resized], dim=0) # 将patches与resize后的图片拼接，在patch维度多加一张原图                
                
                # 1. CLIP特征提取时间测量
                clip_start_time = time.time()
                clipiqa, image_features_org = iqamodel(X_sub) 
                torch.cuda.synchronize()  # 确保GPU操作完成
                clip_end_time = time.time()
                clip_time = clip_end_time - clip_start_time
                total_clip_time += clip_time
                
                # 2. Box-Cox变换时间测量
                boxcox_start_time = time.time()
                image_features_org_abs = torch.abs(image_features_org)
                nrm_score = image_features_org_abs.mean(dim=-1)
                image_features_org_abs_box = perceptual_box_cox_transform3(image_features_org_abs, lam=0.5)
                nrm_score2 = image_features_org_abs_box.mean(dim=-1)
                torch.cuda.synchronize()  # 确保GPU操作完成
                boxcox_end_time = time.time()
                boxcox_time = boxcox_end_time - boxcox_start_time
                total_boxcox_time += boxcox_time
                
                # 3. 融合时间测量
                fusion_start_time = time.time()
                comb, w1, w2 = dynamic_weighted_metric(clipiqa.squeeze(1), nrm_score2)
                torch.cuda.synchronize()  # 确保GPU操作完成
                fusion_end_time = time.time()
                fusion_time = fusion_end_time - fusion_start_time
                total_fusion_time += fusion_time
                
                total_images += 1

                predq0 = torch.mean(nrm_score2)
                predq1 = torch.mean(nrm_score)
                org_start_time = time.time()
                predq2 = iqa_metric(raw_image_ini)
                torch.cuda.synchronize()  # 确保GPU操作完成
                org_end_time = time.time()
                org_time = org_end_time - org_start_time
                org_clipiqa_time += org_time
                predq3 = torch.mean(clipiqa)
                predq4 = torch.mean(comb)
               
                prs0.append(predq0.squeeze().cpu().numpy()) 
                prs1.append(predq1.squeeze().cpu().numpy())
                prs2.append(predq2.squeeze().cpu().numpy())
                prs3.append(predq3.squeeze().cpu().numpy())
                prs4.append(predq4.squeeze().cpu().numpy())
                w1_list.append(w1.mean().cpu().numpy())
                w2_list.append(w2.mean().cpu().numpy())

        # 计算平均时间
        avg_clip_time = total_clip_time / total_images * 1000  # 转换为毫秒
        avg_boxcox_time = total_boxcox_time / total_images * 1000
        avg_fusion_time = total_fusion_time / total_images * 1000
        avg_org_time = org_clipiqa_time / total_images * 1000
        avg_total_time = avg_clip_time + avg_boxcox_time + avg_fusion_time
        
        # 输出时间统计
        log_and_print(base_logger, msg='------- 时间统计 ---------')
        log_and_print(base_logger, msg=f"CLIP特征提取: {avg_clip_time:.2f} ms/图像")
        log_and_print(base_logger, msg=f"Box-Cox变换: {avg_boxcox_time:.2f} ms/图像")
        log_and_print(base_logger, msg=f"融合计算: {avg_fusion_time:.2f} ms/图像")
        log_and_print(base_logger, msg=f"总处理时间: {avg_total_time:.2f} ms/图像")
        log_and_print(base_logger, msg=f"原pyiqa中clipiqa时间: {avg_org_time:.2f} ms/图像")
        log_and_print(base_logger, msg=f"处理图像总数: {total_images}")
        
        # 性能结果输出
        log_and_print(base_logger, msg='-------nrm-adv---------')
        plcc, srcc, rmse = correlation_evaluation(prs0, gts,is_plot=False, plot_path="")
        log_and_print(base_logger, msg="SRCC:{:.4f}, PLCC:{:.4f}, RMSE{:.4f}".format(srcc,plcc,rmse))

        log_and_print(base_logger, msg='-------nrm---------')
        plcc, srcc, rmse = correlation_evaluation(prs1, gts,is_plot=False, plot_path="")
        log_and_print(base_logger, msg="SRCC:{:.4f}, PLCC:{:.4f}, RMSE{:.4f}".format(srcc,plcc,rmse))

        log_and_print(base_logger, msg='-------pyiqa---------')
        plcc, srcc, rmse = correlation_evaluation(prs2, gts,is_plot=False, plot_path="")
        log_and_print(base_logger, msg="SRCC:{:.4f}, PLCC:{:.4f}, RMSE{:.4f}".format(srcc,plcc,rmse))

        log_and_print(base_logger, msg='-------myclipiqa---------')
        plcc, srcc, rmse = correlation_evaluation(prs3, gts,is_plot=False, plot_path="")
        log_and_print(base_logger, msg="SRCC:{:.4f}, PLCC:{:.4f}, RMSE{:.4f}".format(srcc,plcc,rmse))

        log_and_print(base_logger, msg='-------comb---------')
        plcc, srcc, rmse = correlation_evaluation(prs4, gts,is_plot=False, plot_path="")
        log_and_print(base_logger, msg="SRCC:{:.4f}, PLCC:{:.4f}, RMSE{:.4f}".format(srcc,plcc,rmse))

    df = pd.DataFrame({
        'GMOS': gts, 
        'comb': prs4,
        'clipiqa_cos': prs3,
        'nrm-adv': prs0,
        'nrm': prs1,
        'w1':w1_list,
        'w2':w2_list,
    })
    df.to_csv(checkpoint_dir+'/'+datasets+'_result.csv', index=False)
    
    # 返回时间统计结果
    return {
        'dataset': datasets,
        'avg_clip_time_ms': avg_clip_time,
        'avg_boxcox_time_ms': avg_boxcox_time,
        'avg_fusion_time_ms': avg_fusion_time,
        'avg_total_time_ms': avg_total_time,
        'total_images': total_images
    }


checkpoint_dir = 'rebuttal/time_cost'
score_type = 'mos'

os.makedirs(checkpoint_dir,exist_ok = True)
base_logger = get_logger(os.path.join(checkpoint_dir,'train_test.log'), 'log')



if __name__ == '__main__':
    image_paths_all = [
        "/data/cbl/IQA/datasets/live/", 
        "/data/cbl/IQA/datasets/kadid10k/images/",
        "/data/cbl/IQA/datasets/koniq-10k/1024x768/",
        "/data/cbl/IQA/zhicheng/AGRM/data/AGIQA-3K/",
        "/data/cbl/IQA/datasets/SIQAD/DistortedImages/",
        '/data/cbl/IQA/datasets/CSIQ/dst_imgs_all/',
        '/data/cbl/IQA/datasets/TID2013/distorted_images/',
        # 'cdcdsno'
    ]
    json_prefix = "./jsons/"
    dataset_config = {
        "livec": [json_prefix + "livec.json"],
        "kadid": [json_prefix + "kadid.json"],
        "koniq": [json_prefix + "koniq.json"],
        "AGIQA-3k": [json_prefix + "AGIQA-3k.json"],
        "SIQAD": [json_prefix + "SIQAD.json"],
        "CSIQ": [json_prefix + "csiq.json"],
        "TID2013": [json_prefix + "tid2013.json"],
        # "SPAQ": [json_prefix + "spaq.json"],
    }

    # 收集所有数据集的时间统计
    timing_results = []
    
    for idx, (dataset_name, json_paths) in enumerate(dataset_config.items()):
        image_paths = [image_paths_all[idx]] 
        # import pdb;pdb.set_trace()
        timing_result = main(image_paths, json_paths, dataset_name)
        timing_results.append(timing_result)
    
    # 输出总体时间统计
    log_and_print(base_logger, msg='\n------- 总体时间统计 ---------')
    for result in timing_results:
        log_and_print(base_logger, 
            msg=f"{result['dataset']}: CLIP={result['avg_clip_time_ms']:.2f}ms, "
                f"BoxCox={result['avg_boxcox_time_ms']:.2f}ms, "
                f"Fusion={result['avg_fusion_time_ms']:.2f}ms, "
                f"Total={result['avg_total_time_ms']:.2f}ms")
    
    # 计算平均时间
    avg_clip = np.mean([r['avg_clip_time_ms'] for r in timing_results])
    avg_boxcox = np.mean([r['avg_boxcox_time_ms'] for r in timing_results]) 
    avg_fusion = np.mean([r['avg_fusion_time_ms'] for r in timing_results])
    avg_total = np.mean([r['avg_total_time_ms'] for r in timing_results])
    
    log_and_print(base_logger, 
        msg=f"平均值: CLIP={avg_clip:.2f}ms, BoxCox={avg_boxcox:.2f}ms, "
            f"Fusion={avg_fusion:.2f}ms, Total={avg_total:.2f}ms")
    
    # 保存时间统计到CSV
    timing_df = pd.DataFrame(timing_results)
    timing_df.to_csv(checkpoint_dir + '/timing_analysis.csv', index=False)