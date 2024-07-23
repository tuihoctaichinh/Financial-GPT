import pandas as pd
import numpy as np
import requests 
from bs4 import  BeautifulSoup
import os
from datetime import datetime

path = 'E:/Report/VCSC/'
os.chdir(path)
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
files = os.listdir(path)
if not os.path.exists(path):
    os.makedirs(desktop+'/Report/VCSC/')
    os.chdir(desktop+'/Report/VCSC/')

url = 'https://www.vietcap.com.vn/api/cms-service/v1/page/analysis?is-all=true&page=0&size=200&direction=DESC&sortBy=date&language=2'
r = requests.get(url)
data = r.json()['data']['pagingGeneralResponses']['content']
df = pd.DataFrame(data)
filter_link = (~pd.isnull(df['file'])) & (df['pageLink'] != 'market-commentary')
link_pdf = df[filter_link]
link_pdf['fname'] = link_pdf['file'].apply(lambda x: x.split('/')[-1] if x else None)
filter_link = (~link_pdf['fname'].str.contains('Daily')) & (~link_pdf['fname'].str.contains('monthly'))
link_pdf = link_pdf[filter_link]

for i in range(len(link_pdf)):
    # check if the file is already downloaded or not
    if link_pdf['fname'].iloc[i] not in files:
        try:
            url = link_pdf['file'].iloc[i]
            r = requests.get(url)
            with open(link_pdf['fname'].iloc[i], 'wb') as f:
                f.write(r.content)
            print(f'{link_pdf["fname"].iloc[i]} is downloaded')
        except:
            print(f'{link_pdf["fname"].iloc[i]} error')
    else:
        print(f'{link_pdf["fname"].iloc[i]} exist')

