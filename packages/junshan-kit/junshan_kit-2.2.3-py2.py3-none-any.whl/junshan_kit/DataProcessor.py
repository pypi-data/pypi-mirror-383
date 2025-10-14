"""
----------------------------------------------------------------------
>>> Author       : Junshan Yin  
>>> Last Updated : 2025-10-12
----------------------------------------------------------------------
"""

import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
import junshan_kit.datahub
import zipfile

class CSVToPandasMeta:
    def __init__(self):
        self.data_downloader = junshan_kit.datahub.kaggle_data()
        

    def read_csv(self, data_name):
        self.csv_path = f'exp_data/{data_name}/{data_name}.csv'
        if not os.path.exists(self.csv_path):
            self.data_downloader.download_data(f'{data_name}', f'exp_data/{data_name}')  

    # ----------------- ccfd_kaggle ----------------------------------
    def ccfd_kaggle(self, data_name = 'ccfd-kaggle', show_info = True):
        # download data if not exist
        self.read_csv(data_name)
        
        df = pd.read_csv(self.csv_path)
        m_before, n_before = df.shape
        df = df.dropna(axis=0, how='any')
        m_after, n_after = df.shape
        df['Class'] = df['Class'].replace(0, -1)

        if show_info:
            pos_count = (df['Class'] == 1).sum()
            neg_count = (df['Class'] == -1).sum()
            
            print('\n' + '='*60)
            print(f"{'CCFD-Kaggle Dataset Info':^60}")
            print('='*60)
            print(f"{'Original size:':<25} {m_before} rows x {n_before} cols")
            print(f"{'Size after dropping NaNs:':<25} {m_after} rows x {n_after} cols")
            print(f"{'Positive samples (+1):':<25} {pos_count}")
            print(f"{'Negative samples (-1):':<25} {neg_count}")
            print(f"{'Export size:':<25} {m_after} rows x {n_after} cols")
            print('-'*60)
            print(f"More details: https://www.jianguoyun.com/p/Dd1clVgQ4ZThCxiwzZQGIAA")
            print('='*60 + '\n')

        return df
    
    # ------------------------ 
    def ghpdd_kaggle(self, data_name='ghpdd-kaggle', show_info=True):
        # download data if not exist
        self.read_csv(data_name)

        # read csv
        df = pd.read_csv(self.csv_path)
        m_before, n_before = df.shape

        # drop NaNs
        df = df.dropna(axis=0, how='any')
        m_after, n_after = df.shape

        # drop unique identifier
        if 'property_id' in df.columns:
            df.drop(columns=['property_id'], inplace=True)

        # Replace label 0 with -1
        df['decision'] = df['decision'].replace(0, -1)

        # Identify categorical and numerical columns
        cat_cols = ['country', 'city', 'property_type', 'furnishing_status']
        num_cols = [col for col in df.columns if col not in cat_cols + ['decision']]

        # One-Hot encode categorical columns
        df = pd.get_dummies(df, columns=cat_cols)

        # Convert boolean columns to int
        bool_cols = df.select_dtypes(include='bool').columns
        for col in bool_cols:
            df[col] = df[col].astype(int)

        # Standardize numerical columns
        scaler = StandardScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])

        # The size after export
        m_export, n_export = df.shape

        if show_info:
            pos_count = (df['decision'] == 1).sum()
            neg_count = (df['decision'] == -1).sum()
            
            print('\n' + '='*70)
            print(f"{'GHPDD-Kaggle Dataset Info':^70}")
            print('='*70)
            print(f"{'Original size:':<35} {m_before} rows x {n_before} cols")
            print(f"{'Size after dropping NaNs:':<35} {m_after} rows x {n_after} cols")
            print(f"{'Positive samples (+1):':<35} {pos_count}")
            print(f"{'Negative samples (-1):':<35} {neg_count}")
            print(f"{'Export size (after encoding & scaling):':<35} {m_export} rows x {n_export} cols")
            print('-'*70)
            print(f"{'Note: categorical columns one-hot encoded, numerical standardized.'}")
            print(f"More details: https://www.jianguoyun.com/p/DU6Lr9oQqdHDDRj5sI0GIAA")
            print('='*70 + '\n')

        return df



class CSV_TO_Pandas:
    def __init__(self):
        pass

    def unzip_file(self, zip_path: str, unzip_folder: str):
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
    
    # -----------------------------------------------------

    def clean_data(self, csv_path, drop_cols: list, label_col: str, label_map: dict,  print_info = False):
        # Step 0: Load the dataset
        df = pd.read_csv(csv_path)

        # Save original size
        m_original, n_original = df.shape

        # Step 1: Drop non-informative columns
        df = df.drop(columns=drop_cols)

        # Step 2: Remove rows with missing values
        df = df.dropna(axis=0, how='any')
        m_encoded, n_encoded = df.shape
        
        # Step 3: Map target label to -1 and +1
        df[label_col] = df[label_col].map(label_map)

        # Step 4: Encode categorical features (exclude label column)
        text_feature_cols = df.select_dtypes(include=['object', 'string', 'category']).columns
        text_feature_cols = [col for col in text_feature_cols if col != label_col]  # ✅ exclude label

        df = pd.get_dummies(df, columns=text_feature_cols, dtype=int)
        m_cleaned, n_cleaned = df.shape

        # print info
        if print_info:
            pos_count = (df[label_col] == 1).sum()
            neg_count = (df[label_col] == -1).sum()

            # Step 6: Print dataset information
            print('\n' + '='*80)
            print(f"{'Dataset Info':^70}")
            print('='*80)
            print(f"{'Original size:':<40} {m_original} rows x {n_original} cols")
            print(f"{'Size after dropping NaN & non-feature cols:':<40} {m_cleaned} rows x {n_cleaned} cols")
            print(f"{'Positive samples (+1):':<40} {pos_count}")
            print(f"{'Negative samples (-1):':<40} {neg_count}")
            print(f"{'Size after one-hot encoding:':<40} {m_encoded} rows x {n_encoded} cols")
            print('-'*80)
            print(f"Note:")
            print(f"{'Label column:':<40} {label_col}")
            print(f"{'Dropped non-feature columns:':<40} {', '.join(drop_cols) if drop_cols else 'None'}")
            print(f"{'text fetaure columns:':<40} {', '.join(list(text_feature_cols)) if list(text_feature_cols) else 'None'}")
            print('='*80 + '\n')

        return df

        

        
