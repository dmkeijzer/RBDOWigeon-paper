import numpy as np
import scipy.stats as stat
import sys
import pathlib as pl
import os 
import multiprocessing as mp
import matplotlib.pyplot as plt
import pickle

sys.path.append(str(list(pl.Path(__file__).parents)[1]))


import Flight_performance.Flight_performance_final as FP
from Validation_analysis.rv_handler import RandVar
import Final_optimization.constants_final as const


if __name__ == "__main__":

    file_baseline = r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\valid_data\Baseline\Deterministic_Jun__1_22.00_hist.csv"
            
    with open(r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\Mission_class.pkl", "rb") as f:
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

    # Initalise
    mission_res = np.ones((2,6))
    conv_condition = True
    conv_metric_lst = []
    conv_target = 0.85 # Percentage difference allowed in std
    n_iterations = 10 
    min_mission_dist = 100

    print("Entering convergence loop")

    # Convergence loop
    while conv_condition:
        h_trans_stoch = stat.halfnorm.rvs(loc=95, scale=50, size= n_iterations)
        dist_samples = np.array(stat.genextreme.rvs(0.94,loc=309.40,scale=84.96, size = n_iterations))

        while np.size(dist_samples[dist_samples < min_mission_dist]) != 0:
            n_resample = np.size(dist_samples[dist_samples <min_mission_dist])
            dist_samples[dist_samples < min_mission_dist] = stat.genextreme.rvs(0.94,loc=309.40,scale=84.96, size = n_resample)
        
        sim_samples = np.column_stack((dist_samples*1000,
                                    stat.uniform.rvs(scale=600, size= n_iterations) ,
                                    h_trans_stoch ,
                                    1.2 * h_trans_stoch , 
                                    1.4 * h_trans_stoch/mission.rod * stat.bernoulli.rvs(0.01, size= n_iterations)))

        with mp.Pool(os.cpu_count()) as p:
            mission_res_chunk = p.starmap(mission.single_sample_monte_carlo, sim_samples)

        mission_res = np.append(mission_res, mission_res_chunk, axis=0) # array [[x00, x01, x02, x03, x04, array[y00, y01, y02, y03, y04],
            #                                                                     x11, x11, x12, x13, x14, array[y10, y11, y12, y13, y14]] etc

        conv_metric_lst.append(np.std(mission_res[:,0]))
        print(conv_metric_lst[-1])


        try:
            if np.absolute((conv_metric_lst[-2] - conv_metric_lst[-1])/conv_metric_lst[-2]*100 ) < conv_target and np.absolute((conv_metric_lst[-2] - conv_metric_lst[-3])/conv_metric_lst[-3]*100 )  < conv_target:
                conv_condition = False
        except IndexError:
            pass

    mission_res = np.delete(mission_res, [0,1], axis= 0)


    #Create a fitting distribution for all stochastic variables

    performance_data =  [i.flatten() for i in np.hsplit(mission_res[:,:-1], 5)]

    with mp.Pool(os.cpu_count()) as p:
        energy_rv, t_rv, power_rv, thrust_rv, t_cr_rv = p.map(RandVar, performance_data)


    energy_dist_data = [i.flatten() for i in np.hsplit(np.vstack(mission_res[:, -1]), 5)]

    with mp.Pool(os.cpu_count()) as p:
            Ecruise_rv, Eclimb_rv, Edesc_rv, Eloit_cr_rv, Eloit_hov_rv = p.map(RandVar, energy_dist_data)


    # Turning stochastic variables into deterministic values by means of a confidence interval 

    x, pdf, cdf = energy_rv.plt()

    plt.plot(x/3.6e6,pdf)
    plt.show()

    # c_i = 0.9 # confidence interval

    # energy_wc =  energy_rv.ppf(c_i)
    # energy_optimizer = energy_rv.get_expectation() + energy_rv.get_std()
    # t_tot = t_rv.ppf(c_i)
    # P_max_eng_mission  = power_rv.ppf(c_i)
    # max_thrust = thrust_rv.ppf(c_i)
    # t_hor = t_cr_rv.ppf(c_i)
    # energy_pie_chart_distr  = [Ecruise_rv.ppf(c_i), Eclimb_rv.ppf(c_i), Edesc_rv.ppf(c_i), Eloit_cr_rv.ppf(c_i), Eloit_hov_rv.ppf(c_i)]