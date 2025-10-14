"""
----------------------------------------------------------------------
>>> Author       : Junshan Yin  
>>> Last Updated : 2025-10-12
----------------------------------------------------------------------
"""

import kagglehub
import os, time
import warnings
import shutil
from kaggle.api.kaggle_api_extended import KaggleApi
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class kaggle_data:
    def list_datasets(self):
        api = KaggleApi()
        api.authenticate()
        datasets = api.dataset_list(user='junshan888')
        print('Available datasets:')
        print('*' * 60)
        if datasets is not None:
            for ds in datasets:
                if ds is not None:
                    print(ds.title)
        print('*' * 60)
    
    def list_user_datasets(self):
        warnings.warn(
            "list_user_datasets() is deprecated. Use list_datasets() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.list_datasets()
    
        # example:  list_user_datasets()

    #---------------------------------------------------------------
    def download_data(self, data_name = 'letter-libsvm', copy_path = None):
        path = kagglehub.dataset_download(f'junshan888/{data_name}')
        # print("Downloaded to:", path)
        if copy_path is not None:
            # Create target directory if it doesn't exist
            os.makedirs(copy_path, exist_ok=True)
            # Copy dataset to target directory
            shutil.copytree(path, copy_path, dirs_exist_ok=True)

            print(f"✅ Dataset has been copied to: {copy_path}")

    # example: read_data(copy_path='./exp_data')


class JianguoDownloaderChrome:
    def __init__(self, url: str, download_path: str = "./downloads"):
        self.url = url
        self.download_path = os.path.abspath(download_path)
        os.makedirs(self.download_path, exist_ok=True)

        # Configure Chrome options
        self.chrome_options = Options()
        prefs = {
            "download.default_directory": self.download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1,
        }
        self.chrome_options.add_experimental_option("prefs", prefs)

        # Optional stability flags
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")

        # Start Chrome
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def open_page(self):
        """Open the Jianguoyun share page."""
        print(f"🌐 Opening link: {self.url}")
        self.driver.get(self.url)

    def click_download_button(self):
        """Find and click the download button."""
        print("🔍 Looking for the download button...")
        wait = WebDriverWait(self.driver, 30)
        span = wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'下载')]"))
        )
        parent = span.find_element(By.XPATH, "./..")
        self.driver.execute_script("arguments[0].click();", parent)
        print(f"✅ Download button clicked. Files will be saved to: {self.download_path}")

        # If Jianguoyun opens a new tab, switch to it
        time.sleep(3)
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            print("📂 Switched to download tab.")

    def wait_for_downloads(self, timeout=30000):
        """Wait until all downloads are finished."""
        print("⏳ Waiting for downloads to finish...")
        start_time = time.time()
        while True:
            downloading = [f for f in os.listdir(self.download_path) if f.endswith(".crdownload")]
            if not downloading:
                print("✅ Download completed!")
                return True
            if time.time() - start_time > timeout:
                print("⏰ Timeout: downloads may not have finished.")
                return False
            time.sleep(2)

    def get_latest_file(self):
        """Return the most recently downloaded file (if any)."""
        files = [os.path.join(self.download_path, f) for f in os.listdir(self.download_path)]
        return max(files, key=os.path.getctime) if files else None

    def close(self):
        """Close the browser."""
        self.driver.quit()
        print("🚪 Browser closed.")

    def run(self):
        """Run the complete download process."""
        print('*'*50)
        try:
            self.open_page()
            self.click_download_button()
            self.wait_for_downloads()
            latest = self.get_latest_file()
            if latest:
                print(f"📄 Latest downloaded file: {latest}")
        except Exception as e:
            print("❌ Error occurred:", e)
        finally:
            self.close()
        print('*'*50)



