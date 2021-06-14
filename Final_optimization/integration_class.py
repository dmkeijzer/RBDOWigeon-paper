import numpy as np
import Aero_tools as at
import constants_final as const

# Aero
import Preliminary_Lift.Drag as drag_comp
import Preliminary_Lift.Wing_design as wingdes
import Preliminary_Lift.Airfoil_analysis as airfoil

# Performance
import Flight_performance.Flight_performance_final as FP

# Propulsion
import PropandPower.BEM as BEM
import PropandPower.power_budget as PB
import PropandPower.engine_sizing_positioning as eng_siz
import PropandPower.battery as batt

# Stability and Control
import stab_and_ctrl.Vertical_tail_sizing as vert_tail
from stab_and_ctrl.hover_controllabilty import HoverControlCalcTandem
from stab_and_ctrl.landing_gear_placement import LandingGearCalc
from stab_and_ctrl.loading_diagram import CgCalculator
from stab_and_ctrl.xcg_limits import xcg_limits, optimise_wings

# Structures
import structures.Weight as wei
import structures.StructuralAnalysis as SAD

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
# l3_fus = const.l_tailcone
# TODO: fuselage length is now an optimisation variable, tailcone initial guess: 2.7 (this is a minimum)
# l_fus = l1_fus + l2_fus  # + l3_fus
h_fus = const.h_fuselage
fus_upsweep = const.upsweep

# --------------------- Initial estimates ---------------------
# Aero
# CLmax = 1.7
# s1, s2 = const.s1, const.s2   # Ratio of front and back wing areas to total area
# S1, S2 = 8.25, 8.25           # surface areas of wing one and two
# S_tot = S1+S2                 # Total wing surface area
# AR_wing = 7.5                 # Aspect ratio of a wing, not aircraft
# AR_tot = AR_wing/2            # Aspect ratio of aircraft

# Wingtips
# S_wt = 0    # Surface of the winglets
h_wt_1 = 0.5  # Height of front wingtips
h_wt_2 = 0.5  # Height of back wingtips


# Performance
# h_cr = 1000
# V_cr = 52.87
# C_L_cr = 0.8
# V_stall = 40
# V_max = 100
# n_turn = 2
# ROC = 10
# ROC_hover = 2

mission_range = 300e3       # [m] Mission range  TODO: Maybe add 50 km


# Propulsion
n_prop_1 = 6
n_prop_2 = 6
n_prop = n_prop_1+n_prop_2  # Total number of engines [-]
# disk_load = 250             # [kg/m^2]
# clearance_fus_prop = 0.3    # Horizontal separation between the fuselage and the first propeller [m]
# clearance_prop_prop = 0.3   # Horizontal separation between propellers [m]
# xi_0 = 0.1                  # r/R ratio of hub diameter to out diameters [-]
# m_bat = 800                 # Initial estimate for battery mass [kg]
max_power = 2e6             # [W] Maximum engine power TODO: Check

# Structures
n_ult = 3.2 * 1.5   # 3.2 is the max we found, 1.5 is the safety factor


# ------------------ Constants for weight estimation ----------------
# TODO: revise Pmax
Pmax_weight = 15.25  # this is defined as maximum perimeter in Roskam, so i took top down view of the fuselage perimeter

# # PAX
# # From project guide: 95 kg per pax (including luggage)
# n_pax = 5  # number of passengers (pilot included)
# m_pax = 88  # assume average mass of a passenger according to Google
# cargo_m = (95-m_pax)*n_pax  # Use difference of pax+luggage - pax to get cargo mass

# # Fuselage and CGs
# pos_fus = l_fus/2                       # fuselage centre of mass away from the nose
# pos_lgear = pos_fus + 0.4               # Main landing gear position away from the nose
# pos_frontwing, pos_backwing = 0.5, 7    # positions of the wings away from the nose

