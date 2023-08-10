import sys
import pathlib as pl
import  numpy as np
import os
import pickle
import matplotlib.pyplot as plt
import pdb

sys.path.append(str(list(pl.Path(__file__).parents)[1]))
os.chdir(str(list(pl.Path(__file__).parents)[1]))

from modules.MCS.rv_handler import RandVar
from tests.setup.fixtures import mission_class_baseline, mission_class_mcs
import modules.MCS.mcs_handling as mcs
import input.constants_final as const



def test_flight_performance_baseline(mission_class_baseline):
    # mission_class_baseline.plotting = True
    Etot, t_tot, P_mac, T_max, t_hor, energy_dist = mission_class_baseline.total_energy()

    print(f"Energy = {Etot}")
    print(f"Time = {t_tot}")

    assert Etot/3.6e6 > 100
    assert Etot/3.6e6 > 100 # Needs more elaborate tests


def test_flight_performance_mcs(mission_class_mcs):
    # mission_class_mcs.plotting = True
    Etot, t_tot, P_mac, T_max, t_hor, energy_dist = mission_class_mcs.single_sample_monte_carlo(const.mission_range_baseline, const.loiter_time_baseline,const.transition_height_baseline, const.h_cruise , 0, const.h_cruise )

    print(f"Energy = {Etot}")
    print(f"Time = {t_tot}")

    assert Etot/3.6e6 > 100
    assert Etot/3.6e6 > 100 #Needs more elaborate tests


def test_equality_mission_class(mission_class_baseline, mission_class_mcs):
    Etot, t_tot, P_mac, T_max, t_hor, energy_dist = mission_class_mcs.single_sample_monte_carlo(const.mission_range_baseline, const.loiter_time_baseline,const.transition_height_baseline, const.h_cruise , 0, const.h_cruise )
    Etot_base, t_tot_base, P_mac_base, T_max_base, t_hor_base, energy_dist_base = mission_class_baseline.total_energy()

    print(f"Energy mcs = {Etot/3.6e6}")
    print(f"Energy baseline = {Etot_base/3.6e6}")
    

    assert np.isclose(Etot_base/3.6e6,  Etot/3.6e6, atol= 0.1)


# def test_cruising_alt_sensitivity(mission_class_mcs):

#     energies = []
#     x = np.linspace(300,1000,30)
#     for i in x:
#         Etot, t_tot, P_mac, T_max, t_hor, energy_dist = mission_class_mcs.single_sample_monte_carlo(393.2e3, 592 , 100, 120, 0, i)
#         energies.append(Etot/3.6e6)

#     print(f" x = {x}")
#     print(f" energies = {energies}")

#     plt.plot(x, energies)
#     plt.xlabel("Cruising altitude")
#     plt.ylabel("Energy consumed")
#     plt.grid()
#     plt.show()
