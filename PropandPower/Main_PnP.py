import battery as bat
import Propulsion as prop
from constants import *


# Li_ion = bat.Battery(300, 200, 1)

# Define values for parameters
D_inner_ratio = 0.10  # ratio of inner diameter compared to outer diameter
D_prop_pure_hover = 0.6  # ratio of pure hover prop (just config 3) compared to root chord.

ActDisk = prop.ActuatorDisk(D_inner_ratio, D_prop_pure_hover)

# ActDisk = ActuatorDisk(D_inner_ratio, n_prop,TWRatio,V_e_LTO)
print("Required total area for hover", ActDisk.A_hover(), "[m**2]")
print("Required diameter per prop is", ActDisk.D_prop_outer(), "[m] for the cruise props")
if N_cruise != N_hover:
    D_hover = D_prop_pure_hover * c_r
    print("Diameter dedicated hover engines:", D_hover, "[m]")
print("There are", N_hover, "propellers, of which", N_hover - N_cruise, "are purely for hover")
print()
print("Exit speed in cruise:", ActDisk.V_e_cruise(), "[m/s]")
print("Ideal power for cruise:", ActDisk.P_ideal(), "[W]")
print("Efficiency in cruise:", ActDisk.eff(), "[-]")

