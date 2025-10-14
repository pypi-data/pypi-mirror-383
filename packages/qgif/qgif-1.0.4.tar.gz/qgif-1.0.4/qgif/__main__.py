#!/usr/bin/env python

import sys
import os
import argparse

from qgif import VERSION
from qgif.qgif import convert_gif_to_qgif, decode_qgif

def check_range(param_name, t):
    def checker(value):
        value = t(value)
        if value < 0 or value > 10:
            raise argparse.ArgumentTypeError(f"Argument '{param_name}' must be between 0 and 10, but got {value}")
        return value
    return checker

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="qgif", description="QGIF generator and decoder")
    subparsers = parser.add_subparsers(dest="command")

    parser_convert = subparsers.add_parser("convert", help="Convert GIF to QGIF.")
    parser_convert.add_argument("-f", "--format", required=True, choices=["gx64", "gx96"], help="The format of generated QGIF frames.")
    parser_convert.add_argument("-i", "--input", required=True, help="The input GIF file name.")
    parser_convert.add_argument("-o", "--output", required=True, help="Generated QGIF file name.")
    parser_convert.add_argument("-fr", "--framerate", type=int, default=0, help="The frame rate of QGIF file. (default: same as GIF)")
    parser_convert.add_argument("-l", "--lvgl", action="store_true", help="Generate LVGL C file.")
    parser_convert.add_argument("--crop-size", type=int, nargs=2, help="Size to crop the image (width height)")
    parser_convert.add_argument("--scale-size", type=int, nargs=2, help="Size to scale the image (width height)")
    parser_convert.add_argument("--bilateral-strength", default=0, type=check_range("--bilateral-strength", float),
            help="Strength of bilateral filter (0-10, can be a float)")
    parser_convert.add_argument("--median-strength", default=0, type=check_range("--median-strength", int),
            help="Strength of spatial median filter (0-10)")
    parser_convert.add_argument("--interframe-threshold", default=0, type=check_range("--interframe-threshold", int),
            help="Threshold for interframe median filtering (0-10)")
    parser_convert.add_argument("--temporal-threshold", default=0, type=check_range("--temporal-threshold", int),
            help="Threshold for temporal denoise (0-10)")

    parser_decode = subparsers.add_parser("decode", help="Decode QGIF to frames.")
    parser_decode.add_argument("-i", "--input", required=True, help="The input QGIF file name.")
    parser_decode.add_argument("-o", "--output", required=True, help="The directory of output frames and pngs.")
    parser_decode.add_argument("-c", "--colordepth", type=int, required=True, choices=[16, 32], help="The color depth of decoded frames.")

    parser.add_argument("-V", "--version", action="version", version="qgif %s" % VERSION)

    args = parser.parse_args()
    if args.command == "convert":
        convert_gif_to_qgif(args.input,
                args.output,
                args.format,
                args.lvgl,
                args.framerate,
                crop_size=args.crop_size,
                scale_size=args.scale_size,
                bilateral_strength=args.bilateral_strength,
                median_strength=args.median_strength,
                interframe_threshold=args.interframe_threshold,
                temporal_threshold=args.temporal_threshold)
    elif args.command == "decode":
        decode_qgif(args.input, args.output, args.colordepth)

