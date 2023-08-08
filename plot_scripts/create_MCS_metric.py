import numpy as np
import scipy.stats as stat
import sys
import pathlib as pl
import os 
import multiprocessing as mp
import matplotlib.pyplot as plt
import pickle
import yaml

sys.path.append(str(list(pl.Path(__file__).parents)[1]))


import modules.MCS.mcs_handling as mcs
import modules.Flight_performance.flight_performance_mcs as FP
from modules.MCS.rv_handler import RandVar
import input.constants_final as const

os.chdir(str(list(pl.Path(__file__).parents)[1]))


if __name__ == "__main__": #Required due to the multiprocessing involved

    #USER INPUT FROM INPUT
    #==========================================================================================================
    with open(os.path.realpath(r'input\environment_variables_plotting.yml'), 'r') as yamlfile:
        data = yaml.safe_load(yamlfile)

    dir_path = data["baseline"]["dir"]
    label =  os.path.split(dir_path)[-1][3:]
    pickle_path = os.path.join(dir_path,  "Mission_class" + label + ".pkl" )
    #==========================================================================================================



    if not os.path.exists(pickle_path):
        raise Exception("Could not find pickle path")
            
    with open(pickle_path, "rb") as f:
        mission_baseline = pickle.load(f)

    MTOM = mission_baseline.m
    V_cr = mission_baseline.v_cruise
    CLmax= mission_baseline.CL_max
    S_tot = mission_baseline.S
    tot_prop_area = mission_baseline.A_disk
    max_power = mission_baseline.P_max
    Cl_alpha_curve = mission_baseline.Cl_alpha_curve
    CD_a_w = mission_baseline.CD_a_w
    CD_a_f = mission_baseline.CD_a_f
    alpha_lst = mission_baseline.alpha_lst
    drag = mission_baseline.Drag    

    mission = FP.mission(MTOM, V_cr, CLmax, S_tot, tot_prop_area, P_max=max_power,
                            Cl_alpha_curve=Cl_alpha_curve, CD_a_w=CD_a_w, CD_a_f=CD_a_f, alpha_lst=alpha_lst,
                            Drag=drag, plot_monte_carlo=False)

    #-----------------------------Monte carlo energy estimation--------------------------------------
    mission_res, sample_hist, conv_metric_lst =  mcs.get_mcs_results(mission, const.convergence_targ, chunksize= const.chunksize)
    energy_rv, t_rv, power_rv, thrust_rv, t_cr_rv =  mcs.get_performance_data(mission_res)
    Ecruise_rv, Eclimb_rv, Edesc_rv, Eloit_cr_rv, Eloit_hov_rv = mcs.get_energy_distr(mission_res)

    # Create storage location for data from mcs metrci
    if os.path.exists(os.path.join(dir_path, "mcs_metric")):
        pass
    else:
        os.mkdir(os.path.join(dir_path, 'mcs_metric'))

    np.save(os.path.join(dir_path, "mcs_metric",  r"mcs_metric_samples" + label + ".npy"), sample_hist)
    np.save(os.path.join(dir_path, "mcs_metric", r"mcs_metric_results" + label + ".npy"), mission_res)
    print("\nSaved the results of the mission analysis successfully\n")

        
    str_lst = ["energy_rv", "t_rv", "power_rv", "thrust_rv", "t_cr_rv", "Ecruise_rv", "Eclimb_rv", "Edesc_rv", "Eloit_cr_cv", "Eloit_hov_rv"]
    obj_lst = [energy_rv, t_rv, power_rv, thrust_rv, t_cr_rv, Ecruise_rv, Eclimb_rv, Edesc_rv, Eloit_cr_rv, Eloit_hov_rv]

    for name, obj in zip(str_lst, obj_lst):
        with open(os.path.join(dir_path, "mcs_metric",  name +  label +  ".pkl" ), "wb") as f:
            pickle.dump(obj, f)
        print(f"Saved the results {name} successfully")
        