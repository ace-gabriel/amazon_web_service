import os, sys, json, requests
import pandas as pd
import numpy as np
import fiona
from shapely.geometry import shape,mapping, Point, Polygon, MultiPolygon
import shapely
import geopandas as gpd

__author__ = "__Gabriel__"
__contact__ = " __gabrielyin@berkeley.edu__"

# basic read ins
try:
    print("Reading Bike Data...")
    bike_data = pd.read_csv('bike_trips/cuspadsdata/bike_trips/201606-citibike-tripdata.csv')
except ValueError:
    print("Error reading bike data.")

# try:
#     green_taxi = pd.read_csv('data/green_201606.csv')
# except ValueError:
#     print("Error reading green taxi data.")

try:
    print("Reading Yellow Taxi Data...")
    yellow_taxi = pd.read_csv('yellow_taxi/yellow_taxi/yellow_201606.csv')
except ValueError:
    print("Error reading yellow taxi data.")

try:
    # get taxi data zone data and process it into the database
    print("Reading Map Data...")
    taxi_zone = gpd.GeoDataFrame.from_file('taxi_zones/cuspadsdata/taxi_zones/taxi_zones.shp').to_crs({'proj':'longlat', 'ellps':'WGS84', 'datum':'WGS84'})
    taxi_zone = taxi_zone[taxi_zone['borough'] == "Manhattan"]
except ValueError:
    print("Error reading taxi zone shapefile.")

# preprocess data and location-zone mapping preprocessing
bike_data = bike_data[['starttime', 'stoptime', 'start station id', 'start station name', 'start station latitude',
                      'start station longitude', 'end station latitude', 'end station longitude']]
# create features that map the start point to a geo location
bike_data['start_point'] = [shapely.geometry.Point(long, lat) for lat, long in zip(bike_data['start station latitude'],
                                                                             bike_data['start station longitude'])]
# similarly we do the same for the end point location
bike_data['end_point'] = [shapely.geometry.Point(long, lat) for lat, long in zip(bike_data['end station latitude'],
                                                                             bike_data['end station longitude'])]
# create a dictionary to map a zone to its location ID
location_zone_mapping = {zone : aid for zone, aid in zip(taxi_zone['LocationID'], taxi_zone['geometry'])}

# map each taxi trip's start & end data to the taxi zone
for i in np.arange(0, len(bike_data)):
    for zone in location_zone_mapping.keys():
        if bike_data['start_point'][i].within(location_zone_mapping[zone]):

            print("Verbose 0: Assigned taxi zone %d to start bike trip %d" % (zone, i))
            bike_data.loc[i]['start_zone'] = zone

        if bike_data['end_point'][i].within(location_zone_mapping[zone]):
            print("Verbose 0: Assigned taxi zone %d to end bike trip %d" % (zone, i))
            bike_data.loc[i]['end_zone'] = zone

    print("%d trips left. " % (len(bike_data) - i))
    print("-" * 20)

# export csv file
bike_data.to_csv("bike_data.csv", sep="\t")
