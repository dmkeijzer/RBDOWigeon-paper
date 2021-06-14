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
import PropandPower.engine_sizing_positioning as engsiz
import PropandPower.battery as batt

# Stability and Control
import stab_and_ctrl.Vertical_tail_sizing as vert_tail

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
l_fus = l1_fus + l2_fus  # + l3_fus
h_fus = const.h_fuselage
fus_upsweep = const.upsweep

# --------------------- Initial estimates ---------------------
# Aero
CLmax = 1.46916
s1, s2 = const.s1, const.s2   # Ratio of front and back wing areas to total area
S1, S2 = 8.25, 8.25           # surface areas of wing one and two
S_tot = S1+S2                 # Total wing surface area
AR_wing = 7.5                 # Aspect ratio of a wing, not aircraft
AR_tot = AR_wing/2            # Aspect ratio of aircraft

# Wingtips
# S_wt = 0    # Surface of the winglets
h_wt_1 = 0.5  # Height of front wingtips
h_wt_2 = 0.5  # Height of back wingtips


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
clearance_fus_prop = 0.3    # Horizontal separation between the fuselage and the first propeller [m]
clearance_prop_prop = 0.3   # Horizontal separation between propellers [m]
xi_0 = 0.1                  # r/R ratio of hub diameter to out diameters [-]
m_bat = 800                 # Initial estimate for battery mass [kg]


# Structures
# TODO: Revise initial mass
MTOM = 3000         # maximum take-off mass from statistical data - Class I estimation

n_ult = 3.2 * 1.5   # 3.2 is the max we found, 1.5 is the safety factor


# Stability
S_v = 1.558     # Area of the vertical tail [m^2]
h_tail = 1.396  # Height of vertical tail [m]

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
# pos_prop = [0.2, 0.2, 0.2, 0.2, 7.0, 7.0, 7.0, 7.0]  # 4 on front wing and 4 on back wing


