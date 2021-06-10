import numpy as np
import Aero_tools as at
import constants_final as const

# Aero
import Preliminary_Lift.Drag as drag
import Preliminary_Lift.Wing_design as wingop
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
def init_mass(MTOM, S1, S2, n_ult, AR_wing1, AR_wing2, pos_frontwing, pos_backwing, Pmax, l_fus, n_pax, pos_fus,
              pos_lgear, n_prop, m_prop, pos_prop, m_pax):
    wing = wei.Wing(MTOM, S1, S2, n_ult, AR_wing, [pos_frontwing, pos_backwing])
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

        Range
        Aerofoil (Clmax, Cmac, …)
        Cabin design
        Taper ratios
        Quarter-chord sweep
        Weight of propulsion system
        Constraints on wing placement and dimensions
        Change in CL on front and rear wing due to elevator
        Clearance requirements
        """

        return optim_outputs, internal_inputs

    def multirun(self, N_iters):
        """
        With this you can run the integrated code as many times as you want per optimisation, so that you get internal
        convergence of the internal parameters

        :param N_iters: Number of iterations of the code for each optimisation iteration
        """
        internal_inputs = self.initial_est
        for i in range(N_iters):
            optim_outputs, internal_inputs = self.run(internal_inputs)
        return optim_outputs, internal_inputs