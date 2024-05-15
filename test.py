


'''
Convert image to .ico icon

'''

import os
from PIL import Image
import sys

def convert_to_ico(input_path, output_path, sizes=[(64, 64)]):
    """
    Convert an image to ICO format.
    
    Args:
    input_path (str): The path to the input image file.
    output_path (str): The path where the .ico file will be saved.
    sizes (list): A list of tuple sizes for the icon.
    """
    with Image.open(input_path) as img:
        img.save(output_path, format='ICO', sizes=sizes)

if __name__ == "__main__":
    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    assets_dir = os.path.join(dir_path, 'assets')

    # Loop through all files in the assets directory
    for file_name in os.listdir(assets_dir):
        if file_name.endswith('.png'):
            input_image = os.path.join(assets_dir, file_name)
            output_ico = os.path.join(assets_dir, file_name.replace('.png', '.ico'))
            
            convert_to_ico(input_image, output_ico)


'''
Profile memory of import statements

'''

# from memory_profiler import profile

# @profile
# def import_modules():
#     from print_tricks import pt
    
#     import json, ctypes, threading, sys, os, time
#     import tkinter as tk
#     from tkinter import font, messagebox
#     from pynput import keyboard, mouse
#     from pystray import MenuItem as item, Icon, Menu, MenuItem
#     from PIL import Image

# # Call the function to execute the imports and profile them
# import_modules()

# '''
# python -m memory_profiler test.py
# '''