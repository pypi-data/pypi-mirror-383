from torch.utils.data import DataLoader
from ImageDataset import  AIGCDataset,AIGCDataset_3k,AIGCIQA2023Dataset

from torchvision.transforms import Compose, ToTensor, Normalize, RandomHorizontalFlip
from torchvision import transforms

from PIL import Image
import logging

try:
    from torchvision.transforms import InterpolationMode
    BICUBIC = InterpolationMode.BICUBIC
except ImportError:
    BICUBIC = Image.BICUBIC


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



class AdaptiveResize(object):
    """Resize the input PIL Image to the given size adaptively.

    Args:
        size (sequence or int): Desired output size. If size is a sequence like
            (h, w), output size will be matched to this. If size is an int,
            smaller edge of the image will be matched to this number.
            i.e, if height > width, then image will be rescaled to
            (size * height / width, size)
        interpolation (int, optional): Desired interpolation. Default is
            ``PIL.Image.BILINEAR``
    """

    def __init__(self, size, interpolation=InterpolationMode.BILINEAR, image_size=None):
        assert isinstance(size, int)
        self.size = size
        self.interpolation = interpolation #插值方式，默认为双线性插值
        if image_size is not None:
            self.image_size = image_size
        else:
            self.image_size = None

    #调用一个对象时即使用圆括号时，Python会自动查找并执行该对象的__call__方法。
    def __call__(self, img):
        """
        Args:
            img (PIL Image): Image to be scaled.

        Returns:
            PIL Image: Rescaled image.
        """
        h, w = img.size

        if self.image_size is not None:
            if h < self.image_size or w < self.image_size:
                return transforms.Resize(self.image_size, self.interpolation)(img)

        if h < self.size or w < self.size:
            return transforms.Resize(self.size, self.interpolation)(img)
        else:
            return img


def _convert_image_to_rgb(image):
    return image.convert("RGB")

def _preprocess2():
    return Compose([
        _convert_image_to_rgb,
        AdaptiveResize(512), #调整图像大小到512 
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])

def _preprocess3():
    return Compose([
        _convert_image_to_rgb,
        AdaptiveResize(512),
        RandomHorizontalFlip(),
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])

def _preprocess4():
    return Compose([
        _convert_image_to_rgb,
        AdaptiveResize(768),
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])

def _preprocess5():
    return Compose([
        _convert_image_to_rgb,
        AdaptiveResize(768),
        RandomHorizontalFlip(),
        ToTensor(),
        Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
    ])

def convert_models_to_fp32(model):
    for p in model.parameters():
        p.data = p.data.float()
        if p.grad is not None:
            p.grad.data = p.grad.data.float()


def get_logger(filepath, log_info):
    logger = logging.getLogger(filepath)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(filepath)
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)
    logger.info('-' * 30 + log_info + '-' * 30)
    return logger


def log_and_print(logger, msg):
    logger.info(msg)
    print(msg)  

import torch
import torch.nn.functional as F

def extract_patches(
    image: torch.Tensor,
    kernel_h: int = 224,
    kernel_w: int = 224,
    step: int = None,
    num_patch: int = None,
    test: bool = False
) -> torch.Tensor:
    """
    将图像分割成多个图像块（patches）。

    Args:
        image (torch.Tensor): 输入图像张量，形状为 (C, H, W)。
        kernel_h (int): 图像块的高度。默认为 224。
        kernel_w (int): 图像块的宽度。默认为 224。
        step (int): 步长。默认为 None，表示根据图像大小动态确定。
        num_patch (int): 需要提取的图像块数量。默认为 None。
        test (bool): 是否为测试模式。默认为 False。

    Returns:
        torch.Tensor: 提取的图像块张量，形状为 (num_patches, C, kernel_h, kernel_w)。
    """
    # 增加批次维度
    image = image.unsqueeze(0)
    n_channels = image.size(1)

    # 确定步长
    if step is None:
        if (image.size(2) >= 1024) or (image.size(3) >= 1024):
            step = 48
        else:
            step = 32

    # 使用 unfold 方法将图像分割为小块
    patches = image.unfold(2, kernel_h, step).unfold(3, kernel_w, step)
    patches = patches.permute(2, 3, 0, 1, 4, 5).reshape(-1, n_channels, kernel_h, kernel_w)

    # 根据测试模式选择图像块
    if test and (num_patch is not None):
        sel_step = patches.size(0) // num_patch
        sel = torch.zeros(num_patch)
        for i in range(num_patch):
            sel[i] = sel_step * i
        sel = sel.long()
    else:
        if num_patch is not None:
            sel = torch.randint(low=0, high=patches.size(0), size=(num_patch,))
            sel = sel.long()
        else:
            sel = torch.arange(patches.size(0))
    patches = patches[sel, ...]

    return patches