import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
import os
import file_creation as rdg

#----------------------------
# Get the required data
#--------------------------------
path_range_data = os.path.join(os.path.dirname(__file__), "trip_2.0.csv")
gdp_data_path =  os.path.join(os.path.dirname(__file__), "plotting_df.csv")

df_trips = pd.read_csv(path_range_data).to_numpy() # array - example row ['The Hague-Bremen' 326.5480004995904 'The-Bre-dir' 99.0] 


class Bin():
    def __init__(self, frequency, edges, flight_df, total_df_gdp):
        self.left_bound =  edges[0]
        self.right_bound = edges[1]
        self.flights = flight_df[(flight_df[:,1].astype("float64") > self.left_bound) * (flight_df[:,1].astype("float64") < self.right_bound)]
        self.freq = frequency
        self.df_gdp = total_df_gdp

    def bin_expectation(self):
        pass
        labels = self.flights[:,2]
        sum_bin_gdp =  np.sum(self.flights[:,3].astype("float64"))

        eq_par_trip = [] # list - "equal parent trip, meaning flight that came from the same two trip flight"
        
        for idx_i, i in enumerate(labels):
            for idx_j, j in enumerate(labels):
                if idx_i != idx_j:
                    if i == j:
                        eq_par_trip.append([self.flights[idx_i,0], self.flights[idx_j,0], self.flights[idx_i, 3]])
        eq_par_trip = np.array(eq_par_trip)
        if len(eq_par_trip) > 0:
            corr_fac = np.sum(eq_par_trip[: : 2,2].astype("float64")) / self.df_gdp  # corrrection factor for rule of addition, P(A n B) happens when a two way trip had the same parent trip
            corr_bin_gdp = sum_bin_gdp / self.df_gdp - corr_fac
            weighted_freq = self.freq * corr_bin_gdp
        else: 
            weighted_freq = self.freq *  (sum_bin_gdp / self.df_gdp)
        
        return weighted_freq

#===================================================================
# Define all the functions for the analysis, see their docstrings
#===================================================================

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

def two_trip_analysis(lim):
    """ Elobarote on function later 
    """
    data = []

    two_trip = df_trips[(df_trips[:,1] < 2 * lim) * (df_trips[:,1] > lim) ] #selects trips which could be flown in two flight but not one
    one_trip = df_trips[df_trips[:,1] < lim] #array - selects direct flights

    for trip_2 in two_trip:
        depar_connect = np.ones((1,4)) # array - initialize arrays which will contain all direct connections to the current hub in the loop
        dest_connect = np.ones((1,4)) 
        
        depar = trip_2[0].split("-")[0] # string - The departure hub/city
        dest = trip_2[0].split("-")[1]
        
        for i in one_trip: # loop to get all connections from departure hub under the limit
            if i[0].split("-")[0] == depar or i[0].split("-")[1] == depar: 
                depar_connect = np.append(depar_connect, [i], axis=0)
        
        for j in one_trip: # loop to get all connect to destination hub under the limit
            if j[0].split("-")[1] == dest or j[0].split("-")[0] == dest: 
                dest_connect = np.append(dest_connect, [j] , axis=0)

        depar_connect = np.delete(depar_connect, 0 , axis=0) # deleting ones created at the beginning to avoid error
        dest_connect = np.delete(dest_connect, 0 , axis=0)
        
        hubs_depar = [i.split("-")[1] if i.split("-")[0] == depar else i.split("-")[0]  for i in depar_connect[:,0]] #creating list with connected hubs so we math them
        hubs_dest = [i.split("-")[1] if i.split("-")[0] == dest else i.split("-")[0]  for i in dest_connect[:,0]]

        if len(set(hubs_dest).intersection(hubs_depar)) == 0: # bool - See if a match exists between connected hubs, if not continue to next trip
            continue
        else:
            intersections = set(hubs_dest).intersection(hubs_depar) # set - intersection refers to the hubs both departure and destination could fly to
            lst_depar_intersec = [] # list - initalize list that will contain distance fro departure to intersection
            lst_dest_intersec = []
            
            for idx in range(len(intersections)): #this loop gets the distances from all possible routes so  from departure - intersections and intersection - destination
                lst_depar_intersec.append([i[1]  for i in one_trip if depar + "-" + list(intersections)[idx] == i[0] or list(intersections)[idx] + "-"  + depar == i[0]][0]) 
                lst_dest_intersec.append([i[1]  for i in one_trip if dest + "-" + list(intersections)[idx] == i[0] or list(intersections)[idx] + "-"  + dest == i[0]][0])
            
            sum_range = np.array(lst_depar_intersec) + np.array(lst_dest_intersec) # array - sum the departure - intersection - destination ranges 
            idx_intersec = np.where(sum_range == min(sum_range))[0][0] # integer - represents the index
            shorterst_intersec = list(intersections)[idx_intersec] # string - city shortest intersectiom
            label = depar[:3] + "-" + dest[:3] + "-2step"
            sum_gdp = trip_2[3] # Get the sum gdp, which will be necessary for the probability distribution
            data.append([depar + "-" + shorterst_intersec, float(lst_depar_intersec[idx_intersec]) ,label , sum_gdp] )
            data.append([shorterst_intersec + "-" + dest, float(lst_dest_intersec[idx_intersec]) , label , sum_gdp])
    
    data = np.array(data) # array - example of a row ['Lyon-Milan', '342.78286276713493', 'Par-Mil-2step', '955.8'] 
    return data

