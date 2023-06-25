import scipy.stats as stat
import numpy as np
import sys
import os
import pathlib as pl
import multiprocessing as mp

sys.path.append(str(list(pl.Path(__file__).parents)[2]))
os.chdir(str(list(pl.Path(__file__).parents)[2]))

import input.constants_final as const
from modules.MCS.rv_handler import RandVar


def sample_mission_data(chunksize):
    h_trans_stoch = stat.halfnorm.rvs(loc=95, scale=50, size= chunksize)
    dist_samples = np.array(stat.genextreme.rvs(0.94,loc=309.40,scale=84.96, size = chunksize))*1000

    while np.size(dist_samples[dist_samples < const.minimum_dist]) != 0:
        n_resample = np.size(dist_samples[dist_samples < const.minimum_dist])
        dist_samples[dist_samples < const.minimum_dist] = stat.genextreme.rvs(0.94,loc=309.40,scale=84.96, size = n_resample)*1000
    
    sim_samples = np.column_stack((dist_samples,
                                stat.uniform.rvs(scale=600, size= chunksize) ,
                                h_trans_stoch ,
                                1.2 * h_trans_stoch , 
                                1.4 * h_trans_stoch/const.rod * stat.bernoulli.rvs(0.01, size= chunksize)))
    return sim_samples


def get_mcs_results(MissionClass, conv_target, chunksize= 100):

    # Initalise
    mission_res = []
    sample_history =  []
    conv_condition = True
    conv_metric_lst = []
    

    # Convergence loop
    while conv_condition:
        sim_samples = sample_mission_data(chunksize)
        sample_history.append(sim_samples)

        with mp.Pool(os.cpu_count()) as p:
            mission_res_chunk = np.array(p.starmap(MissionClass.single_sample_monte_carlo, sim_samples), dtype= object)

        mission_res.append(mission_res_chunk)  # array [[x00, x01, x02, x03, x04, array[y00, y01, y02, y03, y04],
            #                                                                     x11, x11, x12, x13, x14, array[y10, y11, y12, y13, y14]] etc
        conv_metric_lst.append(np.std(mission_res[:,0]))

        try:
            print(f"Delta Q = {np.absolute(conv_metric_lst[-2] - conv_metric_lst[-1])} ")
            if np.absolute((conv_metric_lst[-2] - conv_metric_lst[-1])/conv_metric_lst[-2]*100 ) < conv_target and np.absolute((conv_metric_lst[-2] - conv_metric_lst[-3])/conv_metric_lst[-3]*100 )  < conv_target:
                conv_condition = False
        except IndexError:
            pass

    mission_res = np.vstack(mission_res)
    sample_history = np.vstack(sample_history)

    return mission_res, sample_history

def get_performance_data(mission_res):
    data = [i.flatten() for i in np.hsplit(mission_res[:,:-1], 5)]

    with mp.Pool(os.cpu_count()) as p:
        energy_rv, t_rv, power_rv, thrust_rv, t_cr_rv = p.map(RandVar, data)

    return energy_rv, t_rv, power_rv, thrust_rv, t_cr_rv

def get_energy_distr():
    data = [i.flatten() for i in np.hsplit(np.vstack(mission_res[:, -1]), 5)]

    with mp.Pool(os.cpu_count()) as p:
            Ecruise_rv, Eclimb_rv, Edesc_rv, Eloit_cr_rv, Eloit_hov_rv = p.map(RandVar, data)




if __name__ == "__main__":
    print(sample_mission_data(100).shape)
