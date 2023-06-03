import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import re
import sys
import pathlib as pl
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "Final_optimization"))
import rv_handler as rv

class npz_tool: #TODO come up with better names lol
    """_summary_
    """
    def __init__(self, file_path, save_bool):
        """This class turns the npz output of the file Optimization.py into a usable datatype which some standard methods and gives easy access to each column by the main data 
        object into a Pandas.Dataframe. For the standard methods please see further documentation.

        :param file_path: The path (relative or absolute) to the npz output
        :type file_path: string
        """        
    
        df_arr = np.load(os.path.realpath(file_path), allow_pickle= True)
        df = pd.DataFrame(df_arr["array1"][1:])
        df.columns = df_arr["array1"][0,:]
    
   
        self.df = df
        self.save_bool = save_bool
        self.file_path = file_path
        self.conv_lst = df["Converged_des"]
        self.final_energy = self.df["Energy"][self.conv_lst].to_numpy()[-1]/3.6e6
        # match = re.search(r'(\w{3}_\d{1,2}_\d{2}\.\d{2})_(\d{4})', os.path.split(file_path)[-1])
        self.id =  os.path.split(self.file_path)[-1][:-4]
        self.title = "MCS Based Mission"
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")



    def energy_convergence(self, converged= True):

        energy_data = np.array(self.df["Energy"][self.conv_lst])/3.6e6 if converged else np.array(self.df["Energy"])/3.6e6
        plt.plot(energy_data, "vk-.")
        plt.xlabel(r"$n_{th}$ Converged design") if converged else plt.xlabel(r"$n_{th}$ iteration")
        plt.ylabel("Energy [Kwh]")
        plt.suptitle(self.title)
        if self.save_bool:
            plt.savefig(os.path.join(self.download_path, self.id) + "_EnergyConv_" +  ".pdf", bbox_inches= "tight")
        else:
            plt.show()
    
    def pie_chart_energy(self):
        plot_data = np.array(self.df["Energy_dist"][self.conv_lst])[-1]
        phases = ["Cruise", "Climb", "Descend", "Loiter cruise", "Loiter Hover"]
        plt.pie(plot_data, labels = phases, autopct = '%1.1f%%', explode= [0.1,0,0,0.2,0.2])
        plt.suptitle(self.title)
        if self.save_bool:
            plt.savefig(os.path.join(self.download_path, self.id) + "_PieChart_" +  ".pdf", bbox_inches= "tight")
        else:
            plt.show()

    def energy_pdf_cdf_plot(self, n= -1):

        dist = self.df["Energy_rv"][self.conv_lst].to_numpy()[n]
        x, pdf, cdf = dist.plt()

        plt.clf()
        plt.plot(x/3.6e6, pdf*3.6e6, "k-.", label= "pdf")
        plt.xlabel("Energy [KwH]")
        plt.ylabel("PDF")
        plt.legend()
        plt.twinx()
        plt.plot(x/3.6e6, cdf, "k-", label= "cdf")
        plt.legend()
        plt.ylabel("CDF")
        plt.suptitle(self.title)
        if self.save_bool:
            plt.savefig(os.path.join(self.download_path, self.id) + "_PdfCdf_" +  ".pdf", bbox_inches= "tight")
        else:
            plt.show()
    

    def plot_performance(self):

        energy_rv = self.df["Energy_rv"].to_numpy()[-1]
        time_rv = self.df["time_rv"].to_numpy()[-1]
        power_rv = self.df["power_rv"].to_numpy()[-1]
        # thrust_rv = self.df["thrust_rv"].to_numpy()[-1] # mission independent all samples have the same value
        time_cruise_rv = self.df["time_cruise_rv"].to_numpy()[-1]


        fig, axs = plt.subplots(2,2)
        x1, pdf1, cdf1 = energy_rv.plt()  
        axs[0,0].plot(x1/3.6e6, pdf1*3.6e6, "k-", label = "Total energy")
        axs[0,0].set_ylabel("PDF [-]")
        axs[0,0].set_xlabel("Energy [Kwh]")
        axs[0,0].legend()

        x2, pdf2, cdf2 = time_rv.plt()  
        axs[0,1].plot(x2, pdf2, "k-", label = "Time")
        axs[0,1].set_ylabel("PDF [-]")
        axs[0,1].set_xlabel("Time [s]")
        axs[0,1].legend()

        x3, pdf3, cdf3 = power_rv.plt()
        axs[1,0].plot(x3/1000, pdf3*1000,"k-", label = "Power")
        axs[1,0].set_xlabel("Power [Kw]")
        axs[1,0].set_ylabel("PDF [-]")
        axs[1,0].legend()

        x5, pdf5, cdf5 = time_cruise_rv.plt()
        axs[1,1].plot(x5, pdf5,"k-", label = "Time cruise")
        axs[1,1].set_xlabel("Time [s]")
        axs[1,1].set_ylabel("PDF [-]")
        axs[1,1].legend()

        fig.suptitle(self.title)
                   
        if self.save_bool:
            plt.savefig(os.path.join(self.download_path, self.id) + "_Perf_" +  ".pdf", bbox_inches= "tight")
        else:
            plt.show()

    def energy_phases(self):
        energy_rv = self.df["Energy_rv"].to_numpy()[-1]
        Ecruise_rv = self.df["Ecruise_rv"].to_numpy()[-1]
        Eclimb_rv = self.df["Eclimb_rv"].to_numpy()[-1]
        Edesc_rv = self.df["Edesc_rv"].to_numpy()[-1]
        Eloit_cr_rv = self.df["Eloit_cr_rv"].to_numpy()[-1] # mission independent all samples have the same value
        Eloit_hov_rv = self.df["Eloit_hov_rv"].to_numpy()[-1]

        fig, axs = plt.subplots(3,2)
        fig.suptitle(self.title)
        fig.set_figheight(8)
        fig.set_figwidth(15)

        x1, pdf1, cdf1 = Ecruise_rv.plt()  
        axs[0,0].plot(x1/3.6e6, pdf1*3.6e6, color="k")
        axs[0,0].set_title("Cruise")
        axs[0,0].set_xlabel("Energy [KwH]")
        axs[0,0].set_ylabel("PDF [-]")
        axs[0,0].grid(lw=0.8, alpha=0.8)

        x2, pdf2, cdf2 = Eclimb_rv.plt()  
        axs[0,1].plot(x2/3.6e6, pdf2*3.6e6, color="k")
        axs[0,1].set_title("Climb")
        axs[0,1].set_xlabel("Energy [KwH]")
        axs[0,1].set_ylabel("PDF [-]")
        axs[0,1].grid(lw=0.8, alpha=0.8)

        x3, pdf3, cdf3 = Edesc_rv.plt()
        axs[1,0].plot(x3/3.6e6, pdf3*3.6e6, color="k")
        axs[1,0].set_title("Descend")
        axs[1,0].set_xlabel("Energy [KwH]")
        axs[1,0].set_ylabel("PDF [-]")
        axs[1,0].grid(lw=0.8, alpha=0.8)

        hist, bin_edges = Eloit_cr_rv.data
        bin_edges = bin_edges/3.6e6
        tot_area = np.sum(hist*np.diff(bin_edges))
        hist = [(hist[idx]*width)/(tot_area) for idx, width in enumerate(np.diff(bin_edges))]
        if not np.isclose(np.sum(hist),1):
            raise Exception("The density computation of the histogram has failed")

        # axs[1,1].vlines(bin_edges[:-1], np.zeros(np.size(bin_edges) - 1), hist, "k")
        axs[1,1].stairs(hist, bin_edges/3.6e6, fill= True, color= "lightgray", edgecolor ="k", lw= 2)
        axs[1,1].set_title("Loiter cruise conf")
        axs[1,1].set_xlabel("Energy [KwH]")
        axs[1,1].set_ylabel("[-]")
        axs[1,1].grid(lw=0.8, alpha=0.8)

        hist, edges, patches = axs[2,0].hist(Eloit_hov_rv.data/3.6e6, density= True, lw= 2, rwidth = 0.85, color= "lightgray", edgecolor="k")
        axs[2,0].set_ylim([0,1.1*np.max(hist[1:])])
        axs[2,0].set_title("Loiter hover conf")
        axs[2,0].set_xlabel("Energy [KwH]")
        axs[2,0].set_ylabel("[-]")
        axs[2,0].grid(lw=0.8, alpha=0.8)

        x4, pdf4, cdf4 = energy_rv.plt()  
        axs[2,1].plot(x1/3.6e6, pdf1*3.6e6, "k-", label = "Total energy")
        axs[2,1].set_ylabel("PDF [-]")
        axs[2,1].set_xlabel("Energy [Kwh]")
        axs[2,1].grid(lw=0.8, alpha=0.8)
        axs[2,1].legend()

        fig.suptitle(self.title)
        fig.tight_layout()
        if self.save_bool:
            plt.savefig(os.path.join(self.download_path, self.id) + "_EnergyPhases_" +  ".pdf", bbox_inches= "tight")
        else:
            plt.show()
    
    def design_parameter(self):

        fig, axs = plt.subplots(2,3)
        fig.set_figheight(8)
        fig.set_figwidth(15)

        #MTOM
        y1 = self.df["MTOM"][self.conv_lst].to_numpy()
        axs[0, 0].plot(y1, label= "MTOM")
        axs[0, 0].legend()
        axs[0, 0].set_xlabel(r"$n_{th}$ Converged design")
        axs[0, 0].set_ylabel('MTOM [kg]')
        axs[0, 0].grid()

        # Aspect ratio's
        y2 = self.df["AR1"][self.conv_lst].to_numpy()
        y3 = self.df["AR2"][self.conv_lst].to_numpy()
        axs[0, 1].plot(y2, label= "AR front")
        axs[0, 1].plot(y3, label= "AR rear")
        axs[0, 1].set_xlabel(r"$n_{th}$ Converged design")
        axs[0, 1].set_ylabel("AR [-]")
        axs[0, 1].legend()
        axs[0, 1].grid()

        # Energy
        y4 = self.df["Energy"][self.conv_lst].to_numpy()
        axs[0, 2].plot(y4/3.6e6, label=r'Energy' )
        axs[0, 2].set_xlabel(r"$n_{th}$ Converged design")
        axs[0, 2].set_ylabel(r'Energy [kWh]')
        axs[0, 2].legend()
        axs[0, 2].grid()

        # CLmax
        # y5 = self.df["CLmax"][self.conv_lst].to_numpy()
        # axs[1, 0].plot(y5, label=r'$C_{Lmax}$ [-]')
        # axs[1, 0].set_xlabel(r"$n_{th}$ Converged design")
        # axs[1, 0].set_ylabel(r'$C_{Lmax}$ [-]')
        # axs[1, 0].legend()
        # axs[1, 0].grid()

        # Spans
        y2 = self.df["span1"][self.conv_lst].to_numpy()
        y3 = self.df["span2"][self.conv_lst].to_numpy()
        axs[1, 0].plot(y2, label= "Span front")
        axs[1, 0].plot(y3, label= "Span rear")
        axs[1, 0].set_xlabel(r"$n_{th}$ Converged design")
        axs[1, 0].set_ylabel("Span [m]")
        axs[1, 0].legend()
        axs[1, 0].grid()

        # Control margin
        # y6 = self.df["Cm_alpha"][self.conv_lst].to_numpy()
        # axs[1, 1].plot(y6,label=r'$c_{m_{\alpha}}$')
        # axs[1, 1].set_xlabel(r"$n_{th}$ Converged design")
        # axs[1, 1].set_ylabel(r'$c_{m_{\alpha}}$ [-]')
        # axs[1, 1].legend()
        # axs[1, 1].grid()

        # Wing ratio
        y6 = self.df["S2"][self.conv_lst].to_numpy()/self.df["S1"][self.conv_lst].to_numpy()
        axs[1, 1].plot(y6,label=r'$\frac{S_{rear}}{S_{front}}$')
        axs[1, 1].set_xlabel(r"$n_{th}$ Converged design")
        axs[1, 1].set_ylabel(r'$\frac{S_{rear}}{S_{front}}$[-]', fontsize = 14, alpha = 0.8)
        axs[1, 1].legend(fontsize = 14)
        axs[1, 1].grid()

        # S total
        y7 = self.df["S1"][self.conv_lst].to_numpy()  
        y8 = self.df["S2"][self.conv_lst].to_numpy()
        axs[1, 2].plot(y7, label= r"$S_{front}$")
        axs[1, 2].plot(y8, label= r"$S_{rear}$")
        axs[1, 2].set_xlabel(r"$n_{th}$ Converged design")
        axs[1, 2].set_ylabel(r'S [$m^2$]')
        axs[1, 2].legend()
        axs[1, 2].grid()

        fig.suptitle(self.title)
        fig.tight_layout()
        if self.save_bool:
            plt.savefig(os.path.join(self.download_path, self.id) + "_DesignParams_" +  ".pdf", bbox_inches= "tight")
        else:
            plt.show()


        pass

    def analyze_all(self):

        self.energy_convergence(converged=False)
        self.energy_convergence()
        self.design_parameter()
        self.pie_chart_energy()
        self.energy_pdf_cdf_plot()
        self.plot_performance()
        self.energy_phases()

if __name__ == "__main__":

    runs = os.listdir(r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\valid_data\Monte_Carlo")

    npz_lst = []

    for i in runs:
        path = os.path.join(r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\valid_data\Monte_Carlo", i)
        for file in os.listdir(path):
            if "npz" in file:
                npz_lst.append(os.path.join(path, file))

        
    print(f"file = {npz_lst[-1]}")
    Analysis_tool = npz_tool(npz_lst[-1], True)
    Analysis_tool.analyze_all()
    print(Analysis_tool.df.columns)