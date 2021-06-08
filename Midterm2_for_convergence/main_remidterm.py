import numpy as np

import constants as const
import Aero_tools as at

import Drag_midterm2 as drag_comp
import Wing_design_midterm2 as wing_des
import Airfoil_analysis_midterm2 as airfoil

import prelim_ADT as ADT
import engine_sizing_positioning_midterm2 as eng_siz
import battery_midterm2 as bat

import performance_analysis_midterm2 as perf
import Flight_performance_final_midterm2 as energy_calc

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


# --------------------- Initial estimates ---------------------
# Aero
CLmax = 1.46916
s1, s2 = const.s1, const.s2   # Ratio of front and back wing areas to total area
S1, S2 = 5.25, 5.25           # surface areas of wing one and two
S_tot = S1+S2                 # Total wing surface area
AR_wing = 8                  # Aspect ratio of a wing, not aircraft
AR_tot = AR_wing/2            # Aspect ratio of aircraft

# Wingtips
S_wt = 0    # Surface of the winglets
h_wt_1 = 0  # Height of front wingtips
h_wt_2 = 0  # Height of back wingtips


# Performance
h_cr = 1000
V_cr = 52.87
C_L_cr = 0.8
V_stall = 40
V_max = 100
n_turn = 2
ROC = 10
ROC_hover = 2


# Propulsion
n_prop = 12                 # Number of engines [-]
disk_load = 250             # [kg/m^2]
clearance_fus_prop = 0.2    # Horizontal separation between the fuselage and the first propeller [m]
clearance_prop_prop = 0.2   # Horizontal separation between propellers [m]
xi_0 = 0.1                  # r/R ratio of hub diameter to out diameters [-]
m_bat = 483.15              # Initial estimate for battery mass [kg]


# Structures
# TODO: Revise initial mass
MTOM = 3000         # maximum take-off mass from statistical data - Class I estimation

n_ult = 3.2 * 1.5   # 3.2 is the max we found, 1.5 is the safety factor


# Stability
S_v = 1.063     # Area of the vertical tail [m^2]
h_tail = 1.152  # Height of vertical tail [m]

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
# pos_prop = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0,
#             7.0]  # 8 on front wing and 8 on back wing
pos_prop = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0]  # 6 on front wing and 6 on back wing


# ------------- Initial mass estimate -------------
wing = weight.Wing(MTOM, S1, S2, n_ult, AR_wing, [pos_frontwing, pos_backwing])
fuselage = weight.Fuselage(MTOM, Pmax, l_fus, n_pax, pos_fus)
lgear = weight.LandingGear(MTOM, pos_lgear)
props = weight.Propulsion(n_prop, m_prop, pos_prop)
Mass = weight.Weight(m_pax, wing, fuselage, lgear, props, cargo_m=cargo_m, cargo_pos=6, battery_m=m_bat,
                     battery_pos=3.6, p_pax=[1.5, 3, 3, 4.2, 4.2])

# Initial estimate for the mass
MTOM = Mass.mtom

# TODO: revise approach of reiterating
# Reiterate once because wing uses value for MTOM
wing = weight.Wing(MTOM, S1, S2, n_ult, AR_wing, [pos_frontwing, pos_backwing])
fuselage = weight.Fuselage(MTOM, Pmax, l_fus, n_pax, pos_fus)
lgear = weight.LandingGear(MTOM, pos_lgear)
props = weight.Propulsion(n_prop, m_prop, pos_prop)
Mass = weight.Weight(m_pax, wing, fuselage, lgear, props, cargo_m=cargo_m, cargo_pos=6, battery_m=m_bat,
                     battery_pos=3.6, p_pax=[1.5, 3, 3, 4.2, 4.2])

# Initial estimate for the mass
MTOM = Mass.mtom
print("Initial MTOM:", MTOM, "[kg]")
print(" ")

