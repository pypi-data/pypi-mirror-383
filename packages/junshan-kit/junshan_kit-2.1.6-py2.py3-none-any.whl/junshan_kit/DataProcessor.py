
import pandas as pd
import os

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
            print(f"{'Export size:':<25} {m_after} rows x {n_after} cols")
            print(f"{'Positive samples (+1):':<25} {pos_count}")
            print(f"{'Negative samples (-1):':<25} {neg_count}")
            print('-'*60)
            print(f"More details: https://www.jianguoyun.com/p/Dd1clVgQ4ZThCxiwzZQGIAA")
            print('='*60 + '\n')

        return df


