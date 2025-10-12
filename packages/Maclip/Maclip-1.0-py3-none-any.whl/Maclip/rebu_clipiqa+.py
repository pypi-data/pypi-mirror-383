
import torch
import torch.nn as nn

from pyiqa.archs.arch_util import load_file_from_url, load_pretrained_network

import clip
from clip_model import load
from pyiqa.archs.arch_util import get_url_from_name

from torch import randint
import os
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


default_model_urls = {
    'clipiqa+': get_url_from_name('CLIP-IQA+_learned_prompts-603f3273.pth'),
    'clipiqa+_rn50_512': get_url_from_name('CLIPIQA+_RN50_512-89f5d940.pth'),
    'clipiqa+_vitL14_512': get_url_from_name('CLIPIQA+_ViTL14_512-e66488f2.pth'),
}

OPENAI_CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
OPENAI_CLIP_STD = (0.26862954, 0.26130258, 0.27577711)


class PromptLearner(nn.Module):
    """
    PromptLearner class for learning prompts for CLIP-IQA.

    Disclaimer:
        This implementation follows exactly the official codes in: https://github.com/IceClear/CLIP-IQA. 
        We have no idea why some tricks are implemented like this, which include:
            1. Using n_ctx prefix characters "X"
            2. Appending extra "." at the end
            3. Insert the original text embedding at the middle
    """

    def __init__(self, clip_model, n_ctx=16) -> None:
        """
        Initialize the PromptLearner.

        Args:
            clip_model (nn.Module): The CLIP model.
            n_ctx (int): Number of context tokens. Default is 16.
        """
        super().__init__()

        # For the following codes about prompts, we follow the official codes to get the same results
        prompt_prefix = " ".join(["X"] * n_ctx) + ' '
        init_prompts = [prompt_prefix + 'Good photo..', prompt_prefix + 'Bad photo..']
        with torch.no_grad():
            txt_token = clip.tokenize(init_prompts)
            self.tokenized_prompts = txt_token
            init_embedding = clip_model.token_embedding(txt_token)

        init_ctx = init_embedding[:, 1: 1 + n_ctx]
        self.ctx = nn.Parameter(init_ctx)

        self.n_ctx = n_ctx
        self.n_cls = len(init_prompts)
        self.name_lens = [3, 3]  # hard coded length, which does not include the extra "." at the end

        self.register_buffer("token_prefix", init_embedding[:, :1, :])  # SOS
        self.register_buffer("token_suffix", init_embedding[:, 1 + n_ctx:, :])  # CLS, EOS

    def get_prompts_with_middle_class(self):
        """
        Get prompts with the original text embedding inserted in the middle.

        Returns:
            torch.Tensor: The generated prompts.
        """
        ctx = self.ctx.to(self.token_prefix)
        if ctx.dim() == 2:
            ctx = ctx.unsqueeze(0).expand(self.n_cls, -1, -1)

        half_n_ctx = self.n_ctx // 2
        prompts = []
        for i in range(self.n_cls):
            name_len = self.name_lens[i]
            prefix_i = self.token_prefix[i: i + 1, :, :]
            class_i = self.token_suffix[i: i + 1, :name_len, :]
            suffix_i = self.token_suffix[i: i + 1, name_len:, :]
            ctx_i_half1 = ctx[i: i + 1, :half_n_ctx, :]
            ctx_i_half2 = ctx[i: i + 1, half_n_ctx:, :]
            prompt = torch.cat(
                [
                    prefix_i,     # (1, 1, dim)
                    ctx_i_half1,  # (1, n_ctx//2, dim)
                    class_i,      # (1, name_len, dim)
                    ctx_i_half2,  # (1, n_ctx//2, dim)
                    suffix_i,     # (1, *, dim)
                ],
                dim=1,
            )
            prompts.append(prompt)
        prompts = torch.cat(prompts, dim=0)
        return prompts

    def forward(self, clip_model):
        """
        Forward pass for the PromptLearner.

        Args:
            clip_model (nn.Module): The CLIP model.

        Returns:
            torch.Tensor: The output features.
        """
        prompts = self.get_prompts_with_middle_class()
        x = prompts + clip_model.positional_embedding.type(clip_model.dtype)
        x = x.permute(1, 0, 2)  # NLD -> LND
        x = clip_model.transformer(x)
        x = x.permute(1, 0, 2)  # LND -> NLD
        x = clip_model.ln_final(x).type(clip_model.dtype)

        # x.shape = [batch_size, n_ctx, transformer.width]
        # take features from the eot embedding (eot_token is the highest number in each sequence)
        x = x[torch.arange(x.shape[0]), self.tokenized_prompts.argmax(dim=-1)] @ clip_model.text_projection

        return x

