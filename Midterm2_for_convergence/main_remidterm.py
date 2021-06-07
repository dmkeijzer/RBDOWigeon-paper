import numpy as np

import constants as const
import Aero_tools as at

import Drag_midterm2 as drag_comp
import Wing_design_midterm2 as wing_design
import Airfoil_analysis_midterm2 as airfoil

import prelim_ADT as ADT
import engine_sizing_positioning_midterm2 as eng_siz

import Vertical_tail_sizing_midterm2 as vert_tail
import Weight_midterm2 as weight


"""
Here we will run the midterm code (and part of the new code when available) to have converged values
Create copies of the midterm tools in this folder if necessary and make sure they comply with the new coding rules
Among other things, the idea is to start with a higher weight estimate, closer to the current estimated weight

Start with performance to get wing loading and such, needed for aero

The go to aero to get wing planform

From there we can size the engines

Here we can update the weight and iterate

Lastly, we can size the vertical tail

Vertical tail does not have outputs needed for other departments and it required to manually read a graph, hence it can
be left out of the optimisation and only run at the eng

"""
# --------------------- Fixed parameters and constants ------------------------
# Constants from constants.py
g0 = const.g
rho0 = const.rho_0
gamma = const.gamma
R = const.R

# Fuselage shape is fixed, so fixed variables (update in constants.py if needed)
w_fus = const.w_fuselage
l1_fus = const.l_nosecone
l2_fus = const.l_cylinder
l3_fus = const.l_tailcone
l_fus = l1_fus + l2_fus + l3_fus
h_fus = const.h_fuselage
fus_upsweep = const.upsweep

# Airfoil parameters
# TODO: Implement airfoil parameters

# --------------------- Initial estimates ---------------------
# TODO: revise these values
# Aero
CLmax = 1.46916
S1, S2 = 5.5, 5.5  # surface areas of wing one and two
AR_wing = 10        # Aspect ratio of a wing, not aircraft
AR_tot = AR_wing/2  # Aspect ratio of aircraft

# Wingtips
S_wt = 0  # Surface of the wingtips
h_wt_fwd = 0
h_wt_bck = 0


# Performance
h_cr = 1
V_cr = 1
ISA = at.ISA(h_cr)


# Propulsion
n_prop = 16  # number of engines
disk_load = 250  # [kg/m^2]

# Structures
# TODO: Revise initial mass
MTOM = 1972  # maximum take-off mass from statistical data - Class I estimation

n_ult = 3.2 * 1.5  # 3.2 is the max we found, 1.5 is the safety factor


# Stability
S_v = 5  # Area of the vertical tail [m^2]


# ------------------ Constants for weight estimation ----------------

# TODO: revise Pmax
Pmax = 15.25  # this is defined as maximum perimeter in Roskam, so i took top down view of the fuselage perimeter

# PAX
# From project guide: 95 kg per pax (including luggage)
n_pax = 5  # number of passengers (pilot included)
m_pax = 88  # assume average mass of a passenger according to Google
cargo_m = (95-m_pax)*n_pax  # Use difference of pax+luggage - pax to get cargo mass

# Fuselage and CGs
pos_fus = l_fus/2                       # fuselage centre of mass away from the nose
pos_lgear = pos_fus + 0.4               # Main landing gear position away from the nose
pos_frontwing, pos_backwing = 0.5, 7    # positions of the wings away from the nose

mass_per_prop = 480 / n_prop
m_prop = [mass_per_prop] * n_prop       # list of mass of engines (so 30 kg per engine with nacelle and propeller)
pos_prop = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0,
            7.0]  # 8 on front wing and 8 on back wing

# ------------- Initial mass estimate -------------
wing = weight.Wing(MTOM, S1, S2, n_ult, AR_wing, [pos_frontwing, pos_backwing])
fuselage = weight.Fuselage(MTOM, Pmax, l_fus, n_pax, pos_fus)
lgear = weight.LandingGear(MTOM, pos_lgear)
props = weight.Propulsion(n_prop, m_prop, pos_prop)
Mass = weight.Weight(m_pax, wing, fuselage, lgear, props, cargo_m=cargo_m, cargo_pos=6, battery_m=400, battery_pos=3.6,
                p_pax=[1.5, 3, 3, 4.2, 4.2])

# Initial estiate for the mass
MTOM = Mass.MTOM()

iterate = True

while iterate:


    # TODO: inputs from performance
    M = 1
    S = 1

    # Aero
    wing_design = wing_design.wing_design(AR_tot, 0.5, 0, 0.5, 0, M, S, l_fus-1, h_fus-0.3, w_fus, 0, 0)

    # [b2, c_r2, c_t2, c_MAC2, y_MAC2, X_LEMAC2]
    wing_plan_1, wing_plan_2 = wing_design.wing_planform_double()

    # CL_max
    CLmax = wing_design.CLmax_s()[0]

    # Drag
    # 'tandem', S, l1_fus, l2_fus, l3_fus, np.sqrt(w_fus*h_fus),
    # h, IF_f, IF_w,IF_v, C_L_minD, Abase, S_v, S_t,s1,s2, h_wl1,h_wl2):

    # Oswald efficiency factor
    e = drag_comp.e_OS(AR_tot) * drag_comp.e_factor('tandem', h_fus-0.3, wing_plan_1[0], drag_comp.e_OS(AR_tot))

    # Airfoil
    airfoil_stats = airfoil.airfoil_stats()
    S_t = 0

    drag = drag_comp.componentdrag('tandem', S, l1_fus, l2_fus, l3_fus, np.sqrt(w_fus*h_fus), V_cr, rho, wing_plan_1[3],
                                   AR_tot, e, M, const.k, const.flamf, const.flamw, dyn_vis, const.tc, const.xcm, 0,
                                   wing_design.sweep_atx(0), fus_upsweep, wing_plan_1[2], h_fus-0.3, const.IF_f,
                                   const.IF_w, const.IF_v, airfoil_stats[2], const.Abase, S_v, S_t, 0.5, 0.5, 0, 0)

    # TODO: get CL for cruise
    CD = drag.CD(C_L=1)

    # Propulsion

    act_disk = ADT.ActDisk(TW_ratio, MTOM, v_e, V_cr, D, D)
    # With fuselage shape and span we can have size of the engines
    # From that we can use BEM to design the blades (here number of blades is an input, so we can optimise it if necessary,
    # or just assume one



    # Performance



    # Update weight

    MTOW = weight.Weight()

# Stability
# W,h,xcg,lfus,hfus,wfus,V0,Vstall,CD0,CLfwd,CLrear,CLafwd,CLarear,Sfwd,Srear,Afwd,Arear,Lambda_c4_fwd,Lambda_c4_rear,cfwd,crear,bfwd,brear,taper,ARv):
vertical_tail = vert_tail.VT_sizing()