# ------------- Initial mass estimate -------------
def mass(MTOM, S1, S2, n_ult, AR_wing1, AR_wing2, pos_frontwing, pos_backwing, Pmax, l_fus, n_pax, pos_fus,
         pos_lgear, n_prop, m_prop, pos_prop, m_pax):
    wing = wei.Wing(MTOM, S1, S2, n_ult, AR_wing1, AR_wing2, [pos_frontwing, pos_backwing])
    fuselage = wei.Fuselage(MTOM, Pmax, l_fus, n_pax, pos_fus)
    lgear = wei.LandingGear(MTOM, pos_lgear)
    props = wei.Propulsion(n_prop, m_prop, pos_prop)
    Mass = wei.Weight(m_pax, wing, fuselage, lgear, props, cargo_m=cargo_m, cargo_pos=6, battery_m=m_bat,
                         battery_pos=3.6, p_pax=[1.5, 3, 3, 4.2, 4.2])
    return Mass.mtom


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
        Battery placement
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

        # Optimisation inputs
        AR_wing1 = optim_inputs[0]
        AR_wing2 = optim_inputs[1]
        l3_fus = optim_inputs[2]

        # ----------- Get atmospheric values at cruise --------------
        ISA = at.ISA(h_cr)
        rho = ISA.density()             # Density
        a = ISA.soundspeed()            # Speed of sound
        dyn_vis = ISA.viscosity_dyn()   # Dynamic viscosity

        M = V_cr / a  # Cruise Mach number

        # Aero
        wing_design = wingdes.wing_design(AR_tot, s1, 0, s2, 0, M, S_tot, l_fus - 1, h_fus - 0.3, w_fus, h_wt_1,
                                          h_wt_2)

        # [b2, c_r2, c_t2, c_MAC2, y_MAC2, X_LEMAC2]
        wing_plan_1, wing_plan_2 = wing_design.wing_planform_double()

        taper = wing_plan_1[2] / wing_plan_1[1]

        # CL_max TODO: de_da
        CLmax = wing_design.CLmax_s()[0]

        # # Lift slope
        # CL_alpha_1 = wing_design.liftslope()
        # CL_alpha_2 = wing_design.liftslope()

        # ------ Drag ------

        # Oswald efficiency factor
        # e = drag_comp.e_OS(AR_tot) * drag_comp.e_factor('tandem', h_fus-0.3, wing_plan_1[0], drag_comp.e_OS(AR_tot))

        # Airfoil characteristics
        airfoil_stats = airfoil.airfoil_stats()

        drag = drag_comp.componentdrag('tandem', S_tot, l1_fus, l2_fus, l3_fus, np.sqrt(w_fus * h_fus), V_cr, rho,
                                       wing_plan_1[3], AR_tot, M, const.k, const.flamf, const.flamw, dyn_vis, const.tc,
                                       const.xcm, 0, wing_design.sweep_atx(0)[0], fus_upsweep, wing_plan_1[2],
                                       h_fus - 0.3,
                                       const.IF_f, const.IF_w, const.IF_v, airfoil_stats[2], const.Abase, S_v,
                                       s1, s2, h_wt_1, h_wt_2)

        # TODO: get CL for cruise
        CD0 = drag.CD0()
        CD_cr = drag.CD(C_L=C_L_cr)

        # ----------------- Vertical drag -------------------
        Afus = np.pi * np.sqrt(w_fus * h_fus) ** 2 / 4

        CDs = drag.CD(CLmax)
        CDs_f = drag.CD0_f
        CDs_w = CDs - CDs_f

        CD_a_w_v = wing_design.CDa_poststall(const.tc, CDs_w, CDs_f, Afus, 0, "wing", drag.CD)
        CD_a_f_v = wing_design.CDa_poststall(const.tc, CDs_w, CDs_f, Afus, 90, "fus", drag.CD)

        CD_vertical = CD_a_w_v + CD_a_f_v

        # Propulsion
        # Get drag at cruise
        D_cr = CD_cr * 0.5 * rho * V_cr ** 2 * S_tot

        # Size the propellers
        prop_sizing = eng_siz.PropSizing(wing_plan_1[0], w_fus, n_prop, clearance_fus_prop, clearance_prop_prop, MTOM,
                                         xi_0)

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

        init_sizing = perf.initial_sizing(h_cr, None, drag, V_stall, V_max, n_turn, ROC, V_cr, ROC_hover, MTOM * g0,
                                          CD_vertical, const.eff_prop, const.eff_hover, disk_load)

        # TODO: maybe use S as an inout and not size for stall
        # # Get wing loading and from that the area
        # WS = init_sizing.sizing()[0]
        #
        # S_tot = MTOM * g0 / WS

        S1, S2 = S_tot * s1, S_tot * s2

        V = at.speeds(h_cr, MTOM, CLmax, S_tot, drag)

        # Cruise speed
        V_cr, CL_cr_check = V.cruise()

        # # Stall speed
        # V_stall = V.stall()

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
        Cl_alpha_curve = wing_design.CLa(const.tc, CDs, CDs_f, Afus, alpha_lst)
        CD_a_w = wing_design.CDa_poststall(const.tc, CDs, CDs_f, Afus, alpha_lst, "wing", drag.CD)
        CD_a_f = wing_design.CDa_poststall(const.tc, CDs, CDs_f, Afus, alpha_lst, "fus", drag.CD)

        # Energy sizing
        mission = FP.mission(MTOM, h_cr, V_cr, CLmax, S_tot, n_prop * prop_area, Cl_alpha_curve, CD_a_w,
                             CD_a_f, alpha_lst, drag, m_bat)

        # Get approximate overall efficiency
        eff_overall = 0.91 * 0.57 + 0.699 * 0.43
        energy = mission.total_energy()[0] * 2.77778e-7 * 1000 / eff_overall  # From [J] to [Wh]
        # TODO: check safety factor (1.02 *)

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

        # The mass of one engine is the specific mass of the engines (kg/W) x Total power of the ENGINES / number of eng
        m_prop = const.sp_mass_en * P_eng_tot / n_prop

        # -------------------- Update weight ------------------------
        # TODO mass calculation from function
        # wing = wei.Wing(MTOM, S1, S2, n_ult, AR_wing, [pos_frontwing, pos_backwing])
        # fuselage = wei.Fuselage(MTOM, Pmax, l_fus, n_pax, pos_fus)
        # lgear = wei.LandingGear(MTOM, pos_lgear)
        # props = wei.Propulsion(n_prop, m_prop, pos_prop)
        # Mass = wei.Weight(m_pax, wing, fuselage, lgear, props, cargo_m=cargo_m, cargo_pos=6, battery_m=m_bat,
        #                   battery_pos=3.6, p_pax=[1.5, 3, 3, 4.2, 4.2])
        #
        # # Initial estimate for the mass
        # MTOM = Mass.mtom

        MTOM = mass(MTOM, S1, S2, n_ult, AR_wing1, AR_wing2, pos_frontwing, pos_backwing, Pmax, l_fus, n_pax, pos_fus,
         pos_lgear, n_prop, m_prop, pos_prop, m_pax)


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
