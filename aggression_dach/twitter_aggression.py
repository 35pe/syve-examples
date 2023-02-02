#!/usr/bin/env python3

import os
import requests
import pandas as pd
from glob import glob
from tqdm import tqdm

# development
API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoxLCJleHBfIjoxNTkxMjE1NDgxLjE1MzUwODJ9.GEBE3VBh5bPIYIp5XSn1ktdABFJmbcAhoeKAxowFIgg'
URL = 'http://127.0.0.1:5000/api/off/de/v1'

# production
#API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoxLCJleHBfIjoxNTg4NDA3NTk1LjI5MzIxMzh9.9ugPM9gIoez2FHjoLEdVXX10saLXMPnGLEZj5b2RZcw'
#URL = 'https://hexis.ai/api/off/de/v1'

LOCATIONS_DE = '/Users/sp/Lokal/LAB/framework/scraping/twitter/twitter_scrape_dach_region/locations.txt'
DATA_PATH = '/Users/sp/Lokal/LAB/framework/scraping/twitter/twitter_scrape_dach_region/data'
SAMPLE_SIZE = 10000

results = pd.DataFrame(columns=['id', 'date', 'tweet', 'near', 'score'])

for path in tqdm(glob(DATA_PATH + '/*.csv')):
	#print(path)
	df_all = pd.read_csv(path, header=0, usecols=['id', 'date', 'tweet', 'near'], engine='python')
	#df = df_all.sample(SAMPLE_SIZE)  # randomly sample n rows
	df = df_all.head(SAMPLE_SIZE)  # take the top n rows

	for i, row in df.iterrows():
		#try:
		text = row['tweet'].replace('"','\\"').replace('\n', ' ').replace('#', '')
		#except:
		#	print(row)
		#	continue
		header = {'Authorization': 'Bearer ' + API_KEY}
		data = {'text': text}
		response = requests.post(URL, json=data, headers=header)
		score = response.json()['scores'][0]

		results = results.append({'id': row['id'],
								'date': row['date'],
								'tweet': row['tweet'],
								'near': row['near'],
								'score': score}, ignore_index=True)

print(results.shape[0], 'items')
# caution: deduplication might result in locations with very small/skewed data
#results.drop_duplicates(['id'], inplace=True)
#print(results.shape[0], 'items after deduplication')
results.to_csv('twitter_aggression_data.csv')
