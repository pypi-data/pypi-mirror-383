# coding: utf-8
import sys
import os
from PIL import Image, ImageFilter
import cv2
import numpy as np
from tqdm import tqdm


def map_strength_to_parameters(strength):
    if strength < 0 or strength > 10:
        raise ValueError("强度值应在0到10之间")

    # 非线性映射，使用指数函数控制强度
    min_sigma = 0.00001  # 极低时接近不处理
    max_sigma = 25.0  # 高强度时的最大滤波参数

    sigma = min_sigma + (max_sigma - min_sigma) * (strength / 10.0)
    return sigma

def apply_bilateral_filter(image, strength):
    image_cv = np.array(image)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)
    sigma = map_strength_to_parameters(strength)
    filtered_image_cv = cv2.bilateralFilter(image_cv, d=5, sigmaColor=sigma, sigmaSpace=sigma)
    filtered_image_cv = cv2.cvtColor(filtered_image_cv, cv2.COLOR_BGR2RGB)
    return Image.fromarray(filtered_image_cv)

def reduce_quantization_noise(image, strength=10):
    image_cv = np.array(image)
    image_lab = cv2.cvtColor(image_cv, cv2.COLOR_RGB2Lab)
    L, a, b = cv2.split(image_lab)
    L_filtered = cv2.bilateralFilter(L, d=9, sigmaColor=strength, sigmaSpace=strength)
    image_filtered = cv2.merge((L_filtered, a, b))
    image_rgb = cv2.cvtColor(image_filtered, cv2.COLOR_Lab2RGB)
    return Image.fromarray(image_rgb)

def apply_interframe_median_filter(prev_frame, curr_frame, next_frame, threshold):
    prev_frame_np = np.array(prev_frame)
    curr_frame_np = np.array(curr_frame)
    next_frame_np = np.array(next_frame)
    mask = (np.abs(curr_frame_np - prev_frame_np) < threshold) & (prev_frame_np == next_frame_np)
    curr_frame_np[mask] = prev_frame_np[mask]
    return Image.fromarray(curr_frame_np)

def apply_temporal_denoise(display_frame, curr_frame, threshold):
    display_frame_np = np.array(display_frame)
    curr_frame_np = np.array(curr_frame)
    mask = np.abs(curr_frame_np - display_frame_np) < threshold
    curr_frame_np[mask] = display_frame_np[mask]
    return Image.fromarray(curr_frame_np)

def crop_and_resize(image, crop_size=None, scale_size=None):
    if crop_size:
        width, height = image.size
        crop_width, crop_height = crop_size
        left = (width - crop_width) / 2
        top = (height - crop_height) / 2
        right = (width + crop_width) / 2
        bottom = (height + crop_height) / 2
        image = image.crop((left, top, right, bottom))

    if scale_size:
        image = image.resize(scale_size, Image.BILINEAR)

    return image

def extract_frames(gif_path, output_dir, crop_size=None, scale_size=None,
        bilateral_strength=0, median_strength=0, interframe_threshold=0, temporal_threshold=0):
    gif = Image.open(gif_path)

    gif_info = {}
    gif_info["frames"] = gif.n_frames
    gif_info["duration"] = gif.info["duration"] # 获取第一帧的持续时间

    width, height = gif.size
    if crop_size is not None:
        width, height = crop_size
    if scale_size is not None:
        width, height = scale_size
    gif_info["width"], gif_info["height"] = width, height

    if gif_info["width"] % 4 != 0 or gif_info["height"] % 4 != 0:
        print(f"img width {gif_info['width']} or height {gif_info['height']} is incorrect, must be aligned to 4")
        sys.exit(1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frames = []
    display_frame = None
    frame_count = 0
    try:
        while True:
            frame = gif.convert("RGB")

            # 裁剪和缩放处理
            frame = crop_and_resize(frame, crop_size=crop_size, scale_size=scale_size)

            # 双边滤波处理
            if bilateral_strength > 0:
                frame = apply_bilateral_filter(frame, bilateral_strength)

            # 空域中值滤波处理
            if median_strength > 0:
                frame = frame.filter(ImageFilter.MedianFilter(size=int(median_strength * 2 + 1)))

            frames.append(frame)
            frame_count += 1
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass

    # 时域中值滤波
    if len(frames) > 1 and interframe_threshold > 0:
        prev_frame = frames[-1]
        for frame_index in tqdm(range(len(frames)), desc="Applying interframe median filter"):
            next_frame = frames[(frame_index + 1) % len(frames)]
            frames[frame_index] = apply_interframe_median_filter(prev_frame, frames[frame_index], next_frame, interframe_threshold)
            prev_frame = frames[frame_index]

    # 时域不更新算法
    if temporal_threshold > 0:
        for frame_index in tqdm(range(len(frames)), desc="Applying temporal denoise"):
            if display_frame is not None:
                frames[frame_index] = apply_temporal_denoise(display_frame, frames[frame_index], temporal_threshold)
            display_frame = frames[frame_index]

    for frame_index, frame in tqdm(enumerate(frames), total=frame_count, desc="Saving frames"):
        png_filename = f"{os.path.splitext(os.path.basename(gif_path))[0]}_{frame_index}.png"
        png_path = os.path.join(output_dir, png_filename)
        frame.save(png_path, "PNG")

    return gif_info

