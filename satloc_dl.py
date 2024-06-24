from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time
import os
from argparse import ArgumentParser
import pandas as pd




def OpenBrowser(count, interval):
    """Set up webdriver."""

    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)

    directory = os.getcwd()
    options.set_preference("browser.download.dir", f'{directory}/Sat_csv/')
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

    if args.headless == True:
        options.add_argument('--headless')

    geckodriver_path = "/snap/bin/geckodriver"  # specify the path to your geckodriver
    driver_service = Service(executable_path=geckodriver_path)

    browser = webdriver.Firefox(options=options, service=driver_service)


    browser.get("https://satellitemap.space/#")
    #click cog button
    browser.find_element(By.XPATH, '/html/body/div[6]/div/a[2]/i').click()

    #click home
    browser.find_element(By.XPATH, '//*[@id="c3"]').click()

    #input lattitude
    browser.find_element(By.XPATH, '//*[@id="settings.myloc0"]').send_keys('24.7746')

    #input longitude
    browser.find_element(By.XPATH, '//*[@id="settings.myloc1"]').send_keys('121.0445')

    #click save
    browser.find_element(By.XPATH, '/html/body/div[10]/div/section/div/center/button[1]').click()

    time.sleep(5)

    download_data(browser)

    start = time.time()

    downloaded = 0
    while downloaded < count:
        if time.time()- start > interval:
            download_data(browser)
            downloaded += 1
            start = time.time()
            
    concat_csv('Sat_csv')


def download_data(browser):
    #click ...
    browser.find_element(By.XPATH, '/html/body/div[6]/div/a[3]').click()

    #click download data
    browser.find_element(By.XPATH, '/html/body/div[11]/div/section/div/div[2]/ul/li[7]/a').click()


def concat_csv(dl_path):
    files = os.listdir(dl_path)

    if len(files) < 2:
        return 0
    
    combined_csv = pd.read_csv(os.path.join(dl_path,files[0]))

    for file in files[1:]:
        new_csv = pd.read_csv(os.path.join(dl_path,file))
        combined_csv = pd.concat([combined_csv,new_csv])

    combined_csv.to_csv(f'combined.csv')


parser = ArgumentParser(prog = 'SatDL', description='Download Satellite positional data from the satellitemap.space')
parser.add_argument('--count', type = int, help ='Number of times data is downloaded from the website',default=10)       
parser.add_argument('--interval', type = int, help ='Time between downloads, measured in seconds', default=300)
parser.add_argument('--headless', type = bool, default=True, help = 'Toggle headless option for selenium')

args = parser.parse_args()
try: 
    os.mkdir('Sat_csv')
except:
    print('Download folder exists')

OpenBrowser(args.count,args.interval)

os.rmdir('Sat_csv')

