import os
from PIL import Image
import sys

def convert_to_ico(input_path, output_path, sizes=[(32, 32)]):
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

    # Construct the full path for the input and output
    input_image = os.path.join(dir_path, 'assets', 'SMAK_logo.png')
    output_ico = os.path.join(dir_path, 'assets', 'SMAK_logo.ico')
    
    convert_to_ico(input_image, output_ico)

