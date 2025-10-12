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
from torchvision.transforms import Resize, CenterCrop, ToTensor, Normalize, RandomHorizontalFlip
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
import torchvision.transforms.functional as TF  
def SCI_nrm_process(img):
     
    x = TF.to_tensor(img).unsqueeze(0)  
    default_mean = torch.Tensor(OPENAI_CLIP_MEAN).view(1, 3, 1, 1)
    default_std = torch.Tensor(OPENAI_CLIP_STD).view(1, 3, 1, 1)
    x = (x - default_mean.to(x)) / default_std.to(x)
    return x

def nrm_process(img, size=448):
    process = torchcompose([
        ToTensor(),
        Resize((size, size), interpolation=InterpolationMode.BICUBIC),
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
    if lam == 0:
        transformed = torch.log(x+1)
    else:
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


# -----------------------------主函数-------------------------------
def main(image_paths, jsons, datasets):

    iqa_metric = pyiqa.create_metric('clipiqa').to('cuda')
    iqamodel = CLIPIQA().to('cuda')
    # test_len =1000
    unfold = nn.Unfold(kernel_size=(224, 224), stride=128)
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

            for llddata in tqdm(all_data):
                name = llddata["img_path"]
                raw_image_ini = Image.open(image_path + name).convert("RGB")
                raw_image = nrm_process(raw_image_ini).unsqueeze(0)

                X_sub = unfold(raw_image).view(1, 3, 224, 224, -1)[0]
                X_sub = X_sub.permute(3,0,1,2).cuda()

                I_resized = F.interpolate(raw_image, size=(224, 224), mode='bilinear', align_corners=False).to('cuda')
                X_sub = torch.cat([X_sub, I_resized], dim=0) # 将patches与resize后的图片拼接，在patch维度多加一张原图   

                if datasets == 'CCT_SCI' or datasets == 'SCID':
                    X_sub = SCI_nrm_process(raw_image_ini).to('cuda')
                clipiqa, image_features_org = iqamodel(X_sub) 
                
                # box-cox1
                image_features_org_abs = torch.abs(image_features_org)
                nrm_score = image_features_org_abs.mean(dim=-1)
                image_features_org_abs_box = perceptual_box_cox_transform3(image_features_org_abs, lam=0)
                nrm_score2 = image_features_org_abs_box.mean(dim=-1)
                # comb, w1, w2 = dynamic_weighted_metric(clipiqa.squeeze(1), nrm_score2, base_cos=0.6, base_norm=-2, alpha=1.0) 
                comb, w1, w2 = dynamic_weighted_metric(clipiqa.squeeze(1), nrm_score2)

                predq0 = torch.mean(nrm_score2)
                predq1 = torch.mean(nrm_score)
                predq2 = iqa_metric(raw_image_ini)
                predq3 = torch.mean(clipiqa)
                predq4 = torch.mean(comb)
               
                prs0.append(predq0.squeeze().cpu().numpy()) 
                prs1.append(predq1.squeeze().cpu().numpy())
                prs2.append(predq2.squeeze().cpu().numpy())
                prs3.append(predq3.squeeze().cpu().numpy())
                prs4.append(predq4.squeeze().cpu().numpy())
                w1_list.append(w1.mean().cpu().numpy())
                w2_list.append(w2.mean().cpu().numpy())

        log_and_print(base_logger, msg=f'dataset: {input_json}')   
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

        # print('-------nrm-adv---------')
        # rmse = np.sqrt(np.mean((np.array(prs0) - np.array(gts)) ** 2))
        # print("SRCC:{:.4f}, PLCC:{:.4f}, RMSE:{:.4f}".format(spearmanr(gts, prs0)[0], pearsonr(gts, prs0)[0], rmse))
        
        # print('-------nrm---------')
        # rmse = np.sqrt(np.mean((np.array(prs1) - np.array(gts)) ** 2))
        # print("SRCC:{:.4f}, PLCC:{:.4f}, RMSE:{:.4f}".format(spearmanr(gts, prs1)[0], pearsonr(gts, prs1)[0], rmse))

        # print('-------pyiqa---------')
        # rmse = np.sqrt(np.mean((np.array(prs2) - np.array(gts)) ** 2))
        # print("SRCC:{:.4f}, PLCC:{:.4f}, RMSE:{:.4f}".format(spearmanr(gts, prs2)[0], pearsonr(gts, prs2)[0], rmse))

        # print('-------myclipiqa---------')
        # rmse = np.sqrt(np.mean((np.array(prs3) - np.array(gts)) ** 2))
        # print("SRCC:{:.4f}, PLCC:{:.4f}, RMSE:{:.4f}".format(spearmanr(gts, prs3)[0], pearsonr(gts, prs3)[0], rmse))
        
        # print('-------comb---------')
        # rmse = np.sqrt(np.mean((np.array(prs4) - np.array(gts)) ** 2))
        # print("SRCC:{:.4f}, PLCC:{:.4f}, RMSE:{:.4f}".format(spearmanr(gts, prs4)[0], pearsonr(gts, prs4)[0], rmse))

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


def run_base_constant_ablation(dataset_config, image_paths_all):
    """专门的基础常数消融研究"""
    import itertools
    
    # 测试参数范围
    base_cos_values = [0.6, 1.0]
    base_norm_values = [-2,-0.2, 0.2, 0.4, 0.6, 1.0, 1.4]
    # alpha_values = [1.0]

    # base_cos_values = [1.0]
    # base_norm_values = [0.6]
    alpha_values = [0.2, 0.5, 1.0, 1.5, 2.0]
    
    results_summary = []
    
    for dataset_name, json_paths in dataset_config.items():
        image_path = image_paths_all[list(dataset_config.keys()).index(dataset_name)]
        
        with open(json_paths[0]) as f:
            all_data = json.load(f)
            gts = [float(di["gt_score"]) for di in all_data]
        
        iqa_metric = pyiqa.create_metric('clipiqa').cuda()
        iqamodel = CLIPIQA().to('cuda')
        unfold = nn.Unfold(kernel_size=(224, 224), stride=128)
        
        # 预计算特征以避免重复计算
        log_and_print(base_logger, msg=f"预计算 {dataset_name} 的特征...")
        features_cache = []

        for llddata in tqdm(all_data):
            name = llddata["img_path"]
            raw_image_ini = Image.open(image_path + name).convert("RGB")
            raw_image = nrm_process(raw_image_ini).unsqueeze(0)

            X_sub = unfold(raw_image).view(1, 3, 224, 224, -1)[0]
            X_sub = X_sub.permute(3,0,1,2).cuda()

            I_resized = F.interpolate(raw_image, size=(224, 224), mode='bilinear', align_corners=False).to('cuda')
            X_sub = torch.cat([X_sub, I_resized], dim=0) # 将patches与resize后的图片拼接，在patch维度多加一张原图   

            if dataset_name == 'CCT_SCI' or dataset_name == 'SCID':
                    X_sub = SCI_nrm_process(raw_image_ini).to('cuda')
            clipiqa, image_features_org = iqamodel(X_sub) 
            
            # box-cox1
            image_features_org_abs = torch.abs(image_features_org)
            nrm_score = image_features_org_abs.mean(dim=-1)
            image_features_org_abs_box = perceptual_box_cox_transform3(image_features_org_abs, lam=0)
            nrm_score2 = image_features_org_abs_box.mean(dim=-1)


            features_cache.append({
                'clipiqa': clipiqa.squeeze(1).cpu(),
                'nrm_score2': nrm_score2.cpu(),
                'gt': float(llddata["gt_score"])
            })
        
        # 参数搜索
        log_and_print(base_logger, msg=f"开始 {dataset_name} 的参数搜索...")
        
        for base_cos, base_norm, alpha in itertools.product(base_cos_values, base_norm_values, alpha_values):
            if (base_cos == base_norm) and base_cos != 1.0:
                continue
            prs = []
            current_gts = []
            
            for feature in features_cache:
                clipiqa = feature['clipiqa'].to('cuda')
                nrm_score2 = feature['nrm_score2'].to('cuda')
                
                comb, _, _ = dynamic_weighted_metric(
                    clipiqa, nrm_score2, 
                    base_cos=base_cos, base_norm=base_norm, alpha=alpha
                )
                pred_score = torch.mean(comb)
                prs.append(pred_score.squeeze().cpu().numpy())
                current_gts.append(feature['gt'])
            
            plcc, srcc, rmse = correlation_evaluation(prs, current_gts, is_plot=False, plot_path="")
            
            results_summary.append({
                'dataset': dataset_name,
                'base_cos': base_cos,
                'base_norm': base_norm,
                'alpha': alpha,
                'srcc': srcc,
                'plcc': plcc,
                'rmse': rmse
            })
            
            log_and_print(base_logger, 
                msg=f"{dataset_name}: base_cos={base_cos}, base_norm={base_norm}, alpha={alpha} -> SRCC:{srcc:.4f} PLCC:{plcc:.4f} RMSE:{rmse:.4f}")
    
    # 保存详细结果并分析最优参数
    df_summary = pd.DataFrame(results_summary)
    df_summary.to_csv(checkpoint_dir + '/base_constant_ablation_detailed.csv', index=False)
    
    # 找出每个数据集的最优参数
    for dataset in dataset_config.keys():
        dataset_results = df_summary[df_summary['dataset'] == dataset]
        best_srcc = dataset_results.loc[dataset_results['srcc'].idxmax()]
        log_and_print(base_logger, 
            msg=f"{dataset} 最优参数: base_cos={best_srcc['base_cos']}, base_norm={best_srcc['base_norm']}, alpha={best_srcc['alpha']}, SRCC={best_srcc['srcc']:.4f},PLCC={best_srcc['plcc']:.4f},RMSE={best_srcc['rmse']:.4f}")
    
    return df_summary



checkpoint_dir = 'rebuttal/CGI_SCI'
score_type = 'mos'

os.makedirs(checkpoint_dir,exist_ok = True)
base_logger = get_logger(os.path.join(checkpoint_dir,'train_test.log'), 'log')


if __name__ == '__main__':
    image_paths_all = [
        # "/home/zhicheng/datasets/IQA/CCT/", 
        # "/home/zhicheng/datasets/IQA/CCT/",
        # "/home/zhicheng/datasets/IQA/CCT/",
        "/home/zhicheng/datasets/IQA/SCID/DistortedSCIs/",
    ]
    json_prefix = "./jsons/"
    dataset_config = {
        # "CCT_CGI": [json_prefix + "CCT_CGI.json"],
        # "CCT_SCI": [json_prefix + "CCT_SCI.json"],
        # "CCT_NSI": [json_prefix + "CCT_NSI.json"],
         "SCID": [json_prefix + "SCID.json"],
    }

    # run_base_constant_ablation(dataset_config, image_paths_all)

    for idx, (dataset_name, json_paths) in enumerate(dataset_config.items()):
        image_paths = [image_paths_all[idx]] 
        # import pdb;pdb.set_trace()
        main(image_paths, json_paths, dataset_name)

