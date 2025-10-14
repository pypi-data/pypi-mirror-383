import os
import re

def sanitize_filename(filename):
    # 移除不合法的字符，只保留字母、数字和下划线
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', filename)

    # 如果第一个字符是数字，则在前面加上一个下划线
    if sanitized and sanitized[0].isdigit():
        sanitized = '_' + sanitized

    # 检查是否是C语言的关键字
    c_keywords = {
        "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum", "extern",
        "float", "for", "goto", "if", "inline", "int", "long", "register", "restrict", "return", "short", "signed",
        "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while", "_Alignas",
        "_Alignof", "_Atomic", "_Bool", "_Complex", "_Generic", "_Imaginary", "_Noreturn", "_Static_assert", "_Thread_local"
    }

    if sanitized in c_keywords:
        sanitized = '_' + sanitized

    return sanitized

def gen_lvgl_file(bin_file, lvgl_file, image_width, image_height):
    image_name_with_extension = os.path.basename(bin_file)
    image_name, _ = os.path.splitext(image_name_with_extension)
    image_name = sanitize_filename(image_name)

    # 读取二进制文件
    with open(bin_file, 'rb') as bin_file:
        bin_data = bin_file.read()

    # 生成C文件内容
    c_file_content = f"""#ifdef __has_include
    #if __has_include("lvgl.h")
        #ifndef LV_LVGL_H_INCLUDE_SIMPLE
            #define LV_LVGL_H_INCLUDE_SIMPLE
        #endif
    #endif
#endif

#if defined(LV_LVGL_H_INCLUDE_SIMPLE)
    #include "lvgl.h"
#else
    #include "lvgl/lvgl.h"
#endif

#ifndef LV_ATTRIBUTE_MEM_ALIGN
#define LV_ATTRIBUTE_MEM_ALIGN
#endif

#ifndef LV_ATTRIBUTE_IMG_{image_name.upper()}
#define LV_ATTRIBUTE_IMG_{image_name.upper()}
#endif

const LV_ATTRIBUTE_MEM_ALIGN LV_ATTRIBUTE_LARGE_CONST LV_ATTRIBUTE_IMG_{image_name.upper()} uint8_t {image_name}_bin[] = {{
"""

    # 将二进制数据转换为C数组格式
    for i, byte in enumerate(bin_data):
        if i % 12 == 0:
            c_file_content += '\n  '
        c_file_content += f'0x{byte:02x}, '

    c_file_content = c_file_content.rstrip(', ')  # 移除最后一个逗号和空格
    c_file_content += '\n};\n\n'

    # 添加图像描述符
    c_file_content += f"""const lv_img_dsc_t {image_name} = {{
  .header.cf = LV_IMG_CF_RAW_CHROMA_KEYED,
  .header.always_zero = 0,
  .header.reserved = 0,
  .header.w = {image_width},
  .header.h = {image_height},
  .data_size = {len(bin_data)},
  .data = {image_name}_bin,
}};
"""

    # 写入C文件
    with open(lvgl_file, 'w') as c_file:
        c_file.write(c_file_content)