class CLIPIQA(nn.Module):
    """
    CLIPIQA metric class.

    Args:
        model_type (str): The type of the model. Default is 'clipiqa'.
        backbone (str): The backbone model. Default is 'RN50'.
        pretrained (bool): Whether to load pretrained weights. Default is True.
        pos_embedding (bool): Whether to use positional embedding. Default is False.
    """

    def __init__(self,
                 model_type='clipiqa',
                 backbone='RN50',
                 pretrained=True,
                 pos_embedding=False) -> None:
        super().__init__()

        self.clip_model = [load(backbone, 'cpu')]  # avoid saving clip weights
        # Different from original paper, we assemble multiple prompts to improve performance
        self.prompt_pairs = clip.tokenize([
            'Good image', 'bad image',
            'Sharp image', 'blurry image',
            'sharp edges', 'blurry edges',
            'High resolution image', 'low resolution image',
            'Noise-free image', 'noisy image',
        ])

        self.model_type = model_type
        self.pos_embedding = pos_embedding
        if 'clipiqa+' in model_type:
            self.prompt_learner = PromptLearner(self.clip_model[0])

        self.default_mean = torch.Tensor(OPENAI_CLIP_MEAN).view(1, 3, 1, 1)
        self.default_std = torch.Tensor(OPENAI_CLIP_STD).view(1, 3, 1, 1)

        for p in self.clip_model[0].parameters():
            p.requires_grad = False
        
        if pretrained and 'clipiqa+' in model_type:
            if model_type == 'clipiqa+' and backbone == 'RN50':
                self.prompt_learner.ctx.data = torch.load(load_file_from_url(default_model_urls['clipiqa+']), weights_only=False)
            elif model_type in default_model_urls.keys():
                load_pretrained_network(self, default_model_urls[model_type], True, 'params')
            else:
                raise ValueError(f'No pretrained model for {model_type}')
    
    def forward(self, x):
        """
        Forward pass for the CLIPIQA model.

        Args:
            x (torch.Tensor): Input tensor with shape (N, C, H, W).

        Returns:
            torch.Tensor: The output probabilities.
        """
        # preprocess image
        x = (x - self.default_mean.to(x)) / self.default_std.to(x)
        clip_model = self.clip_model[0].to(x)

        if self.model_type == 'clipiqa':
            prompts = self.prompt_pairs.to(x.device)
            logits_per_image, logits_per_text, nrm_score = clip_model(x, prompts, pos_embedding=self.pos_embedding)
        elif 'clipiqa+' in self.model_type:
            learned_prompt_feature = self.prompt_learner(clip_model)
            # logits_per_image, logits_per_text = clip_model(
            #     x, None, text_features=learned_prompt_feature, pos_embedding=self.pos_embedding)
            logits_per_image, logits_per_text, nrm_score = clip_model(x, prompts, pos_embedding=self.pos_embedding)

        probs = logits_per_image.reshape(logits_per_image.shape[0], -1, 2).softmax(dim=-1)

        return probs[..., 0].mean(dim=1, keepdim=True), nrm_score

def nrm_process(img, size=224):
    process = torchcompose([
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])
    return process(img)

from torchvision.transforms.functional import InterpolationMode
def agiqa1k_nrm_process(img, size=224):
    process = torchcompose([
        # Resize(size),
        Resize((size, size), interpolation=InterpolationMode.BICUBIC),
        # CenterCrop(size),
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])
    return process(img)

def perceptual_box_cox_transform3(x, lam=0.5, alpha=0.2, epsilon=1e-6):
    # 3. Perceptual transformation
    # x = (x - x.mean(dim=1, keepdim=True)) / (x.std(dim=1, keepdim=True) + epsilon)  # [B, D]
    # x = torch.abs(x) # [B, D]
    x = (x) / (x.std(dim=1, keepdim=True) + epsilon)  # [B, D]
    # box-cox
    transformed = ((x + 1) ** lam - 1) / lam

    return transformed

