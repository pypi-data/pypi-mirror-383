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


def download_data():
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
            JianguoyunDownloaderFirefox(url=url).run()
            print("✅ Download completed using Firefox")
            break
        elif choice == "2":
            JianguoyunDownloaderChrome(url=url).run()
            print("✅ Download completed using Chrome")
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.\n")


def credit_card_fraud_detection(data_name = "Credit Card Fraud Detection"):

    csv_path = f'./exp_data/{data_name}' + 'creditcard.csv'
    drop_cols = []
    label_col = 'Class'
    label_map = {0: -1, 1: 1}

    if not os.path.exists(csv_path):
        print('\n' + '*'*60)
        print(f"Please download the data.")
        print(csv_path)
        download_data()
        junshan_kit.kit.unzip_file(f'./exp_data/{data_name}/{data_name}.zip', f'./exp_data/{data_name}')
        

    
        




    cleaner = junshan_kit.DataProcessor.CSV_TO_Pandas()
    cleaner.preprocess_dataset(csv_path, drop_cols, label_col, label_map)


    assert False
    
    dataloader = junshan_kit.DataProcessor.CSV_TO_Pandas()
    dataloader.preprocess_dataset()
    # Step 0: Load the dataset
    csv_path = "creditcard.csv"
    df = pd.read_csv(csv_path)



def wine_and_food_pairing_dataset():
    pass 

