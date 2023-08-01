
import sys
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pathlib as pl
import numpy as np
import yaml 

sys.path.append(str(list(pl.Path(__file__).parents)[2]))


from modules.plotting.MCS_metric_deterministic_reader import determinisic_energy_pdf_cdf_plot
from modules.plotting.npz_reader import npz_tool
from modules.plotting.weight_computation import Wing, Fuselage, LandingGear

os.chdir(str(list(pl.Path(__file__).parents)[2]))

def plot_pdf_cdf():

    with open(os.path.realpath(r'input\environment_variables_plotting.yml'), 'r') as yamlfile:
        data = yaml.safe_load(yamlfile)

    dir_path = data["baseline"]["dir"]
    label_mcs = os.path.split(data["mcs"]["dir"])[-1][3:]
    label_deter = os.path.split(data["baseline"]["dir"])[-1][3:]
    
    # Create storage location for data from mcs metrci
    if os.path.exists(os.path.join(dir_path, "plots")):
        pass
    else:
        os.mkdir(os.path.join(dir_path, 'plots'))

    dump_path = os.path.join(os.path.join(dir_path , "plots", "compare_baseline_mcs" + label_mcs))


    npz_reader = npz_tool( save_bool= False)
    data_csv = pd.read_csv(os.path.join(dir_path, "Deterministic" + label_deter + "_hist.csv"))
    conv_lst = np.array(np.round(data_csv["converged"],0), dtype= bool)

    x_deter, pdf_deter, cdf_deter = determinisic_energy_pdf_cdf_plot(False, return_data= True)
    x_mcs, pdf_mcs, cdf_mcs, dist= npz_reader.energy_pdf_cdf_plot(return_data=True)

    sns.set(style="white")

    plt.clf()
    plt.figure(figsize=(10,6))
    plt.plot(x_deter/3.6e6, pdf_deter, "-.", label= "PDF Deterministic Design")
    plt.vlines([data_csv["Energy"][conv_lst].to_numpy()[-1]/3.6e6], 0, pdf_deter[np.argmin(np.abs(x_deter - data_csv["Energy"][conv_lst].to_numpy()[-1]))], color="red", alpha=0.3)
    plt.fill_between(x_deter/3.6e6, pdf_deter, np.zeros(np.size(x_deter)), where= (x_deter > data_csv["Energy"][conv_lst].to_numpy()[-1]), color='red', alpha=0.3)
    plt.plot(x_mcs/3.6e6, pdf_mcs, "-", color="C1", label= "PDF MCS Design ")
    plt.vlines([dist.ppf(0.9)/3.6e6], 0, pdf_mcs[np.argmin(np.abs(x_mcs - dist.ppf(0.9)))], color="red", alpha=0.3)
    plt.fill_between(x_mcs/3.6e6, pdf_mcs, np.zeros(np.size(x_mcs)), where= (x_mcs > dist.ppf(0.9)), color='red', alpha=0.3)
    plt.xlabel("Energy [KwH]")
    plt.ylabel("PDF [-]")
    plt.grid(lw= 0.8, alpha= 0.8)
    plt.legend()
    # plt.suptitle("MCS vs Deterministic")

    plt.savefig(dump_path + "_Pdf_" +  ".pdf", bbox_inches= "tight")

    plt.clf()
    plt.figure(figsize=(10,6))
    plt.plot(x_deter/3.6e6, cdf_deter, "-.", label= "CDF Deterministic Design")
    plt.vlines([data_csv["Energy"][conv_lst].to_numpy()[-1]/3.6e6], 0, cdf_deter[np.argmin(np.abs(x_deter - data_csv["Energy"][conv_lst].to_numpy()[-1]))], color="red", alpha=0.3)
    plt.fill_between(x_deter/3.6e6, cdf_deter, np.zeros(np.size(x_deter)), where= (x_deter > data_csv["Energy"][conv_lst].to_numpy()[-1]), color='red', alpha=0.3)
    plt.plot(x_mcs/3.6e6, cdf_mcs, "-", color="C1", label= "CDF MCS Design ")
    plt.vlines([dist.ppf(0.9)/3.6e6], 0, cdf_mcs[np.argmin(np.abs(x_mcs - dist.ppf(0.9)))], color="red", alpha=0.3)
    plt.fill_between(x_mcs/3.6e6, cdf_mcs, np.zeros(np.size(x_mcs)), where= (cdf_mcs > 0.9), color='red', alpha=0.3)
    plt.xlabel("Energy [KwH]")
    plt.ylabel("CDF [-]")
    plt.grid(lw= 0.8, alpha= 0.8)
    plt.legend()
    plt.suptitle("MCS vs Deterministic")

    plt.savefig(dump_path + "_cdf_" +  ".pdf", bbox_inches= "tight")


