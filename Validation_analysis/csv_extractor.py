from cProfile import label
from time import time_ns
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import sys
import pathlib as pl
import re

class npz_tool: #TODO come up with better names lol
    """_summary_
    """
    def __init__(self, version, time_stamp):
        self.version = version
        self.mont_carl = version[:2].lower() == "mo"
        self.time_stamp = time_stamp
        self.ml_path =  list(pl.Path(__file__).parents)[2] / "logs" / "valid_data" / "Monte_Carlo"  #Monte Carlo path
        self.bl_path =  list(pl.Path(__file__).parents)[2] / "logs" / "valid_data" / "Baseline"  #Monte Carlo path
        
        if version[:2].lower() == "mo":
            folder_lst = os.listdir(self.ml_path)

            for folder in folder_lst:
                if str(time_stamp).replace(":",".") in folder:
                    file_lst = os.listdir(os.path.join(self.ml_path, folder))
                    folder_loc = folder
                    break
            try:
                for file in file_lst:
                    if "npz" in file:  
                        df_arr = np.load(os.path.join(self.ml_path, folder_loc, file), allow_pickle= True)
                        df = pd.DataFrame(df_arr["array1"][1:])
                        df.columns = df_arr["array1"][0,:]
            except UnboundLocalError:
                raise Exception(f"Could not find timestamp = {time_stamp}")
        
        elif version[:2].lower() == "ba":
            folder_lst = os.listdir(self.bl_path)

            for folder in folder_lst:
                if str(time_stamp).replace(":",".") in folder:
                    file_lst = os.listdir(os.path.join(self.bl_path, folder))
                    folder_loc = folder
                    break
            try:
                for file in file_lst:
                    if "csv" in file:  
                        df_output = pd.read_csv(os.path.join(self.bl_path, folder_loc, file))
            except UnboundLocalError:
                raise Exception(f"Could not find timestamp = {time_stamp}")
            
        else:
            raise OSError(f"Please choose correct folder either baseline or Monte Carlo")
   
        self.df = df
        self.conv_lst = df["Converged_des"]
        self.final_energy = self.df["Energy"][self.conv_lst].to_numpy()[-1]/3.6e6

    def energy_convergence(self, converged= True):
        if self.mont_carl:
            energy_data = np.array(self.df["Energy"][self.conv_lst])/3.6e6 if converged else np.array(self.df["Energy"])
        else:
            pass
        plt.plot(energy_data, "vk-.")
        plt.xlabel(r"$n_{th}$ Converged design") if converged else plt.xlabel(r"$n_{th}$ iteration")
        plt.ylabel("Energy [Kwh]")
        plt.show()
    
    def pie_chart_energy(self):
        plot_data = np.array(self.df["Energy_dist"][self.conv_lst])[-1]
        phases = ["Cruise", "Climb", "Descend", "Loiter cruise", "Loiter Hover"]
        plt.pie(plot_data, labels = phases, autopct = '%1.1f%%', explode= [0.1,0,0,0.2,0.2])
        plt.show()

    def pdf_cdf_plot(self, n= -1):

        dist = self.df["dist_type"][self.conv_lst].to_numpy()[n]
        params = self.df["params_dist"][self.conv_lst].to_numpy()[n]
        arg = params[:-2]
        loc = params[-2]
        scale = params[-1]
        x = np.linspace(0, np.max(self.df["Summary_energy"][self.conv_lst].to_numpy()[n]) ,  100000)

        pdf = dist.pdf(x, loc= loc, scale= scale, *arg)
        cdf = dist.cdf(x, loc= loc, scale= scale, *arg)

        plt.clf()
        plt.plot(x/3.6e6, pdf, "k-.", label= "pdf")
        plt.xlabel("Energy")
        plt.ylabel("PDF")
        plt.legend()
        plt.twinx()
        plt.plot(x/3.6e6, cdf, "k-", label= "cdf")
        plt.legend()
        plt.ylabel("CDF")
        plt.show()
                   
if __name__ == "__main__":
        
    Analysis_tool = npz_tool("mont", "17.47")
    print(Analysis_tool.final_energy)
    print(Analysis_tool.pdf_cdf_plot())

