import os
import cv2
import numpy as np
import torch
import torchvision
from PIL import Image
from tqdm import tqdm


model = torch.load('inference_model/ophtalmic_segmentation.pb', weights_only=False)
model.eval()
model.to('cuda')
get_tensor = torchvision.transforms.ToTensor()


def to_tensor(
    x: np.ndarray,
) -> np.ndarray:
    return x.transpose([2, 0, 1]).astype('float32')


def sem_processing(*args):
    (source_image,) = args
    return inference(source_image=source_image.copy())


def plt2arr(fig, draw=True):
    if draw:
        fig.canvas.draw()
    rgba_buf = fig.canvas.buffer_rgba()
    (w, h) = fig.canvas.get_width_height()
    rgb_arr = np.frombuffer(rgba_buf, dtype=np.uint8).reshape((h, w, 3))
    return rgb_arr


def get_temp_mask(
    mask: np.ndarray,
) -> np.ndarray:
    mask = cv2.GaussianBlur(mask, (21, 21), 11)
    color_mask = cv2.applyColorMap(np.uint8(mask * 255), cv2.COLORMAP_JET)
    return color_mask


def inference(
        source_image: Image.Image,
):
    w, h = source_image.size
    image = np.array(source_image.copy())
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (1024, 1024))
    image = to_tensor(np.array(image))
    y_hat = model(torch.Tensor([image]).to('cuda'))
    mask_pred = y_hat.sigmoid()
    masks_source = (mask_pred > 0.02).float()
    masks_source = masks_source.permute(0, 2, 3, 1)
    masks_source = masks_source.squeeze().cpu().numpy()
    temp_card = get_temp_mask(
        mask=np.sum(masks_source[:, :, :], axis=2)
    )
    mask = np.array(source_image.convert('L'))
    mask[mask > 15] = 95
    mask = Image.fromarray(mask)
    temp_card = Image.fromarray(cv2.resize(cv2.cvtColor(temp_card, cv2.COLOR_RGB2BGR), (w, h)))
    source_image.paste(temp_card, (0, 0), mask=mask)

    return source_image
