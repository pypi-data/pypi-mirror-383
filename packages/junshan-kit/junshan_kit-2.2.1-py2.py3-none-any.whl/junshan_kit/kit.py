import zipfile
import os

def unzip_file(zip_path, dest_folder=None):
    """
    Extract a ZIP file to a folder.

    Parameters:
        zip_path (str): Path to the ZIP file to extract.
        dest_folder (str, optional): Folder to extract files into.
                                    If None, the function uses a folder
                                    with the same name as the ZIP file.
    """
    if dest_folder is None:
        dest_folder = os.path.splitext(os.path.basename(zip_path))[0]

    os.makedirs(dest_folder, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_folder)

    print(f"✅ Extracted '{zip_path}' to '{os.path.abspath(dest_folder)}'")
