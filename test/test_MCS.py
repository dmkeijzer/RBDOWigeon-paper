import sys
import pathlib as pl
import  numpy as np
import os
import pickle

sys.path.append(str(list(pl.Path(__file__).parents)[1]))
os.chdir(str(list(pl.Path(__file__).parents)[1]))

from modules.MCS.rv_handler import RandVar
from modules.Flight_performance.Flight_performance_final import mission
import modules.MCS.mcs_handling as mcs
import input.constants_final as const



def test_randvar():
    test_arr = np.random.randn(2000)
    test_instance = RandVar(test_arr)

    ppf_test = test_instance.ppf(0.5)
    expect_test = test_instance.get_expectation()
    std_test = test_instance.get_std()

    assert np.isclose(ppf_test, 0., atol= 1e-1)
    assert np.isclose(expect_test, 0., atol= 1e-1)
    assert np.isclose(std_test, 1., atol= 1e-1)


def test_sampling():
    samples = mcs.sample_mission_data(400)
    print(samples)

    assert samples.shape == (400,5)
    assert (samples[:,0] > const.minimum_dist).all()
    assert (samples[:,0] < const.mission_range*1.1).all() 
    assert (samples[:,4] != 0).any()

def test_get_mcs_results():

    with open(r"test\setup\mission_class_test.pkl", "rb") as f:
        MissionClass = pickle.load(f)

    MTOM = MissionClass.m
    h_cr = MissionClass.h_cruise
    V_cr = MissionClass.v_cruise
    CLmax= MissionClass.CL_max
    S_tot = MissionClass.S
    tot_prop_area = MissionClass.A_disk
    max_power = MissionClass.P_max
    Cl_alpha_curve = MissionClass.Cl_alpha_curve
    CD_a_w = MissionClass.CD_a_w
    CD_a_f = MissionClass.CD_a_f
    alpha_lst = MissionClass.alpha_lst
    drag = MissionClass.Drag    

    mission_test = mission(MTOM, h_cr, V_cr, CLmax, S_tot, tot_prop_area, P_max=max_power,
                            Cl_alpha_curve=Cl_alpha_curve, CD_a_w=CD_a_w, CD_a_f=CD_a_f, alpha_lst=alpha_lst,
                            Drag=drag, t_loiter=15*60, rotational_rate=5, plot_monte_carlo=False)

    results, sample_history = mcs.get_mcs_results(mission_test, 0.7)
    pass