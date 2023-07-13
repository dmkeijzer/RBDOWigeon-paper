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

#USER INPUT FROM INPUT
#==========================================================================================================
with open(r'input\environment_variables_plotting.yml', 'r') as yamlfile:
    data = yaml.safe_load(yamlfile)

dir_path = data["baseline"]["dir"]
pkl_file = data["baseline"]["name_pkl"]
#==========================================================================================================


pickle_path = os.path.join(dir_path, pkl_file)

if not os.path.exists(pickle_path):
    raise Exception("Could not find pickle path")
        
with open(pickle_path, "rb") as f:
    mission_baseline = pickle.load(f)

MTOM = mission_baseline.m
h_cr = mission_baseline.h_cruise
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

mission = FP.mission(MTOM, h_cr, V_cr, CLmax, S_tot, tot_prop_area, P_max=max_power,
                        Cl_alpha_curve=Cl_alpha_curve, CD_a_w=CD_a_w, CD_a_f=CD_a_f, alpha_lst=alpha_lst,
                        Drag=drag, t_loiter=15*60, rotational_rate=5, mission_dist=const.mission_range, plot_monte_carlo=False)

#-----------------------------Monte carlo energy estimation--------------------------------------

file_dir = os.path.join(os.path.dirname(__file__), "deterministic_mcs_metric_storage")
file_name = r"deterministic_mcs_metric.npy"

if not os.path.exists(file_dir):
    raise Exception("Could not find the directory to write the file to")

mission_res, sample_hist, conv_metric_lst =  mcs.get_mcs_results(mission, const.convergence_targ , chunksize= const.chunksize)

energy_rv, t_rv, power_rv, thrust_rv, t_cr_rv =  mcs.get_performance_data(mission_res)
Ecruise_rv, Eclimb_rv, Edesc_rv, Eloit_cr_rv, Eloit_hov_rv = mcs.get_energy_distr(mission_res)

np.save(os.path.join(file_dir, file_name), mission_res)
print("Saved the results of the mission analysis successfully")


#Create a fitting distribution for all stochastic variables

performance_data =  [i.flatten() for i in np.hsplit(mission_res[:,:-1], 5)]

with mp.Pool(os.cpu_count()) as p:
    energy_rv, t_rv, power_rv, thrust_rv, t_cr_rv = p.map(RandVar, performance_data)


energy_dist_data = [i.flatten() for i in np.hsplit(np.vstack(mission_res[:, -1]), 5)]

with mp.Pool(os.cpu_count()) as p:
        Ecruise_rv, Eclimb_rv, Edesc_rv, Eloit_cr_rv, Eloit_hov_rv = p.map(RandVar, energy_dist_data)
    
str_lst = ["energy_rv", "t_rv", "power_rv", "thrust_rv", "t_cr_rv", "Ecruise_rv", "Eclimb_rv", "Edesc_rv", "Eloit_cr_cv", "Eloit_hov_rv"]
obj_lst = [energy_rv, t_rv, power_rv, thrust_rv, t_cr_rv, Ecruise_rv, Eclimb_rv, Edesc_rv, Eloit_cr_rv, Eloit_hov_rv]

for name, obj in zip(str_lst, obj_lst):
    with open(os.path.join(file_dir, name + ".pkl" ), "wb") as f:
        pickle.dump(obj, f)
    print(f"Saved the results {name} successfully")
    