# mass_per_prop = 480 / n_prop
# m_prop = [mass_per_prop] * n_prop       # list of mass of engines (so 30 kg per engine with nacelle and propeller)
# # pos_prop = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0,
# #             7.0]  # 8 on front wing and 8 on back wing
# pos_prop = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0]  # 6 on front wing and 6 on back wing
# # pos_prop = [0.2, 0.2, 0.2, 0.2, 7.0, 7.0, 7.0, 7.0]  # 4 on front wing and 4 on back wing


# ------------- Initial mass estimate -------------
def mass(MTOM, S1, S2, n_ult, AR_wing1, AR_wing2, pos_frontwing, pos_backwing, Pmax, l_fus, n_pax, pos_fus,
         pos_lgear, n_prop, m_prop, pos_prop, m_pax, cargo_m):
    wing = wei.Wing(MTOM, S1, S2, n_ult, AR_wing1, AR_wing2, [pos_frontwing, pos_backwing])
    m_wf = wing.wweight1
    m_wr = wing.wweight2
    fuselage = wei.Fuselage(MTOM, Pmax, l_fus, n_pax, pos_fus)
    m_fus = fuselage.mass
    cg_fus = fuselage.pos
    lgear = wei.LandingGear(MTOM, pos_lgear)
    cg_gear = lgear.pos
    props = wei.Propulsion(n_prop, m_prop, pos_prop)
    cg_props = props.pos_prop
    m_prop = props.mass
    Mass = wei.Weight(m_pax, wing, fuselage, lgear, props, cargo_m=cargo_m, cargo_pos=6, battery_m=m_bat,
                      battery_pos=3.6, p_pax=[1.5, 3, 3, 4.2, 4.2])

    return Mass.mtom, m_wf, m_wr, m_fus, m_prop, cg_fus, cg_gear, cg_props


