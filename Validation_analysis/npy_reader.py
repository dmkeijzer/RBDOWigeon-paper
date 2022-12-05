import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import sys
import pathlib as pl
print(os.path.join(os.path.dirname(os.path.dirname(__file__)), "Final_optimization"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "Final_optimization"))
import rv_handler as rv

class npz_tool: #TODO come up with better names lol
    """_summary_
    """
    def __init__(self, file_path):
    
        df_arr = np.load(os.path.realpath(file_path), allow_pickle= True)
        df = pd.DataFrame(df_arr[1:])
        df.columns = df_arr[0,:]
    
   
        self.df = df
        self.conv_lst = df["Converged_des"]
        self.final_energy = self.df["Energy"][self.conv_lst].to_numpy()[-1]/3.6e6

    def energy_convergence(self, converged= True):
        energy_data = np.array(self.df["Energy"][self.conv_lst])/3.6e6 if converged else np.array(self.df["Energy"])/3.6e6
        plt.plot(energy_data, "vk-.")
        plt.xlabel(r"$n_{th}$ Converged design") if converged else plt.xlabel(r"$n_{th}$ iteration")
        plt.ylabel("Energy [Kwh]")
        plt.show()
    
    def pie_chart_energy(self):
        plot_data = np.array(self.df["Energy_dist"][self.conv_lst])[-1]
        phases = ["Cruise", "Climb", "Descend", "Loiter cruise", "Loiter Hover"]
        plt.pie(plot_data, labels = phases, autopct = '%1.1f%%', explode= [0.1,0,0,0.2,0.2])
        plt.show()

    def energy_pdf_cdf_plot(self, n= -1):

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
    
    def analyze_all(self):

        self.energy_convergence(converged=False)
        self.energy_convergence()
        self.pie_chart_energy()
        self.energy_pdf_cdf_plot()
                   
if __name__ == "__main__":
        
    Analysis_tool = npz_tool(r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\Monte_carlo_Nov_29_20.56_2022.npy")
    print(Analysis_tool.df.head(20))
    # print(Analysis_tool.analyze_all())
    dummy = None