def compare_weights():

    with open(os.path.realpath(r'input\environment_variables_plotting.yml'), 'r') as yamlfile:
        data = yaml.safe_load(yamlfile)

    mcs_run_path = data["mcs"]["dir"]
    label_mcs = os.path.split(data["mcs"]["dir"])[-1][3:]

    deter_run_path = data["baseline"]["dir"]
    label_deter = os.path.split(data["baseline"]["dir"])[-1][3:]

    mcs_path =  os.path.join(mcs_run_path, "monte_carlo_results" + label_mcs + ".npz")
    deter_path= os.path.join(deter_run_path, "Deterministic" + label_deter + "_hist.csv")

    dump_path = os.path.join(deter_run_path, "plots")


    data_deter = pd.read_csv(deter_path)
    data_robust = npz_tool(True)
    n_ult = 3.2
    Pmax = 17 # maximum perimeter of fuselage

    # mtom
    mtom_deter = data_deter["MTOM"].to_numpy()[-1]
    mtom_robust = data_robust.df["MTOM"][data_robust.conv_lst].to_numpy()[-1]

    # lf
    lf_deter = data_deter["lf"].to_numpy()[-1]
    lf_robust = data_robust.df["lf"][data_robust.conv_lst].to_numpy()[-1]

    # surface area
    s1_deter = data_deter["S1"].to_numpy()[-1]
    s2_deter = data_deter["S2"].to_numpy()[-1]
    s1_robust = data_robust.df["S1"][data_robust.conv_lst].to_numpy()[-1]
    s2_robust = data_robust.df["S2"][data_robust.conv_lst].to_numpy()[-1]

    #  Aspect ratio
    ar1_deter = data_deter["AR1"].to_numpy()[-1]
    ar2_deter = data_deter["AR2"].to_numpy()[-1]
    ar1_robust = data_robust.df["AR1"][data_robust.conv_lst].to_numpy()[-1]
    ar2_robust = data_robust.df["AR2"][data_robust.conv_lst].to_numpy()[-1]

    # Battery masses
    m_bat_deter = data_deter["battery_m"].to_numpy()[-1]
    m_bat_robust = data_robust.df["battery_m"][data_robust.conv_lst].to_numpy()[-1]

    # Vertical tail mass
    vtail_deter = data_deter["Vertical_tail_mass"].to_numpy()[-1]
    vtail_robust = data_robust.df["Vertical_tail_mass"][data_robust.conv_lst].to_numpy()[-1]

    # Power train  mass
    powertrain_deter = data_deter["Vertical_tail_mass"].to_numpy()[-1]*12
    powertrain_robust = data_robust.df["Vertical_tail_mass"][data_robust.conv_lst].to_numpy()[-1]*12

    # wing mass
    wing_deter = Wing(mtom_deter, s1_deter, s2_deter, n_ult, ar1_deter, ar2_deter)
    wing_robust = Wing(mtom_robust, s1_robust, s2_robust, n_ult, ar1_robust, ar2_robust)

    # fuselage  mass
    fuse_deter = Fuselage(mtom_deter,Pmax, lf_deter, 5)
    fuse_robust = Fuselage(mtom_robust,Pmax, lf_robust, 5)

    #Make list of componetns
    comp_deter= [wing_deter.wweight1, wing_deter.wweight2, vtail_deter, m_bat_deter, fuse_deter.mass, powertrain_deter]
    comp_robust = [wing_robust.wweight1, wing_robust.wweight2, vtail_robust, m_bat_robust, fuse_robust.mass, powertrain_robust]
    str_lst = ["Wing 1", "Wing 2", r"$V_{tail}$", "Battery", "Fuselage", "Powertrain"]

        # Create subplots with 1 row and 2 columns
    fig, axes = plt.subplots(1, 2)
    fig.set_figheight(8)
    fig.set_figwidth(8)

    # Plot the first pie chart on the first subplot
    axes[0].pie(comp_deter, labels=str_lst, autopct='%1.1f%%', startangle=90)
    axes[0].set_title('Deterministic Design Weight Distribution')

    # Plot the second pie chart on the second subplot
    axes[1].pie(comp_robust, labels=str_lst, autopct='%1.1f%%', startangle=90)
    axes[1].set_title('RBDO Design Weight Distribution')

    # Adjust the spacing between subplots
    plt.subplots_adjust(wspace=0.4)

    # Display the figure
    fig.tight_layout()
    plt.savefig(os.path.join(dump_path,  "weight_pie_chart_comparison.pdf") , bbox_inches= "tight")
    # plt.show()


    return comp_deter, comp_robust


# plot_pdf_cdf()
