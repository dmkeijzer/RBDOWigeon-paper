import battery as bat
import Propulsion as prop
from constants import *


# Li_ion = bat.Battery(300, 200, 1)

# Define values for parameters
D_inner_ratio = 0.10  # ratio of inner diameter compared to outer diameter
TWRatio = 1.4
V_e_LTO = 240/3.6
D_prop_pure_hover = 2

ActDisk = prop.ActuatorDisk(D_inner_ratio,TWRatio,V_e_LTO,D_prop_pure_hover)

# ActDisk = ActuatorDisk(D_inner_ratio, n_prop,TWRatio,V_e_LTO)
print("Required total area for hover", ActDisk.A_hover(), "[m**2]")
print("Required diameter per prop is", ActDisk.D_prop_outer(),"[m] for the cruise props")
print("There are",N_hover,"propellers, of which",N_hover - N_cruise,"are purely for hover")
print("Exit speed in cruise:", ActDisk.V_e_cruise(), "[m/s]")
print("Ideal power for cruise:", ActDisk.P_ideal(), "[W]")
print("Efficiency in cruise:", ActDisk.eff(), "[-]")