def plot_hist_two_trip_weightless(lim , n_bins):
    """ Plots an histogram of the dataset given, 
    it must be of shape (x , 2) where x can be any number 
    """
    
    direct_flights = df_trips[df_trips[:,1] < lim]
    two_step_flights = two_trip_analysis(lim)
    total_flights = np.append(direct_flights, two_step_flights, axis= 0) # array - example ['Paris-Dortmund', 470.1237855871516, 'Par-Dor-dir', 910.4]
    hist_data = total_flights[:,1].astype("float64")
    plt.hist(hist_data, bins = n_bins, density= True, rwidth= 0.9)
    plt.ylabel("frequency")
    plt.xlabel("Range")
    plt.title("Unweighted distribution with two step flight")
    plt.show()
 

def plot_hist_two_trip_weights(lim, n_bins=9): 
    pass
    corr_bins = [] # corrected bins - initialize which will contain classes
    
    direct_flights = df_trips[df_trips[:,1] < lim]
    two_step_flights = two_trip_analysis(lim)
    total_flights = np.append(direct_flights, two_step_flights, axis= 0) # array - example ['Paris-Dortmund', 470.1237855871516, 'Par-Dor-dir', 910.4]
    hist_data = total_flights[:,1].astype("float64")
    df_sum_gdp = np.sum(total_flights[:,3].astype("float64"))
    hist_freq, bin_edges = np.histogram(hist_data, bins= n_bins)
    
    for idx, i in enumerate(bin_edges):
        if bin_edges[idx] == bin_edges[-1]:
            continue
        state_edges = [i, bin_edges[idx + 1]]
        state_freq = hist_freq[idx]
        state_bin = Bin(state_freq, state_edges, total_flights, df_sum_gdp) # Use created class to do computations on the bins 
        corr_bins.append(state_bin)
    counts = [i.bin_expectation() for i in corr_bins]
    plt.hist(bin_edges[:-1], bin_edges, weights= counts, density= True, rwidth= 0.9)
    plt.ylabel("frequency")
    plt.xlabel("Range")
    plt.title("Weighted distribution with two step flight")
    plt.show()
 

            
            
if __name__ == "__main__":
    plot_hist_two_trip_weightless(500, n_bins=9)
    plot_hist_two_trip_weights(500, n_bins=9)







