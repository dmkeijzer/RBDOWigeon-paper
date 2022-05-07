from operator import index
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import raw_data_geo as rdg
import scipy.stats as stat
import geoplot
import os


# Get the required data
#--------------------------------------------------------------------------
path_range_data = os.path.join(os.path.dirname(__file__), "journey.csv")
df_trips = pd.read_csv(path_range_data).to_numpy()
#------------------------------------------------------------------------

# Define all the functions for the analysis, see their docstrings
#------------------------------------------------------------------------------------------

def plot_hist(lim):
    """ Plots an histogram of the dataset given, 
    it must be of shape (x , 2) where x can be any number 
    """
    
    n, bins, pathches = plt.hist(x= df_trips[df_trips[:,1]<lim,1], bins= 18, color='#0504aa',alpha=0.8, rwidth=0.8, density= True)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Kilometres')
    plt.ylabel('Frequency')
    plt.title('Discrete distributions of direct flights')
    plt.show()
    return n, bins

def iso_cities(lim):
    """returns array with isolated cities for the limiter given
    There is a way more efficient way to do this, should probably change
    """

    iso = [] # ['Madrid', 'Lisbon', 'Warsaw', 'Bucharest'] result with 400

    for idx_i, city in enumerate(rdg.df_geo[:,0]):
        loc = []
        
        for idx_j, trip in enumerate(df_trips[:,0]):
            if trip.find(city) != -1: #checks whether city from outer loop is in the trip from the inner loop
                loc.append(idx_j)
        
        if len(loc) == 0: # if city is not recognized, move to next city
            continue
        all_trips_check = df_trips[loc, 1] < lim # list of all trips containing the city from outer loop
        if np.sum(all_trips_check) == 0:
            iso.append(city)
    
    return iso

def two_step_flight(max_range):
    """ The following functon will take all trips which are possible in two flights (parent trip) and store them
    as seperate trips (child trips). Each child trip will have the same probability"""
        
    df_nondir = df_trips[ df_trips[:,1]>lim , :]


    # Remove isolated cities 

    lst_iso = self.iso_cities(lim)
    loc1 = [] 
    
    for idx, trip in enumerate(df_nondir[:,0]): # for each trip check whether one of the isolated cities is within it
        for city in lst_iso: 
            if trip.find(city) != -1:   
                loc1.append(idx)
                continue
    
    df_nondir = np.delete(df_nondir, loc1, axis=0)

    # TODO: algorithm which divided up the cities 


plot_hist(800)







