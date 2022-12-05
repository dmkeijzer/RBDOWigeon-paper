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
        df = pd.DataFrame(df_arr["array1"][1:])
        df.columns = df_arr["array1"][0,:]
    
   
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

    def plot_performance(self):
        energy_rv = self.df["Energy_rv"].to_numpy()[-1]
        time_rv = self.df["time_rv"].to_numpy()[-1]
        power_rv = self.df["power_rv"].to_numpy()[-1]
        thrust_rv = self.df["thrust_rv"].to_numpy()[-1] # mission independent all samples have the same value
        time_cruise_rv = self.df["time_cruise_rv"].to_numpy()[-1]


        fig, axs = plt.subplots(2,2)
        x1 = np.linspace(0, np.max(energy_rv.data), 1000)
        axs[0,0].plot(x1, energy_rv.best_fit.pdf(x1, loc= energy_rv.loc, scale= energy_rv.scale, *energy_rv.arg))
        axs[0,0].set_title("Energy")
        x2 = np.linspace(0, np.max(time_rv.data), 1000)
        axs[0,1].plot(x2, time_rv.best_fit.pdf(x2, loc= time_rv.loc, scale= time_rv.scale, *time_rv.arg))
        axs[0,1].set_title("Time")
        x3 = np.linspace(np.min(power_rv.data), np.max(power_rv.data), 1000)
        axs[1,0].plot(x3, power_rv.best_fit.pdf(x3, loc= power_rv.loc, scale= power_rv.scale, *power_rv.arg))
        axs[1,0].set_title("Power")
        # x4 = np.linspace(np.min(thrust_rv.data), np.max(thrust_rv.data), 1000)
        # axs[1,1].plot(x4, thrust_rv.best_fit.pdf(x4, loc= thrust_rv.loc, scale= thrust_rv.scale, *thrust_rv.arg))
        # axs[1,1].set_title("Thrust")
        x5 = np.linspace(0, np.max(time_cruise_rv.data), 1000)
        axs[1,1].plot(x5, time_cruise_rv.best_fit.pdf(x5, loc= time_cruise_rv.loc, scale= time_cruise_rv.scale, *time_cruise_rv.arg))
        axs[1,1].set_title("time_cruise")
        plt.show()
                   

    def energy_phases(self):
        Ecruise_rv = self.df["Ecruise_rv"].to_numpy()[-1]
        Eclimb_rv = self.df["Eclimb_rv"].to_numpy()[-1]
        Edesc_rv = self.df["Edesc_rv"].to_numpy()[-1]
        Eloit_cr_rv = self.df["Eloit_cr_rv"].to_numpy()[-1] # mission independent all samples have the same value
        Eloit_hov_rv = self.df["Eloit_hov_rv"].to_numpy()[-1]


        fig, axs = plt.subplots(3,2)
        x1 = np.linspace(np.min(Ecruise_rv.data), np.max(Ecruise_rv.data), 1000)
        axs[0,0].plot(x1/3.6e6, Ecruise_rv.best_fit.pdf(x1, loc= Ecruise_rv.loc, scale= Ecruise_rv.scale, *Ecruise_rv.arg))
        axs[0,0].set_title("Cruise")
        x2 = np.linspace(np.min(Eclimb_rv.data), np.max(Eclimb_rv.data), 1000)
        axs[0,1].plot(x2/3.6e6, Eclimb_rv.best_fit.pdf(x2, loc= Eclimb_rv.loc, scale= Eclimb_rv.scale, *Eclimb_rv.arg))
        axs[0,1].set_title("Climb")
        x3 = np.linspace(np.min(Edesc_rv.data), np.max(Edesc_rv.data), 1000)
        axs[1,0].plot(x3/3.6e6, Edesc_rv.best_fit.pdf(x3, loc= Edesc_rv.loc, scale= Edesc_rv.scale, *Edesc_rv.arg))
        axs[1,0].set_title("Descend")
        x4 = np.linspace(0, np.max(Eloit_cr_rv.data), 1000)
        axs[1,1].plot(x4/3.6e6, Eloit_cr_rv.best_fit.pdf(x4, loc= Eloit_cr_rv.loc, scale= Eloit_cr_rv.scale, *Eloit_cr_rv.arg))
        axs[1,1].set_title("Loiter cruise conf")
        x5 = np.linspace(np.min(Eloit_hov_rv.data), np.max(Eloit_hov_rv.data), 1000)
        axs[2,0].plot(x5/3.6e6, Eloit_hov_rv.best_fit.pdf(x5, loc= Eloit_hov_rv.loc, scale= Eloit_hov_rv.scale, *Eloit_hov_rv.arg))
        axs[2,0].set_title("Loiter hover conf")
        plt.show()
if __name__ == "__main__":
        
    Analysis_tool = npz_tool(r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\Monte_carlo_Nov_29_22.07_2022.npz")
    print(Analysis_tool.df.columns)
    # test_tool = npz_tool(r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\Monte_carlo_Nov_24_10.23_2022.npz")
    Analysis_tool.energy_convergence()
    Analysis_tool.plot_performance()
    Analysis_tool.energy_phases()
    dummy = None