class RunDSE:
    def __init__(self, fixed_inputs: np.array, initial_estimates: np.array):
        """
        This class integrates all the code and runs the optimisation

                Fixed:
        Range
        Aerofoil (Clmax, Cmac, …)
        Cabin design
        Taper ratios
        Quarter-chord sweep
        Weight of propulsion system
        Constraints on wing placement and dimensions
        Change in CL on front and rear wing due to elevator
        Clearance requirements

                            Internal (first estimates):
        Loading diagram (CG position and excursion)
        Rotor diameter
        Stall speed
        Energy consumption
        Peak power
        Maximum take-off mass
        Wing mass
        Landing gear placement
        Battery mass
        MTOM

                                    Optimisation variables:
        Tail-cone length
        Wing surface area
        Aspect ratios
        Relative wing sizes
        # Battery placement
        Wing placement

        :param fixed_inputs:        These are the fixed inputs passed into the integrated code (from constants.py)
        :param initial_estimates:   These are the initial estimates for the changing internal variables, to initialise
                                    the code
        """
        # TODO: break down fixed inputs into actual inputs with self.
        self.fixed_inps = fixed_inputs
        self.initial_est = initial_estimates

    def run(self, optim_inputs, internal_inputs):
        """
        Here goes the main integration code
        It takes as inputs the optimisation variables and also estimates of its internal variables (e.g. battery mass)
        So for one set of optim inputs it results the optimisation outputs (e.g. mass and energy consumption)
        and also the internal parameters needed for iteration


        """
        # Initial estimates/
        MTOM = internal_inputs[0]
        m_bat = internal_inputs[1]
        V_cr = internal_inputs[2]
        h_cr = internal_inputs[3]
        C_L_cr = internal_inputs[4]
        CLmax = internal_inputs[5]
        prop_radius = internal_inputs[6]
        de_da = internal_inputs[7]
        Sv = internal_inputs[8]
        V_stall = internal_inputs[9]


        # Optimisation inputs
        AR_wing1 = optim_inputs[0]
        AR_wing2 = optim_inputs[1]

        # Wing areas
        S1 = optim_inputs[2]
        S2 = optim_inputs[3]
        S_tot = S1 + S2

        # Relative wing sizes in terms of area
        s1 = S1/S_tot
        s2 = S2/S_tot

        l3_fus = optim_inputs[4]
        l_fus = l1_fus + l2_fus + l3_fus

        # Positions of the wings [horizontally, vertically]
        pos_front_wing = [optim_inputs[5], optim_inputs[6]]
        pos_back_wing = [optim_inputs[7], optim_inputs[8]]

        # Distances (positive if back wing is further aft and higher)
        wing_distance_hor = pos_back_wing[0] - pos_front_wing[0]
        wing_distance_ver = pos_back_wing[1] - pos_front_wing[1]

        # ----------- Get atmospheric values at cruise --------------
        ISA = at.ISA(h_cr)
        rho = ISA.density()             # Density
        a = ISA.soundspeed()            # Speed of sound
        dyn_vis = ISA.viscosity_dyn()   # Dynamic viscosity

        M = V_cr / a                    # Cruise Mach number


        # Aero TODO get wing distance from stability
        wing_design = wingdes.wing_design(AR_wing1, AR_wing2, s1, 0, s2, 0, M, S_tot, wing_distance_hor,
                                          wing_distance_ver, w_fus, h_wt_1, h_wt_2, const.k_wl)

        # [b2, c_r2, c_t2, c_MAC2, y_MAC2, X_LEMAC2]
        wing_plan_1, wing_plan_2 = wing_design.wing_planform_double()

        # ------ Drag ------
        Afus = np.pi * np.sqrt(w_fus * h_fus)**2 / 4

        # Airfoil characteristics
        airfoil_stats = airfoil.airfoil_stats()

        drag = drag_comp.componentdrag('tandem', S_tot, l1_fus, l2_fus, l3_fus, np.sqrt(w_fus * h_fus), V_cr, rho,
                                       wing_plan_1[3], AR_wing1, AR_wing2, M, const.k, const.flamf, const.flamw, dyn_vis, const.tc,
                                       const.xcm, 0, wing_design.sweep_atx(0)[0], fus_upsweep, wing_plan_1[2],
                                       wing_distance_ver, const.IF_f, const.IF_w, const.IF_v, airfoil_stats[2],
                                       const.Abase, Sv, s1, s2, h_wt_1, h_wt_2, const.k_wl)


        taper = wing_plan_1[2] / wing_plan_1[1]

        CDs = drag.CD(CLmax)  # 1.7 init estimate
        CDs_f = drag.CD0_f
        CDs_w = CDs - CDs_f

        # CL_max TODO: get de_da from stability
        alpha_wp = 1    # If we only want CLmax (and not slope) this does not matter
        CLmax = wing_design.CLa_wprop(T_per_eng_durings_stall, V_stall, rho, 2*prop_radius, n_prop_1, n_prop_2,
                                      const.tc, CDs_w, CDs_f, Afus, alpha_wp, de_da)

        # # Lift slope
        # CL_alpha_1 = wing_design.liftslope()
        # CL_alpha_2 = wing_design.liftslope()


        # TODO: get CL for cruise
        CD0 = drag.CD0()
        CD_cr = drag.CD(C_L=C_L_cr)

        # ----------------- Vertical drag -------------------

        # CDs = drag.CD(CLmax)
        # CDs_f = drag.CD0_f
        # CDs_w = CDs - CDs_f

        CD_a_w_v = wing_design.CDa_poststall(const.tc, CDs_w, CDs_f, Afus, 0, "wing", drag.CD)
        CD_a_f_v = wing_design.CDa_poststall(const.tc, CDs_w, CDs_f, Afus, 90, "fus", drag.CD)

        CD_vertical = CD_a_w_v + CD_a_f_v

        # Propulsion
        # Get drag at cruise
        D_cr = CD_cr * 0.5 * rho * V_cr ** 2 * S_tot

        # Size the propellers
        prop_sizing = eng_siz.PropSizing(wing_plan_1[0], w_fus, n_prop, const.c_fp, const.c_pp, MTOM, const.xi_0)

        prop_radius = prop_sizing.radius()
        prop_area = prop_sizing.area_prop()
        disk_load = prop_sizing.disk_loading()

        # act_disk = ADT.ActDisk(TW_ratio, MTOM, v_e, V_cr, D, D)
        # With fuselage shape and span we can have size of the engines
        # From that we can use BEM to design the blades (here number of blades is an input,
        # so we can optimise it if necessary, or just assume one

        # ----------------------- Performance ------------------------
        # Cl_alpha_curve, CD_a_w, CD_a_f, alpha_lst, Drag

        # post_stall = Wing_params.post_stall_lift_drag(tc, CDs, CDs_f, Afus)

        # init_sizing = perf.initial_sizing(h_cr, None, drag, V_stall, V_max, n_turn, ROC, V_cr, ROC_hover, MTOM * g0,
        #                                   CD_vertical, const.eff_prop, const.eff_hover, disk_load)

        # TODO: maybe use S as an inout and not size for stall
        # # Get wing loading and from that the area
        # WS = init_sizing.sizing()[0]
        #
        # S_tot = MTOM * g0 / WS

        # S1, S2 = S_tot * s1, S_tot * s2

        V = at.speeds(h_cr, MTOM, CLmax, S_tot, drag)

        # Cruise speed
        V_cr, CL_cr_check = V.cruise()

        # Update the stall speed
        V_stall = V.stall()

        # print("CL comparison:", CL_cr_check, C_L_cr, V_cr)

        # Cruise CL of the wings
        L_cr = MTOM * g0
        L_cr_1 = L_cr / 2
        L_cr_2 = L_cr / 2

        CL_cr_1 = 2 * L_cr_1 / (rho * V_cr ** 2 * S1)
        CL_cr_2 = 2 * L_cr_2 / (rho * V_cr ** 2 * S2)
        C_L_cr = CL_cr_2

        # Aero to pass to mission
        alpha_lst = np.arange(0, 89, 0.1)
        Cl_alpha_curve = wing_design.CLa(const.tc, CDs, CDs_f, Afus, alpha_lst, de_da)
        CD_a_w = wing_design.CDa_poststall(const.tc, CDs, CDs_f, Afus, alpha_lst, "wing", drag.CD, de_da)
        CD_a_f = wing_design.CDa_poststall(const.tc, CDs, CDs_f, Afus, alpha_lst, "fus", drag.CD, de_da)

        # Energy sizing TODO: change inputs
        mission = FP.mission(MTOM, h_cr, V_cr, CLmax, S_tot, n_prop * prop_area, P_max = max_power, t_loiter = 30*60,
                             rotational_rate=5, mission_dist = mission_range)

        # Get approximate overall efficiency
        mission.total_energy()
        eff_overall = 0.91 * 0.57 + 0.699 * 0.43 # TODO adapt
        energy = mission.total_energy()[0] * 2.77778e-7 * 1000 / eff_overall  # From [J] to [Wh]
        # TODO: check safety factor (1.02 *)

        # Engine sizing

        # Maximum power [W] and thrust [N] of the engines (total)
        time, P_max_eng_tot, T_max_tot = mission.total_energy()[1:4]
        P_max_eng_ind = P_max_eng_tot/n_prop                    # Maximum power [W] of the engines (per engine)
        P_max_bat = P_max_eng_tot/const.eff_eng_bat             # Maximum power [W] to be delivered by the battery

        T_max_ind = T_max_tot/n_prop                # Maximum thrust to be delivered by the engines (per engine)

        # Battery sizing
        sp_en_den = const.sp_en_den
        vol_en_den = const.vol_en_den
        batt_cost = const.bat_cost
        DoD = const.DoD
        P_den = const.P_den
        safety_factor = 1  # TODO: discuss
        EOL_C = const.EOL_C

        # sp_en_den, vol_en_den, tot_energy, cost, DoD, P_den, P_max, safety, EOL_C
        battery = batt.Battery(sp_en_den, vol_en_den, energy, batt_cost, DoD, P_den, P_max_bat, safety_factor, EOL_C)

        m_bat = battery.mass()

        # The mass of one engine is the specific mass of the engines (kg/W) x Total power of ONE ENGINE
        m_prop = const.sp_mass_en * P_max_eng_ind


        # -------------------- Update weight ------------------------
        pos_fus = l_fus/2  # TODO: revise approximation
        pos_prop_front = [pos_front_wing] * n_prop_1
        pos_prop_back = [pos_back_wing] * n_prop_2

        pos_prop = np.hstack((np.array(pos_prop_front), np.array(pos_prop_back)))

        # TODO get LG pos from stability
        MTOM, m_wf, m_wr, m_fus, m_prop, cg_fus, cg_gear, cg_props = mass(MTOM, S1, S2, n_ult, AR_wing1, AR_wing2,
                                                                          pos_front_wing, pos_back_wing, Pmax_weight,
                                                                          l_fus, const.n_pax, pos_fus, pos_lgear,
                                                                          n_prop, m_prop, pos_prop, const.m_pax,
                                                                          const.m_cargo_tot)

        # ----------------- Stability and control -------------------
        # TODO: add numbers
        # W = 2950 * 9.80665
        # h = 1000
        # lfus = 7.2
        # hfus = 1.705
        # wfus = 1.38
        # xcg = 3.0
        # V0 = 64.72389428906716
        # Vstall = 40
        # Pbr = 110024 / 1.2 * 0.9 / 12
        # # M0 = V0 / np.sqrt(const.gamma * const.R * 288.15)
        # CD0 = 0.03254
        # CLfwd = 1.44333 # Maximum lift coefficient of forward wing
        # CLrear = 1.44333 # Maximum lift coefficient of rear wing
        # CLdesfwd = 0.7382799 # Design lift coefficient of forward wing for cruise
        # CLdesrear = 0.7382799 # Design lift coefficient of rear wing for cruise
        # CLafwd = 5.1685 # Lift slope of forward wing
        # Clafwd = 6.1879 # Airfoil lift slope (fwd wing)
        # Clarear = Clafwd # Airfoil lift slope (rear wing)
        # Cd0fwd = 0.00347  # Airfoil drag coefficient [-]
        # Cd0rear = Cd0fwd
        # CD0fwd = 0.00822  # Wing drag coefficient [-]
        # CD0rear = CD0fwd
        # Cmacfwd = -0.0645 # Pitching moment coefficient at ac [-] (fwd wing)
        # Cmacrear = -0.0645 # Pitching moment coefficient at ac [-] (rear wing)
        # Sfwd = 8.417113787320769 # Forward wing surface area [m^2]
        # Srear = 8.417113787320769 # Rear wing surface area [m^2]
        # taperfwd = 0.45
        # taperrear = 0.45
        # S = Srear + Sfwd
        # Afwd = 9 * 1
        # Arear = 9
        # Gamma = 0
        # Lambda_c4_fwd = 0.0 * np.pi / 180 # Sweep at c/4 [rad]
        # Lambda_c4_rear = 0.0 * np.pi / 180
        # cfwd = 1.014129367767935
        # crear = 1.014129367767935
        # c = Srear / S * crear + Sfwd / S * cfwd
        # bfwd = np.sqrt(Sfwd * Afwd)
        # brear = np.sqrt(Srear * Arear)
        # b = max(bfwd, brear)
        # print(b)
        # e = 1.1302
        # efwd = 0.958 # Span efficiency factor of fwd wing
        # erear = 0.958 # Span efficiency factor of rear wing
        # taper = 0.45
        # n_rot_f = 6
        # n_rot_r = 6
        # rot_y_range_f = [0.5 * bfwd * 0.1, 0.5 * bfwd * 0.9]
        # rot_y_range_r = [0.5 * brear * 0.1, 0.5 * brear * 0.9]
        # K = 4959.86
        # ku = 0.1
        # Zcg = 0.70 # TALK ABOUT STRUCTURES FOR BETTER ESTIMATE
        # elev_fac = 1.4
        # Vr_Vf_2 = 0.90 # TO BE CHANGED -> AERODYNAMICS
        # # crmaxf, crmaxr MAXIMUM root chord lengths of both wings [m]
        # # bmaxf, bmaxr MAXIMUM span lengths of both wings [m]
        # # Arangef, Aranger max and min values of Aspect ratio [-]
        # # xcg_range most front based on loading diagram
        # # max_thrust: total maximum that can be achieved in hover
        # #  x_wf = x_wf, x_wr = x_wr: x-location of rotors approx aerodynamic centers
        # # cg_pax, cg_pil, cg_wf, cg_wr: cg locations of passengers, pilot, front wing and rear wing

        # Hover controllability
        HoverControlCalcTandem(MTOM, n_rot_f = n_prop_1, n_rot_r = n_prop_2, x_wf = x_wf, x_wr = x_wr,
                               rot_y_range_f=[w_fus/2 + const.c_fp + prop_radius, wing_plan_1[0]],
                               rot_y_range_r=[w_fus/2 + const.c_fp + prop_radius, wing_plan_2[0]],
                               K = max_thrust/n_prop, ku = 0.1)

        # x_cg limit

        # Optimize the wing size and aspect ratios for stability and control, ignoring the stability constraint for now
        [Af, Ar, xf, xr, zf, zr, Sr_Sf]  = optimise_wings(Cmacfwd, Cmacrear, CLfwd, CLrear, CLdesfwd, CLdesrear, CD0fwd, CD0rear,
                                                          taperfwd, taperrear, Lambda_c4_fwd, Lambda_c4_rear, efwd, erear, Clafwd, Clarear,
                                                          Zcg, Vr_Vf_2, elev_fac, rho, Pbr, S, W, xrangef,
                                                          xranger, zrangef, zranger, crmaxf, crmaxr, bmaxf, bmaxr,
                                                          Arangef, Aranger, xcg_range, impose_stability=False)

        # Loading diagram
        cg_calc = CgCalculator(m_wf, m_wr, m_fus, m_bat, const.m_cargo_tot, const.m_pax, const.m_pax,
                               cg_fus, cg_bat = const.l_nosecone, cg_cargo = const.cargo_pos, cg_pax, cg_pil)

        # Get the cg range, based on wing placement, the loading order can be changed if needed
        [x_front, x_aft], _, [_, z_top] = cg_calc.calc_cg_range(cg_wf, cg_wr)

        # Landing gear placement
        # TODO: Check if origin of coordinate system starts at ground or bottom of the aircraft
        h_bottom = 0
        gears = LandingGearCalc(1.5*w_fus, x_ng_min = 0.3, y_max_rotor = wing_plan_1[0],
                                gamma = np.radians(5), z_rotor_line_root = pos_front_wing[1] + h_bottom,
                                rotor_rad = prop_radius,
                                fus_back_bottom = const.fus_back_bottom, fus_back_top = const.fus_back_top)

        x_ng, x_mlg, track_width, z_mlg = gears.optimum_placement([x_front, x_aft], x_cg_margin = 0,
                                                                  z_cg_max = z_top, theta = const.pitch_lim,
                                                                  phi = const.lat_lim, psi = const.turn_over,
                                                                  min_ng_load_frac = const.min_ng_load)


        # TODO update array with the final updated values
        internal_inputs = [MTOM, m_bat, V_cr, h_cr, C_L_cr, CLmax, prop_radius, de_da, Sv]

        # Outputs for optimisation cost function
        optim_outputs = [MTOM, energy, time]

        return optim_outputs, internal_inputs

    def multirun(self, N_iters, optim_inputs):
        """
        With this you can run the integrated code as many times as you want per optimisation, so that you get internal
        convergence of the internal parameters

        :param N_iters: Number of iterations of the code for each optimisation iteration
        """
        internal_inputs = self.initial_est

        for i in range(N_iters):
            optim_outputs, internal_inputs = self.run(optim_inputs, internal_inputs)

        return optim_outputs, internal_inputs