iterate = True
while iterate:

    # Get atmospheric values at cruise
    ISA = at.ISA(h_cr)
    rho = ISA.density()             # Density
    a = ISA.soundspeed()            # Speed of sound
    dyn_vis = ISA.viscosity_dyn()   # Dynamic viscosity

    M = V_cr/a                      # Cruise Mach number

    # Aero
    wing_design = wing_des.wing_design(AR_tot, s1, 0, s2, 0, M, S_tot, l_fus-1, h_fus-0.3, w_fus, h_wt_1, h_wt_2)

    # [b2, c_r2, c_t2, c_MAC2, y_MAC2, X_LEMAC2]
    wing_plan_1, wing_plan_2 = wing_design.wing_planform_double()

    taper = wing_plan_1[2]/wing_plan_1[1]

    # CL_max
    CLmax = wing_design.CLmax_s()[0]

    # Lift slope
    CL_alpha_1 = wing_design.liftslope()
    CL_alpha_2 = wing_design.liftslope()

    # ------ Drag ------

    # Oswald efficiency factor
    e = drag_comp.e_OS(AR_tot) * drag_comp.e_factor('tandem', h_fus-0.3, wing_plan_1[0], drag_comp.e_OS(AR_tot))

    # Airfoil characteristics
    airfoil_stats = airfoil.airfoil_stats()

    drag = drag_comp.componentdrag('tandem', S_tot, l1_fus, l2_fus, l3_fus, np.sqrt(w_fus*h_fus), V_cr, rho,
                                   wing_plan_1[3], AR_tot, e, M, const.k, const.flamf, const.flamw, dyn_vis, const.tc,
                                   const.xcm, 0, wing_design.sweep_atx(0)[0], fus_upsweep, wing_plan_1[2], h_fus-0.3,
                                   const.IF_f, const.IF_w, const.IF_v, airfoil_stats[2], const.Abase, S_v, S_wt,
                                   s1, s2, h_wt_1, h_wt_2)

    # TODO: get CL for cruise
    CD0 = drag.CD0()
    CD_cr = drag.CD(C_L=C_L_cr)

    # ----------------- Vertical drag -------------------
    Afus = np.pi * np.sqrt(w_fus * h_fus)**2 / 4

    CDs = drag.CD(CLmax)
    CDs_f = drag.CD0_f
    CDs_w = CDs - CDs_f

    CD_a_w = wing_design.CDa_poststall(const.tc, CDs_w, CDs_f, Afus, 0, "wing", drag.CD)
    CD_a_f = wing_design.CDa_poststall(const.tc, CDs_w, CDs_f, Afus, 90, "fus", drag.CD)

    CD_vertical = CD_a_w + CD_a_f

    # Propulsion
    # Get drag at cruise
    D_cr = CD_cr * 0.5 * rho * V_cr**2 * S_tot

    # Size the propellers
    prop_sizing = eng_siz.PropSizing(wing_plan_1[0], w_fus, n_prop, clearance_fus_prop, clearance_prop_prop, MTOM, xi_0)

    prop_radius = prop_sizing.radius()
    prop_area = prop_sizing.area_prop()
    disk_load = prop_sizing.disk_loading()

    # act_disk = ADT.ActDisk(TW_ratio, MTOM, v_e, V_cr, D, D)
    # With fuselage shape and span we can have size of the engines
    # From that we can use BEM to design the blades (here number of blades is an input,
    # so we can optimise it if necessary, or just assume one

    # ----------------------- Performance ------------------------
    init_sizing = perf.initial_sizing(h_cr, None, drag, V_stall, V_max, n_turn, ROC, V_cr, ROC_hover, MTOM*g0,
                                      CD_vertical, const.eff_prop, const.eff_hover, disk_load)

    # Get wing loading and from that the area
    WS = init_sizing.sizing()[0]

    S_tot = MTOM*g0/WS

    S1, S2 = S_tot*s1, S_tot*s2

    # Cruise CL of the wings
    L_cr = MTOM*g0
    L_cr_1 = L_cr/2
    L_cr_2 = L_cr/2

    CL_cr_1 = 2*L_cr_1/(rho * V_cr**2 * S1)
    CL_cr_2 = 2*L_cr_2/(rho * V_cr**2 * S2)

    # Energy sizing
    mission = energy_calc.mission(MTOM, h_cr, V_cr, S_tot)

    # Get approximate overall efficiency
    eff_overall = 0.91 * 0.57 + 0.699 * 0.43
    energy = 1.2 * mission.total_energy()[0] * 2.77778e-7 * 1000 / eff_overall  # From [J] to [Wh]

    # Battery sizing
    battery = bat.Battery(500, 1000, energy, 1)

    m_bat = battery.mass()

    # -------------------- Update weight ------------------------
    # TODO update battery weight
    wing = weight.Wing(MTOM, S1, S2, n_ult, AR_wing, [pos_frontwing, pos_backwing])
    fuselage = weight.Fuselage(MTOM, Pmax, l_fus, n_pax, pos_fus)
    lgear = weight.LandingGear(MTOM, pos_lgear)
    props = weight.Propulsion(n_prop, m_prop, pos_prop)
    Mass = weight.Weight(m_pax, wing, fuselage, lgear, props, cargo_m=cargo_m, cargo_pos=6, battery_m=m_bat,
                         battery_pos=3.6, p_pax=[1.5, 3, 3, 4.2, 4.2])

    # Update mass and get CG
    MTOM_new = Mass.mtom
    x_CG_MTOM = Mass.mtom_cg

    if (MTOM_new-MTOM)/MTOM < 0.01:
        iterate = False
        MTOM = MTOM_new

    else:
        MTOM = MTOM_new
    print("New MTOM:", MTOM)
    print(" ")

# Stability
vertical_tail = vert_tail.VT_sizing(MTOM*g0, h_cr, x_CG_MTOM, l_fus, h_fus, w_fus, V_cr, V_stall, CD0,
                                    CL_cr_1, CL_cr_2, CL_alpha_1, CL_alpha_2, S1, S2, AR_wing, AR_wing, 0, 0,
                                    wing_plan_1[3], wing_plan_2[3], wing_plan_1[0], wing_plan_2[0], taper, ARv=1.25)

print("Converged MTOM:", MTOM, "[kg]")

print("Energy:", energy, "[kWh]")
print("Battery mass:", m_bat, "[kg]")
print("Wing surface:", S_tot, "[m^2]")
print("")
print("Propeller radius:", prop_radius, "[m]")
print("Disk loading:", disk_load, "[kg/m^2]")
print("Cruise drag:", D_cr, "[N]")
print("Thrust per engine at cruise:", D_cr/16, "[N]")
print("")
print("Cruise speed:", V_cr, "[m/s]")
print("Cruise height:", h_cr, "[m]")

# print("Vertical tail surface", vertical_tail.final_VT_rudder(n_prop, ))
print(" ")
