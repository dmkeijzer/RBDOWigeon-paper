
import sys
import pathlib as pl
import  numpy as np
import os

sys.path.append(str(list(pl.Path(__file__).parents)[1]))
os.chdir(str(list(pl.Path(__file__).parents)[1]))

from modules.MCS.rv_handler import RandVar
import modules.integration.integration_class_baseline  as int_class_baseline
import modules.integration.integration_class_mcs  as int_class_mcs
import input.constants_final as const

# initial_estimate = [MTOM, 0, V_cr, h_cr, C_L_cr, CLmax, prop_radius, de_da, Sv, V_stall, max_power, AR_wing1,
#                             AR_wing2, Sr_Sf, s1, xf, zf, xr, zr, max_thrust_stall, 1, 1.5, 2.4, 2.6, 8, bat_pos]


initial_estimate = {
    "mtom": 2800,
    "not_used1": 0,
    "V_cr": 66.,
    "h_cr": 800,
    "C_L_cr": 0.8,
    "CLmax": 1.68,
    "prop_radius": 0.55,
    "de_da": 0.25,
    "Sv": 1.1,
    "V_stall": 40.,
    "max_power": 1.5e6,
    "AR_wing1": 9,
    "AR_wing2": 9,
    "Sr_Sf":  1.,
    "s1": (1 + 1)**-1,
    "xf": 0.5,
    "zf": 0.3,
    "xr": 6.1,
    "zr": 1.7,
    "max_thrust_stall": 2800*const.g*0.1,
    "root_chord_vtail": 1,
    "tw_ratio_control": 1.5,
    "x_front": 2.4,
    "x_aft": 2.6,
    "not_used2": 0,
    "bat_pos": 1.3
}

input = list(initial_estimate.values())



def test_integration_baseline():
    optimizer_out, internal_input, other_output =  int_class_baseline.RunDSE(input).run(input)
    print(other_output["lines"])

    assert other_output["lines"][7][1] != initial_estimate["mtom"]

