import pytest
import sys
import pathlib as pl
import os
import pickle

sys.path.append(str(list(pl.Path(__file__).parents)[2]))

from modules.Flight_performance.flight_performance_mcs import mission as mission_mcs
from modules.Flight_performance.flight_performance_baseline import (
    mission as mission_baseline,
)
import input.constants_final as const


os.chdir(str(list(pl.Path(__file__).parents)[2]))


@pytest.fixture
def mission_class_mcs():
    os.chdir(str(list(pl.Path(__file__).parents)[2]))
    with open(r"tests\setup\mission_class_test.pkl", "rb") as f:
        MissionClass = pickle.load(f)

    MTOM = MissionClass.m
    V_cr = MissionClass.v_cruise
    CLmax = MissionClass.CL_max
    S_tot = MissionClass.S
    tot_prop_area = MissionClass.A_disk
    max_power = MissionClass.P_max
    Cl_alpha_curve = MissionClass.Cl_alpha_curve
    CD_a_w = MissionClass.CD_a_w
    CD_a_f = MissionClass.CD_a_f
    alpha_lst = MissionClass.alpha_lst
    drag = MissionClass.Drag

    mission_test = mission_mcs(
        MTOM,
        V_cr,
        CLmax,
        S_tot,
        tot_prop_area,
        P_max=max_power,
        Cl_alpha_curve=Cl_alpha_curve,
        CD_a_w=CD_a_w,
        CD_a_f=CD_a_f,
        alpha_lst=alpha_lst,
        Drag=drag,
        plot_monte_carlo=False,
    )
    return mission_test


@pytest.fixture
def mission_class_baseline():
    os.chdir(str(list(pl.Path(__file__).parents)[2]))
    with open(r"tests\setup\mission_class_test.pkl", "rb") as f:
        MissionClass = pickle.load(f)

    MTOM = MissionClass.m
    V_cr = MissionClass.v_cruise
    CLmax = MissionClass.CL_max
    S_tot = MissionClass.S
    tot_prop_area = MissionClass.A_disk
    max_power = MissionClass.P_max
    Cl_alpha_curve = MissionClass.Cl_alpha_curve
    CD_a_w = MissionClass.CD_a_w
    CD_a_f = MissionClass.CD_a_f
    alpha_lst = MissionClass.alpha_lst
    drag = MissionClass.Drag

    mission_test = mission_baseline(
        MTOM,
        const.h_cruise,
        V_cr,
        CLmax,
        S_tot,
        tot_prop_area,
        P_max=max_power,
        Cl_alpha_curve=Cl_alpha_curve,
        CD_a_w=CD_a_w,
        CD_a_f=CD_a_f,
        alpha_lst=alpha_lst,
        Drag=drag,
    )

    return mission_test