def dynamic_weighted_metric(cos, norm, beta1=1.0, beta2=0.6, alpha=1.0):
    d = cos - norm # 差值
    # 生成权重参数：d越大，cos权重越高；d越小，norm权重越高
    # d = torch.sigmoid(d)
    cos_param = beta1 + alpha * d
    norm_param = beta2 - alpha * d
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

    iqa_metric = pyiqa.create_metric('clipiqa').cuda()
    iqamodel = CLIPIQA().cuda()
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
                clipiqa, image_features_org = iqamodel(X_sub) 
                
                # box-cox1
                image_features_org_abs = torch.abs(image_features_org)
                nrm_score = image_features_org_abs.mean(dim=-1)
                image_features_org_abs_box = perceptual_box_cox_transform3(image_features_org_abs, lam=0.5)
                nrm_score2 = image_features_org_abs_box.mean(dim=-1)
                comb, w1, w2 = dynamic_weighted_metric(clipiqa.squeeze(1), nrm_score2) 

                predq0 = torch.mean(nrm_score2)
                predq1 = torch.mean(nrm_score)
                predq2, _ = iqa_metric(raw_image_ini)
                predq3 = torch.mean(clipiqa)
                predq4 = torch.mean(comb)
               
                prs0.append(predq0.squeeze().cpu().numpy()) 
                prs1.append(predq1.squeeze().cpu().numpy())
                prs2.append(predq2.squeeze().cpu().numpy())
                prs3.append(predq3.squeeze().cpu().numpy())
                prs4.append(predq4.squeeze().cpu().numpy())
                w1_list.append(w1.mean().cpu().numpy())
                w2_list.append(w2.mean().cpu().numpy())

        log_and_print(base_logger, f'dataset: {input_json}')   
        
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
        log_and_print(base_logger, f'dataset: {input_json}')   
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


checkpoint_dir = 'rebutal/clipiqa_plus'
score_type = 'mos'

os.makedirs(checkpoint_dir,exist_ok = True)
base_logger = get_logger(os.path.join(checkpoint_dir,'train_test.log'), 'log')


if __name__ == '__main__':
    image_paths_all = [
        # "/home/cbl/IQA/datasets/CVID/",
        # "/home/cbl/IQA/datasets/live/", 

        # "/home/cbl/IQA/datasets/AGIQA-3K/",
        "/home/cbl/IQA/datasets/AGIQA-1K/file/",
        # '/home/cbl/IQA/datasets//CSIQ/dst_imgs_all/',
        # '/home/cbl/IQA/datasets//TID2013/distorted_images/',
        # "/home/cbl/IQA/datasets//CID2013/",

        # "/home/cbl/IQA/datasets//SIQAD/DistortedImages/",
        # "/home/cbl/IQA/datasets//kadid10k/images/",
        # "/home/cbl/IQA/datasets/koniq-10k/1024x768/",
        # "/home/cbl/IQA/datasets/SPAQ/SPAQ/Dataset/TestImage/",
        # '/data/cbl/IQA/datasets/databaserelease2/'
    ]
    json_prefix = "./jsons/"
    dataset_config = {
        # "CVID": [json_prefix + "cvid.json"],
        # "livec": [json_prefix + "livec.json"],

        # "AGIQA-3k": [json_prefix + "AGIQA-3k.json"],
        "AGIQA-1k": [json_prefix + "AGIQA-1k.json"],
        # "CSIQ": [json_prefix + "csiq.json"],
        # "TID2013": [json_prefix + "tid2013.json"],
        # "CID2013": [json_prefix + "cid2013.json"],

        # "SIQAD": [json_prefix + "SIQAD.json"],
        # "kadid": [json_prefix + "kadid.json"],
        # "koniq": [json_prefix + "koniq.json"],
        # "SPAQ": [json_prefix + "spaq.json"],
        # 'LIVE':[json_prefix+ "live.json"],
    }

    for idx, (dataset_name, json_paths) in enumerate(dataset_config.items()):
        image_paths = [image_paths_all[idx]] 
        # import pdb;pdb.set_trace()
        main(image_paths, json_paths, dataset_name)


