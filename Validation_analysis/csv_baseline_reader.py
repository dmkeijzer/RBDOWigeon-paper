import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


file_path = r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\valid_data\Baseline\Deterministic_Jun__1_22.00_hist.csv"
download_path = os.path.join(os.path.expanduser("~"), "Downloads")


data_csv = pd.read_csv(file_path)
print(data_csv.columns)
conv_lst = np.array(np.round(data_csv["converged"],0), dtype= bool)


def plot_design_params(save_bool):


    fig, axs = plt.subplots(2,3)
    fig.suptitle("Deterministic Mission")
    fig.set_figheight(8)
    fig.set_figwidth(15)
    #MTOM
    y1 = data_csv["MTOM"][conv_lst].to_numpy()
    axs[0, 0].plot(y1, label= "MTOM")
    axs[0, 0].legend()
    axs[0, 0].set_xlabel(r"$n_{th}$ Converged design")
    axs[0, 0].set_ylabel('MTOM [kg]')
    axs[0, 0].grid()

    # Aspect ratio's
    y2 = data_csv["AR1"][conv_lst].to_numpy()
    y3 = data_csv["AR2"][conv_lst].to_numpy()
    axs[0, 1].plot(y2, label= "AR front")
    axs[0, 1].plot(y3, label= "AR rear")
    axs[0, 1].set_xlabel(r"$n_{th}$ Converged design")
    axs[0, 1].set_ylabel("AR [-]")
    axs[0, 1].legend()
    axs[0, 1].grid()

    # Cm alpha
    # y4 = data_csv["Cm_alpha"][conv_lst].to_numpy()
    # axs[0, 2].plot(y4, label=r'$C_{m_{\alpha}}$' )
    # axs[0, 2].set_xlabel(r"$n_{th}$ Converged design")
    # axs[0, 2].set_ylabel(r'$C_{m_{\alpha}}$')
    # axs[0, 2].legend()

    # CLmax
    # y5 = data_csv["CLmax"][conv_lst].to_numpy()
    # axs[1, 0].plot(y5, label=r'$C_{Lmax}$ [-]')
    # axs[1, 0].set_xlabel(r"$n_{th}$ Converged design")
    # axs[1, 0].set_ylabel(r'$C_{Lmax}$ [-]')
    # axs[1, 0].grid()
    # axs[1, 0].legend()

    # Spans
    y2 = data_csv["span1"][conv_lst].to_numpy()
    y3 = data_csv["span2"][conv_lst].to_numpy()
    axs[1, 0].plot(y2, label= "Span front")
    axs[1, 0].plot(y3, label= "Span rear")
    axs[1, 0].set_xlabel(r"$n_{th}$ Converged design")
    axs[1, 0].set_ylabel("Span [m]")
    axs[1, 0].legend()
    axs[1, 0].grid()

    # Wing ratio
    y6 = data_csv["S2"][conv_lst].to_numpy()/data_csv["S1"][conv_lst].to_numpy()
    axs[1, 1].plot(y6,label=r'$\frac{S_{rear}}{S_{front}}$')
    axs[1, 1].set_xlabel(r"$n_{th}$ Converged design")
    axs[1, 1].set_ylabel(r'$\frac{S_{rear}}{S_{front}}$[-]', fontsize = 14, alpha = 0.8)
    axs[1, 1].legend(fontsize = 14)
    axs[1, 1].grid()

    # S total
    y7 = data_csv["S1"][conv_lst].to_numpy()  
    y8 = data_csv["S2"][conv_lst].to_numpy()
    axs[1, 2].plot(y7, label= r"$S_{front}$")
    axs[1, 2].plot(y8, label= r"$S_{rear}$")
    axs[1, 2].set_xlabel(r"$n_{th}$ Converged design")
    axs[1, 2].set_ylabel(r'S [$m^2$]')
    axs[1, 2].legend()
    axs[1, 2].grid()

    # Control margin
    y9 = data_csv["Energy"][conv_lst].to_numpy()
    axs[0, 2].plot(y9/3.6e6,label=r'Mission Energy')
    axs[0, 2].set_xlabel(r"$n_{th}$ Converged design")
    axs[0, 2].set_ylabel(r'Energy [kWh]')
    axs[0, 2].grid()
    axs[0, 2].legend()

    fig.tight_layout()
    if save_bool:
        plt.savefig(os.path.join(download_path, os.path.split(file_path)[-1][:-4]) + "_DesignParam_" +  ".pdf", bbox_inches= "tight")
    else:
        plt.show()

def plot_energy_phases(save_bool):

    energy = data_csv["Energy"][conv_lst].to_numpy()
    Ecruise = data_csv["E_cruise"][conv_lst].to_numpy()
    Eclimb = data_csv["E_climb"][conv_lst].to_numpy()
    Edesc = data_csv["E_desc"][conv_lst].to_numpy()
    Eloit = data_csv["E_loiter"][conv_lst].to_numpy() # mission independent all samples have the same value

    fig, axs = plt.subplots(3,2)
    fig.suptitle("Deterministic Mission")
    fig.set_figheight(10)
    fig.set_figwidth(10)

    axs[0,0].plot(energy/3.6e6)
    axs[0, 0].set_xlabel(r"$n_{th}$ Converged design")
    axs[0,0].set_ylabel("Total Energy [kWh]")
    axs[0,0].grid(lw=0.8, alpha=0.8)
    axs[0,0].set_xlim([0,60])

    axs[0,1].plot(Ecruise/3.6e6)
    axs[0, 1].set_xlabel(r"$n_{th}$ Converged design")
    axs[0,1].set_ylabel("Cruise Energy [kWh]")
    axs[0,1].grid(lw=0.8, alpha=0.8)
    axs[0,1].set_xlim([0,60])

    axs[1,0].plot(Eclimb/3.6e6)
    axs[1, 0].set_xlabel(r"$n_{th}$ Converged design")
    axs[1,0].set_ylabel("Climb Energy [kWh]")
    axs[1,0].grid(lw=0.8, alpha=0.8)
    axs[1,0].set_xlim([0,60])

    axs[1,1].plot(Eloit/3.6e6)
    axs[1, 1].set_xlabel(r"$n_{th}$ Converged design")
    axs[1,1].set_ylabel("Loiter Energy [kWh]")
    axs[1,1].grid(lw=0.8, alpha=0.8)
    axs[1,1].set_xlim([0,60])

    axs[2,1].plot(Edesc/3.6e6)
    axs[2, 1].set_xlabel(r"$n_{th}$ Converged design")
    axs[2,1].set_ylabel("Descend Energy [kWh]")
    axs[2,1].grid(lw=0.8, alpha=0.8)
    axs[2,1].set_xlim([0,60])

    fig.suptitle("Determinstic Mission")
    fig.tight_layout()
    if save_bool:
        plt.savefig(os.path.join(download_path, os.path.split(file_path)[-1][:-4]) + "_EnergyPhases_" +  ".pdf", bbox_inches= "tight")
    else:
        plt.show()

plot_design_params(True)
plot_energy_phases(True)
