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
l_fus = l1_fus + l2_fus + l3_fus
h_fus = const.h_fuselage
fus_upsweep = const.upsweep


class RunDSE:
    def __init__(self, inputs: np.array):
        """
        This class integrates all the code and runs the optimisation
        """
        self.a = 1


    def run(self):



