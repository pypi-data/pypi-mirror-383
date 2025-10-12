import os
import torch
import functools
import pandas as pd
from PIL import Image, ImageFile
from torch.utils.data import Dataset
import torch.nn.functional as F

IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif']

ImageFile.LOAD_TRUNCATED_IMAGES = True
def has_file_allowed_extension(filename, extensions):
    """Checks if a file is an allowed extension.
    Args:
        filename (string): path to a file
        extensions (iterable of strings): extensions to consider (lowercase)
    Returns:
        bool: True if the filename ends with one of given extensions
    """
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in extensions)


def image_loader(image_name):
    #print(image_name)
    if has_file_allowed_extension(image_name, IMG_EXTENSIONS):
        I = Image.open(image_name)
    else:
        print(image_name)
    return I.convert('RGB')


def get_default_img_loader():
    return functools.partial(image_loader)

from torchvision.transforms import Compose as torchcompose
from torchvision.transforms import Resize, CenterCrop, ToTensor, Normalize
def nrm_process(img, size=224):
    process = torchcompose([
        # Resize(size),
        # Resize((size, size), interpolation=BICUBIC),
        # CenterCrop(size),
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])

    return process(img)
def ref_imgnrm(img, size=224):
    process = torchcompose([
        # Resize(size),
        # Resize((size, size), interpolation=BICUBIC),
        CenterCrop(size),
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])

    return process(img)

# AIGC数据集，用于训练AIGC模型，数据只有图像，csv文件只有对应图像名称、MOS、对图像的一段文本描述
class AIGCDataset(Dataset):
    def __init__(self, csv_file,
                 img_dir,
                 preprocess,
                 num_patch,
                 test,
                 blind = False,
                 get_loader=get_default_img_loader):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            img_dir (string): Directory of the images.
            transform (callable, optional): transform to be applied on a sample.
        """
        # # 读取xlsx文件
        # self.data = pd.read_excel(csv_file, header=None)
        # # Print and remove the first row
        # print(self.data.iloc[0])
        # self.data = self.data.iloc[1:]

        self.data = pd.read_csv(csv_file, sep=',', header=None)
        self.data = self.data.iloc[1:] #去掉第一行
        print('%d csv data successfully loaded!' % self.__len__())

        self.img_dir = img_dir
        self.loader = get_loader()
        self.preprocess = preprocess
        self.num_patch = num_patch
        self.test = test
        self.blind = blind
        self.in_memory = False

    def __getitem__(self, index):
        image_name = self.data.iloc[index, 0]   
        image_path = os.path.join(self.img_dir, image_name)
        I = self.loader(image_path)
        I = nrm_process(I).unsqueeze(0)

        unfold = nn.Unfold(kernel_size=(224, 224), stride=128)
        X_sub = unfold(I).view(1, 3, 224, 224, -1)[0]
        # patches = X_sub.permute(3,0,1,2).cuda()
        patches = X_sub.permute(3,0,1,2)

        mos = float(self.data.iloc[index, 2])
        prompt = self.data.iloc[index, 1]

        model_name = image_name.split('_')
        model_name = model_name[0]        
        prompt_name = model_name + ' ' + prompt # 用空格拼接模型名字和prompt

        sample = {'I': patches, 'mos': mos,'prompt':prompt, 'prompt_name':prompt_name, 'image_name':image_name}
        return sample

    def __len__(self):
        return len(self.data.index)

import torch.nn as nn
class AIGCDataset_3k(Dataset):
    def __init__(self, csv_file,
                 img_dir,
                 preprocess,
                 num_patch,
                 test,
                 blind = False,
                 get_loader=get_default_img_loader):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            img_dir (string): Directory of the images.
            transform (callable, optional): transform to be applied on a sample.
        """
        self.data = pd.read_csv(csv_file, sep=',', header=None)
        self.data = self.data.iloc[1:]
        print('%d csv data successfully loaded!' % self.__len__())
        self.img_dir = img_dir
        self.loader = get_loader()
        self.preprocess = preprocess
        self.num_patch = num_patch
        self.test = test
        self.blind = blind
        self.in_memory = False

    def __getitem__(self, index):
        image_name = self.data.iloc[index, 0]   
        image_path = os.path.join(self.img_dir, image_name)
        I = self.loader(image_path)
        I = nrm_process(I).unsqueeze(0)

        unfold = nn.Unfold(kernel_size=(224, 224), stride=128)
        X_sub = unfold(I).view(1, 3, 224, 224, -1)[0]
        # patches = X_sub.permute(3,0,1,2).cuda()
        patches = X_sub.permute(3,0,1,2)

        mos = float(self.data.iloc[index, 5]) # 取Normalized MOS for perception subjective score.
        align = float(self.data.iloc[index, 7]) # 取align_mos
        
        prompt = self.data.iloc[index, 1]

        model_name = image_name.split('_')
        model_name = model_name[0]        
        prompt_name = model_name + ' ' + prompt

        mos_std = float(self.data.iloc[index, 6])
        align_std = float(self.data.iloc[index, 8])
        sample = {'I': patches, 'mos': mos,'prompt':prompt, 'prompt_name':prompt_name, 'image_name':image_name,
                  'align' : align, 'mos_std':mos_std, 'align_std':align_std}
        return sample

    def __len__(self):
        return len(self.data.index)


