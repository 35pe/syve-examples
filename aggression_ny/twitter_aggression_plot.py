#!/usr/bin/env python3

import numpy as np
import pandas as pd
import altair as alt
from geopy.geocoders import Nominatim
from time import sleep

LOCATIONS_DE = '/Users/sp/Lokal/LAB/framework/scraping/twitter/twitter_scrape_ny_state/locations.txt'
TOPOJSON_URL1 = 'https://raw.githubusercontent.com/deldersveld/topojson/master/countries/us-states/NY-36-new-york-counties.json' # ny state
TOPOJSON_URL2 = 'https://raw.githubusercontent.com/iliatimofeev/nytaxi/master/nyc_police_precincts-topojson.json' # ny city
DATA_PATH = 'twitter_aggression_data.csv'

data = pd.read_csv(DATA_PATH, engine='python')


# look up geo-coordinates
if 'latitude' not in data.columns:
	geolocator = Nominatim(user_agent="city_locations")
	latitudes = []
	longitudes = []
	location_dict = {}
	print('looking up geo-coordinates')

	with open(LOCATIONS_DE, 'r') as f:
		for name in f.readlines():
			name = name.strip()
			print(name)
			location = geolocator.geocode(name)
			location_dict[name] = (location.latitude, location.longitude)
			sleep(1.0)

	# clean
	#print('data shape before cleaning:', data.shape[0])
	#data = data[data.near != 'False']
	#print('after cleaning:', data.shape[0])

	for i, row in data.iterrows():
		latlong = location_dict[row['near']]
		latitudes.append(latlong[0])
		longitudes.append(latlong[1])

	#print('latitudes:', len(latitudes))
	#print('longitudes:', len(longitudes))
	#print('data.shape:', data.shape[0])

	data['latitude'] = np.asarray(latitudes)
	data['longitude'] = np.asarray(longitudes)
	data.drop(columns=['Unnamed: 0'], inplace=True)
	data.to_csv(DATA_PATH)

	print('done.')


# clean
#data.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'], inplace=True)
#data.to_csv(DATA_PATH)


# MAP (ny state)

# data will be included in the html -> do culling and aggregate values before (instead of using Chart.transform_aggregate)
map_data = data.groupby(['near']).mean()
map_data['near'] = map_data.index
map_data.drop(columns=['id'], inplace=True)  # , 'Unnamed: 0'

# cf. https://altair-viz.github.io/gallery/airports_count.html
topo = alt.topo_feature(TOPOJSON_URL1, feature='cb_2015_new_york_county_20m')

background = alt.Chart(topo).mark_geoshape(fill='lightgray', fillOpacity=1.0, stroke='white', strokeWidth=1).properties(width=500, height=500).project('mercator')

points = alt.Chart(map_data).mark_circle().encode(longitude='longitude:Q', latitude='latitude:Q', size=alt.Size('score:Q', title='score (mean)'), color='score:Q', tooltip=['near:N','score:Q']).properties(title='Aggression in the German-speaking Twittersphere')
#.transform_aggregate(latitude='mean(latitude)', longitude='mean(longitude)', count='mean(score)', groupby=['near'])
#color=alt.value('steelblue')

plot = background + points
plot.save('map.html')


# MAP 2 (ny city)

# data will be included in the html -> do culling and aggregate values before (instead of using Chart.transform_aggregate)
map_data = data.groupby(['near']).mean()
map_data['near'] = map_data.index
map_data.drop(columns=['id', 'Unnamed: 0'], inplace=True)

# remove other ny cities
map_data.drop(map_data[map_data.near.isin(['Albany', 'Syracuse', 'Rochester', 'Buffalo', 'Yonkers'])].index, inplace=True)

# cf. https://altair-viz.github.io/gallery/airports_count.html
topo = alt.topo_feature(TOPOJSON_URL2, feature='nyc_police_precincts')

background = alt.Chart(topo).mark_geoshape(fill='lightgray', fillOpacity=1.0, stroke='white', strokeWidth=1).properties(width=500, height=500).project('mercator')

points = alt.Chart(map_data).mark_circle().encode(longitude='longitude:Q', latitude='latitude:Q', size=alt.Size('score:Q', title='score (mean)'), color='score:Q', tooltip=['near:N','score:Q']).properties(title='Aggression in the German-speaking Twittersphere')
#.transform_aggregate(latitude='mean(latitude)', longitude='mean(longitude)', count='mean(score)', groupby=['near'])
#color=alt.value('steelblue')

plot = background + points
plot.save('map2.html')


# BAR CHART

data.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'], inplace=True)
data.columns = ['id', 'date', 'tweet', 'Area', 'Score', 'latitude', 'longitude']
plot = alt.Chart(data).mark_bar().encode(x='count(Score)', y=alt.Y('Area', sort=alt.EncodingSortField(field='Score', op='sum', order='descending')), color=alt.Color('Score:Q', bin=alt.Bin(maxbins=10))).properties(title='Scores by metropolitan area')
plot.save('barchart_total.html')
