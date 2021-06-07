import Aero_tools as at
# import Drag_midterm2 as drag
import prelim_ADT as ADT
import Vertical_tail_sizing_midterm2 as vert_tail
import Weight_midterm2 as weight
# import Wing_design_midterm2 as wing
import constants as const

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

# Prelim estimate of CLmax
CLmax = 1.46916

# Constants for weight
mtom = 1972  # maximum take-off mass from statistical data - Class I estimation
S1, S2 = 5.5, 5.5  # surface areas of wing one and two
A = 14  # aspect ratio of a wing, not aircraft
n_ult = 3.2 * 1.5  # 3.2 is the max we found, 1.5 is the safety factor
# TODO: revise Pmax
Pmax = 15.25  # this is defined as maximum perimeter in Roskam, so i took top down view of the fuselage perimeter
lf = 7.2  # length of fuselage

# From project guide: 95 kg per pax (including luggage)
n_pax = 5  # number of passengers (pilot included)
m_pax = 88  # assume average mass of a passenger according to Google
cargo_m = (95-m_pax)*n_pax  # Use difference of pax+luggage - pax to get cargo mass

n_prop = 16  # number of engines

pos_fus = 3.6  # fuselage centre of mass away from the nose
pos_lgear = 4  # landing gear position away from the nose
pos_frontwing, pos_backwing = 0.5, 7  # positions of the wings away from the nose
m_prop = [30] * 16  # list of mass of engines (so 30 kg per engine with nacelle and propeller)
pos_prop = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0,
            6.7]  # 8 on front wing and 8 on back wing
wing = weight.Wing(mtom, S1, S2, n_ult, A, [pos_frontwing, pos_backwing])
fuselage = weight.Fuselage(mtom, Pmax, lf, n_pax, pos_fus)
lgear = weight.LandingGear(mtom, pos_lgear)
props = weight.Propulsion(n_prop, m_prop, pos_prop)
weight = weight.Weight(m_pax, wing, fuselage, lgear, props, cargo_m=cargo_m, cargo_pos=6, battery_m=400, battery_pos=3.6,
                p_pax=[1.5, 3, 3, 4.2, 4.2])

# TODO: implement initial mass
weight_initial = 1
iterate = True

while iterate:


    # Performance



    # Aero

    # Propulsion
    # With fuselage shape and span we can have size of the engines
    # From that we can use BEM to design the blades (here number of blades is an input, so we can optimise it if necessary,
    # or just assume one

    # Update weight

    MTOW = weight.Weight()

# Stability
# W,h,xcg,lfus,hfus,wfus,V0,Vstall,CD0,CLfwd,CLrear,CLafwd,CLarear,Sfwd,Srear,Afwd,Arear,Lambda_c4_fwd,Lambda_c4_rear,cfwd,crear,bfwd,brear,taper,ARv):
vertical_tail = vert_tail.VT_sizing()
