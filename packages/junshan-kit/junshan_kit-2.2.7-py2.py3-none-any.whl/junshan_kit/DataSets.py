"""
----------------------------------------------------------------------
>>> Author       : Junshan Yin  
>>> Last Updated : 2025-xx-xx
----------------------------------------------------------------------
"""

import os, time
import pandas as pd
import junshan_kit.DataProcessor
import junshan_kit.kit
from sklearn.preprocessing import StandardScaler


def download_data(data_name):
    from junshan_kit.kit import JianguoyunDownloaderFirefox, JianguoyunDownloaderChrome

    # User selects download method
    while True:
        # User inputs download URL
        url = input("Enter the Jianguoyun download URL: ").strip()

        print("Select download method:")
        print("1. Firefox")
        print("2. Chrome")
        choice = input("Enter the number of your choice (1 or 2): ").strip()

        if choice == "1":
            JianguoyunDownloaderFirefox(url, f"./exp_data/{data_name}").run()
            print("✅ Download completed using Firefox")
            break
        elif choice == "2":
            JianguoyunDownloaderChrome(url, f"./exp_data/{data_name}").run()
            print("✅ Download completed using Chrome")
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.\n")


def credit_card_fraud_detection(data_name = "Credit Card Fraud Detection", print_info = False):

    csv_path = f'./exp_data/{data_name}/creditcard.csv'
    drop_cols = []
    label_col = 'Class'
    label_map = {0: -1, 1: 1}

    if not os.path.exists(csv_path):
        print('\n' + '*'*60)
        print(f"Please download the data.")
        print(csv_path)
        download_data(data_name)
        junshan_kit.kit.unzip_file(f'./exp_data/{data_name}/{data_name}.zip', f'./exp_data/{data_name}')
        
    cleaner = junshan_kit.DataProcessor.CSV_TO_Pandas()
    df = cleaner.preprocess_dataset(csv_path, drop_cols, label_col, label_map, print_info=print_info)

    return df
    
    


def wine_and_food_pairing_dataset():
    pass 

