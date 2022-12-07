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
        # thrust_rv = self.df["thrust_rv"].to_numpy()[-1] # mission independent all samples have the same value
        time_cruise_rv = self.df["time_cruise_rv"].to_numpy()[-1]


        fig, axs = plt.subplots(2,2)
        x1, pdf1, cdf1 = energy_rv.plt()  
        axs[0,0].plot(x1/3.6e6, pdf1, "k-", label = "Energy")
        axs[0,0].set_ylabel("PDF [-]")
        axs[0,0].set_xlabel("Energy [Kwh]")
        axs[0,0].legend()

        x2, pdf2, cdf2 = time_rv.plt()  
        axs[0,1].plot(x2, pdf2, "k-", label = "Time")
        axs[0,1].set_ylabel("PDF [-]")
        axs[0,1].set_xlabel("Time [s]")
        axs[0,1].legend()

        x3, pdf3, cdf3 = power_rv.plt()
        axs[1,0].plot(x3/1000, pdf3,"k-", label = "Power")
        axs[1,0].set_xlabel("Power [Kw]")
        axs[1,0].set_ylabel("PDF [-]")
        axs[1,0].legend()

        # x4, pdf4, cdf4 = thrust_rv.plt()
        # axs[1,1].plot(x4/1000, pdf4,"k-", label = "Thrust")
        # axs[1,1].set_xlabel("kN")
        # axs[1,1].set_ylabel("PDF [-]")
        # axs[1,1].legend()

        x5, pdf5, cdf5 = time_cruise_rv.plt()
        axs[1,1].plot(x5, pdf5,"k-", label = "Time cruise")
        axs[1,1].set_xlabel("Time [s]")
        axs[1,1].set_ylabel("PDF [-]")
        axs[1,1].legend()
        plt.show()
                   

    def energy_phases(self):
        Ecruise_rv = self.df["Ecruise_rv"].to_numpy()[-1]
        Eclimb_rv = self.df["Eclimb_rv"].to_numpy()[-1]
        Edesc_rv = self.df["Edesc_rv"].to_numpy()[-1]
        Eloit_cr_rv = self.df["Eloit_cr_rv"].to_numpy()[-1] # mission independent all samples have the same value
        Eloit_hov_rv = self.df["Eloit_hov_rv"].to_numpy()[-1]


        fig, axs = plt.subplots(3,2)
        x1, pdf1, cdf1 = Ecruise_rv.plt()  
        axs[0,0].plot(x1/3.6e6, pdf1)
        axs[0,0].set_title("Cruise")
        x2, pdf2, cdf2 = Eclimb_rv.plt()  
        axs[0,1].plot(x2/3.6e6, pdf2)
        axs[0,1].set_title("Climb")
        x3, pdf3, cdf3 = Edesc_rv.plt()
        axs[1,0].plot(x3/3.6e6, pdf3)
        axs[1,0].set_title("Descend")
        x4, pdf4, cdf4 = Eloit_cr_rv.plt()
        axs[1,1].plot(x4/3.6e6, pdf4)
        axs[1,1].set_title("Loiter cruise conf")
        x5, pdf5, cdf5 = Eloit_hov_rv.plt()
        axs[2,0].plot(x5/3.6e6, pdf5)
        axs[2,0].set_title("Loiter hover conf")
        plt.show()
if __name__ == "__main__":
        
    Analysis_tool = npz_tool(r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\Monte_carlo_Dec_6_13.21_2022.npz")
    print(Analysis_tool.df.columns)
    print([i.best_fit for i in Analysis_tool.df["power_rv"]])
    # test_tool = npz_tool(r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\Monte_carlo_Nov_24_10.23_2022.npz")
    Analysis_tool.energy_convergence()
    Analysis_tool.plot_performance()
    dummy = None

