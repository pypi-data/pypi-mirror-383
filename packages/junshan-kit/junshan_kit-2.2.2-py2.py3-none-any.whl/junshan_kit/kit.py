"""
----------------------------------------------------------------------
>>> Author       : Junshan Yin  
>>> Last Updated : 2025-10-13
----------------------------------------------------------------------
"""

import zipfile
import os

def unzip_file(zip_path: str, unzip_folder: str):
    """
    Args:
        zip_path (str): Path to the ZIP file to extract.
        dest_folder (str, optional): Folder to extract files into. 
            If None, the function will create a folder with the same 
            name as the ZIP file (without extension).

    Examples:
        >>> zip_path = "./downloads/data.zip"
        >>> unzip_folder = "./exp_data/data"
        >>> unzip_file(zip_path, unzip_folder)
    """

    if unzip_folder is None:
        unzip_folder = os.path.splitext(os.path.basename(zip_path))[0]

    os.makedirs(unzip_folder, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_folder)

    print(f"✅ Extracted '{zip_path}' to '{os.path.abspath(unzip_folder)}'")