class AIGCIQA2023Dataset(Dataset):
    def __init__(self, csv_file,
                 img_dir,
                 preprocess,
                 num_patch,
                 test,
                 blind = False,
                 get_loader=get_default_img_loader):

        self.data = pd.read_csv(csv_file, sep=',', header=None)
        self.data = self.data.iloc[1:]
        print('%d csv data successfully loaded!' % self.__len__())

        self.img_dir = img_dir
        self.loader = get_loader()
        self.preprocess = preprocess
        self.num_patch = num_patch
        self.test = test
        # self.blind = blind
        self.in_memory = False

    def __getitem__(self, index):
        image_name = self.data.iloc[index, 1]   # 000-1.png
        image_path = os.path.join(self.img_dir, self.data.iloc[index, 0], image_name)
        I = self.loader(image_path)
        I = nrm_process(I).unsqueeze(0)

        unfold = nn.Unfold(kernel_size=(224, 224), stride=128)
        X_sub = unfold(I).view(1, 3, 224, 224, -1)[0]
        # patches = X_sub.permute(3,0,1,2).cuda()
        patches = X_sub.permute(3,0,1,2)

        mos = float(self.data.iloc[index, 2])
        authenticity = float(self.data.iloc[index, 3])
        corr = float(self.data.iloc[index, 4])
        prompt = self.data.iloc[index, 5]

        model_name =  self.data.iloc[index, 0] + image_name
        prompt_name = model_name + ' ' + prompt

        sample = {'I': patches, 'mos': mos, 'authenticity':authenticity, 'corr': corr,
                  'prompt':prompt, 'prompt_name':prompt_name, 'image_name':model_name}   # 对于AIGC2023返回的image_name实际为模型名
        return sample

    def __len__(self):
        return len(self.data.index)
    

#-------------------------------------------------------------------------------
from torch.utils.data import DataLoader
def set_dataset_aigc(csv_file, bs, data_set, num_workers, preprocess, num_patch, test, blind=False):

    data = AIGCDataset(
        csv_file=csv_file,
        img_dir=data_set,
        num_patch=num_patch,
        test=test,
        preprocess=preprocess,
        blind=blind)

    if test:
        shuffle = False
    else:
        shuffle = True

    loader = DataLoader(data, batch_size=bs, shuffle=shuffle, pin_memory=True, num_workers=num_workers)

    return loader

def set_dataset_aigc_3k(csv_file, bs, data_set, num_workers, preprocess, num_patch, test, blind=False):

    data = AIGCDataset_3k(
        csv_file=csv_file,
        img_dir=data_set,
        num_patch=num_patch,
        test=test,
        preprocess=preprocess,
        blind=blind)

    if test:
        shuffle = False
    else:
        shuffle = True

    loader = DataLoader(data, batch_size=bs, shuffle=shuffle, pin_memory=True, num_workers=num_workers)

    return loader


def set_dataset_aigc_2023(csv_file, bs, data_set, num_workers, preprocess, num_patch, test, blind=False):

    data = AIGCIQA2023Dataset(
        csv_file=csv_file,
        img_dir=data_set,
        num_patch=num_patch,
        test=test,
        preprocess=preprocess,
        blind=blind)

    if test:
        shuffle = False
    else:
        shuffle = True

    loader = DataLoader(data, batch_size=bs, shuffle=shuffle, pin_memory=True, num_workers=num_workers)

    return loader