import geopandas as gpd
import numpy as np
import pandas as pd
from geopy.distance import distance
import os


#-------------------------------
# Required paths and reading in files
#--------------------------------

path_geo_dataset = r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\own_code\shapefiles\ne_10m_populated_places_simple.shp"
path_cities_dataset = r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\own_code\cities_by_gmp.xlsx"
df_cities_shp = gpd.read_file(path_geo_dataset)
cities_df = pd.read_excel(path_cities_dataset)

# ---------------------------------------------------------------------------------------------
# The code hereunder checks which cities are available in the shapefile from our required
# list and their index in the shapefile to be able to retrieve them.
#----------------------------------------------------------------------------------------------

shp_cities = df_cities_shp["name"].to_numpy() # Available cities from shapefile
list_cities = cities_df["metropolitan_area"].to_numpy() #list of required cities
loc = []

for city in list_cities:
    idx = np.where(shp_cities == city)[0]
    if len(idx) > 0:
        loc.append(idx[0])

eur_cities = df_cities_shp.iloc[loc] # final result (european cities)

#---------------------------------------------------------------------------------------------------
# Some of the data gets filtered and replaced manually. Also some missing data gets added manually
# Only Rhine - Neckar is left out due to it consisting out of a lot of municipals
#---------------------------------------------------------------------------------------------------

df_geo = eur_cities[["name", "latitude", "longitude"]].to_numpy()
filter = (df_geo[:,0]!="Valencia") * (df_geo[:,0]!="Naples") * (df_geo[:,0]!="Dublin") * (df_geo[:,0]!="Athens") * (df_geo[:,0]!="Barcelona")
df_geo = df_geo[filter, :] # removed cities due to untrustworthy data 37 cities left
correction_data = [["London", 51.509865, -0.118092],
                   ["Valencia", 39.466667, -0.375000],
                   ["Naples", 40.853294, 14.305573],
                   ["Dublin", 53.350140, -6.266155],
                   ["Athens", 37.983810, 23.727539],
                   ["Barcelona", 41.390205, 2.154007],
                   ["Gothenburg", 57.708870, 11.974560],
                   ["Nuremburg", 49.460983, 11.061859],
                   ["Braunschweig", 52.266666, 10.51667],
                   ["Hanover", 52.373920, 9.735603],
                   ["Antwerp", 51.2194475, 4.4024643],
                   ["Brescia", 45.541553, 10.211802]]

df_geo = np.append(df_geo, correction_data, axis=0)

# pd.DataFrame(df_geo).to_csv(os.path.join(os.path.dirname(__file__), "plotting_df1.csv") , header= ["name", "lat", "lon"])

def create_trip_file():

    n = 1 
    df_distance = [] 

    for idx_i, city_i in enumerate(df_geo[:,0]):  
        i_str = str(city_i)
        i_coord = (df_geo[idx_i, 1] , df_geo[idx_i, 2])
        
        for idx_j, city_j in enumerate(df_geo[n:,0], start= n):
            j_str = str(city_j)
            j_coord = (df_geo[idx_j, 1] , df_geo[idx_j, 2])
            journey = i_str + "-" + j_str
            dist_journey = distance(i_coord, j_coord).km #computes distance based on coordinates
            
            df_distance.append([journey, dist_journey])
        
        n = n + 1

    #write data to csv file

    df_distance = pd.DataFrame(df_distance)
    df_distance.to_csv(r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\own_code\journey.csv", header=["city-city", "dist"], index= False)
    print("Journey file has been correctly written and saved")


    