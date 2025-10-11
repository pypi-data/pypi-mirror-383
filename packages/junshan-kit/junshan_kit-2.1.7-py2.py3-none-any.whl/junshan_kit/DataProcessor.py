
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
import junshan_kit.datahub

class CSVToPandas:
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

        # 导出后的大小
        m_export, n_export = df.shape

        if show_info:
            pos_count = (df['decision'] == 1).sum()
            neg_count = (df['decision'] == -1).sum()
            
            print('\n' + '='*70)
            print(f"{'GHPDD-Kaggle Dataset Info':^70}")
            print('='*70)
            print(f"{'Original size:':<35} {m_before} rows x {n_before} cols")
            print(f"{'Size after dropping NaNs:':<35} {m_after} rows x {n_after} cols")
            print(f"{'Export size (after encoding & scaling):':<35} {m_export} rows x {n_export} cols")
            print(f"{'Positive samples (+1):':<35} {pos_count}")
            print(f"{'Negative samples (-1):':<35} {neg_count}")
            print('-'*70)
            print(f"{'Note: categorical columns one-hot encoded, numerical standardized.':^70}")
            print(f"More details: https://www.jianguoyun.com/p/DU6Lr9oQqdHDDRj5sI0GIAA")
            print('='*70 + '\n')

        return df



