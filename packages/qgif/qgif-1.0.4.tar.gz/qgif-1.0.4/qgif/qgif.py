# coding: utf-8
import os
import sys
import signal
import ctypes
from ctypes import CFUNCTYPE, c_int
import numpy as np
import time
from PIL import Image
from tqdm import tqdm
import tempfile
import platform

from qgif.gif2png import extract_frames
from qgif.gen_lvgl_file import gen_lvgl_file

def ensure_console():
    try:
        if os.name == 'nt':
            if sys.stdout is None:
                ctypes.windll.kernel32.AllocConsole()
                sys.stdout = open('CONOUT$', 'w')
                sys.stderr = open('CONOUT$', 'w')
    except Exception:
        pass
ensure_console()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, 'frozen'): # pyinstaller
        base_path = sys._MEIPASS
    else:
        base_path = '.'
    return os.path.join(base_path, relative_path)

if platform.system() == 'Windows':
    qgif_lib_path = os.path.join(os.path.dirname(__file__), resource_path("qgif_C\\libqgif.dll"))
else:
    qgif_lib_path = os.path.join(os.path.dirname(__file__), resource_path("qgif_C/libqgif.so"))

qgif_lib = ctypes.CDLL(qgif_lib_path)

exit_flag = False
def signal_handler(sig, frame):
    global exit_flag
    exit_flag = True
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

def get_filename_without_extension(file_path):
    file_name_with_extension = os.path.basename(file_path)
    file_name, _ = os.path.splitext(file_name_with_extension)
    return file_name

def replace_extension(file_path, extension):
    base = os.path.splitext(file_path)[0]
    return base + extension

def get_compress_type_value(compress_type):
    # 0: gx64
    # 1: gx64a
    # 2: gx96
    # 3: gx96a
    compress_types = {
        "gx64" : 0,
        "gx96" : 2,
    }
    return compress_types[compress_type]

"""
void compress_video(const char *image_path, const char *output_path, uint8_t compress_type, uint8_t frame_rate, int (*progress_callback)(int));
"""
qgif_lib.compress_video.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint8, ctypes.c_uint8, CFUNCTYPE(c_int, c_int)]
qgif_lib.compress_video.restype = None


"""
void decode_qgif(const char *input_path, const char *output_path, unsigned char color_depth, int *width, int *height);
"""
qgif_lib.decode_qgif.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint8,
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
qgif_lib.decode_qgif.restype = None


def convert_gif_to_qgif(input_path, output_path, qgif_format, need_output_lvgl, frame_rate=0,\
        crop_size=None, scale_size=None, bilateral_strength=0, median_strength=0,\
        interframe_threshold=0, temporal_threshold=0):
    with tempfile.TemporaryDirectory() as png_path:
        input_name = get_filename_without_extension(input_path)
        input_png_path = os.path.join(png_path, f"{input_name}_X.png")

        # gif to png
        print("Convert gif to png ...")
        gif_info = extract_frames(input_path, png_path, crop_size, scale_size, bilateral_strength, median_strength,
                interframe_threshold, temporal_threshold)
        print("Convert gif to png finish.")

        # png to qgif
        print("Convert png to qgif ...")
        progress_bar = tqdm(total=gif_info["frames"])

        if gif_info["duration"] == 0:
            duration = 100
        else:
            duration = gif_info["duration"]
        if frame_rate < 1 or frame_rate > 64:
            frame_rate = int(1000. / duration)

        global exit_flag
        def progress_callback(frame_index):
            progress_bar.n = frame_index
            progress_bar.refresh()
            if exit_flag:
                return True
            else:
                return False

        PROGRESS_CALLBACK = CFUNCTYPE(c_int, c_int)
        c_progress_callback = PROGRESS_CALLBACK(progress_callback)

        compress_type_value = get_compress_type_value(qgif_format)
        qgif_lib.compress_video(input_png_path.encode("utf-8"), output_path.encode("utf-8"), compress_type_value,
                frame_rate, c_progress_callback)
        progress_bar.close()
        if exit_flag:
            sys.exit(1)
        print(f"Convert png to qgif {output_path} finish.")

        if need_output_lvgl:
            print("Generate LVGL C file ...")
            bin_path = output_path
            lvgl_path = replace_extension(bin_path, ".c")
            gen_lvgl_file(bin_path, lvgl_path, gif_info["width"], gif_info["height"])
            print(f"Generate LVGL C file {lvgl_path} finish.")

        print(f"============================")
        print(f"QGIF {output_path}:")
        print(f"frames: {gif_info['frames']}")
        print(f"framerate: {frame_rate}")
        print(f"img width: {gif_info['width']}, height: {gif_info['height']}")
        print(f"============================")

def decode_qgif(input_path, output_path, color_depth):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_frame_path = os.path.join(output_path, "frames")
    if not os.path.exists(output_frame_path):
        os.makedirs(output_frame_path)
    output_png_path = os.path.join(output_path, "pngs")
    if not os.path.exists(output_png_path):
        os.makedirs(output_png_path)

    print("Decode qgif to frames ...")
    width = ctypes.c_int()
    height = ctypes.c_int()
    qgif_lib.decode_qgif(input_path.encode("utf-8"), output_frame_path.encode("utf-8"), color_depth,
            ctypes.byref(width), ctypes.byref(height))
    print("Decode qgif to frames finish.")

    print("Save frames to pngs ...")
    display_images(output_frame_path, output_png_path, width.value, height.value, color_depth)
    print("Save frames to pngs finish.")


def rgb565_to_rgb888(rgb565):
    rgb565 = ((rgb565 >> 8) & 0xff) | ((rgb565 & 0xff) << 8)
    r = ((rgb565 >> 11) & 0x1F) << 3
    g = ((rgb565 >> 5) & 0x3F) << 2
    b = (rgb565 & 0x1F) << 3
    return (r, g, b)

def convert_rgb888_to_image(data, width, height):
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            index = y * width + x
            pixels[x, y] = (data[index] & 0xff, (data[index] >> 8) & 0xff, (data[index] >> 16) & 0xff)
    return img

def convert_rgb565_to_image(data, width, height):
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            index = y * width + x
            rgb565 = data[index]
            pixels[x, y] = rgb565_to_rgb888(rgb565)
    return img

def display_images(frame_folder, png_folder, width, height, color_depth):
    files = [f for f in os.listdir(frame_folder) if f.endswith(".rgb")]
    files = [f for f in files if f.split(".")[0].isdigit()]
    sorted_files = sorted(files, key=lambda x: int(x.split(".")[0]))

    for image_file in tqdm(sorted_files):
        with open(os.path.join(frame_folder, image_file), "rb") as f:
            rgb_image = f.read()
            if color_depth == 32:
                rgb888_data = np.frombuffer(rgb_image, dtype=np.uint32)
                img = convert_rgb888_to_image(rgb888_data, width, height)
            elif color_depth == 16:
                rgb565_data = np.frombuffer(rgb_image, dtype=np.uint16)
                img = convert_rgb565_to_image(rgb565_data, width, height)
            image_name = get_filename_without_extension(image_file)
            img.save(os.path.join(png_folder, image_name + ".png"))

