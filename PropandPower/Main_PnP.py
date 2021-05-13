import battery as bat
import Propulsion as prop
from constants import *
import ActuatorDisk as AD
import numpy as np

g0 = 9.80665

# Li_ion = bat.Battery(300, 200, 1)

# Define values for parameters
# # D_inner_ratio = 0.10  # ratio of inner diameter compared to outer diameter
# D_prop_pure_hover = 0.6  # ratio of pure hover prop (just config 3) compared to root chord.
#
# ActDisk = prop.ActuatorDisk(D_inner_ratio, D_prop_pure_hover)
#
# # ActDisk = ActuatorDisk(D_inner_ratio, n_prop,TWRatio,V_e_LTO)
# print("Required total area for hover", ActDisk.A_hover(), "[m**2]")
# print("Required diameter per prop is", ActDisk.D_prop_outer(), "[m] for the cruise props")
# if N_cruise != N_hover:
#     D_hover = D_prop_pure_hover * c_r
#     print("Diameter dedicated hover engines:", D_hover, "[m]")
# print("There are", N_hover, "propellers, of which", N_hover - N_cruise, "are purely for hover")
# print()
# print("Exit speed in cruise:", ActDisk.V_e_cruise(), "[m/s]")
# print("Ideal power for cruise:", ActDisk.P_ideal(), "[W]")
# print("Actual power for cruise:", ActDisk.P_actual(), "[W]")
# print("Efficiency in cruise:", ActDisk.eff(), "[-]")

disk = AD.ActDisk(TW_ratio, MTOW/g0, V_e_LTO, V_cruise, MTOW/LD_ratio, D_loading)

# print("Max take-off mass:", MTOW/g0)
# print("Total disk area:", disk.A_disk(), "[m^2]")
print("Total disk area from DL:", disk.A, "[m^2]")
# print("Equivalent radius for one propeller:", np.sqrt(disk.A_disk()/np.pi), "[m]")
print("Equivalent radius for one propeller (from Disk Loading):", np.sqrt(disk.A/np.pi), "[m]")
print("Propeller exit speed at hover:", disk.v_e_hover(), "[m/s]")
# print("Disk area per propeller:", disk.A_disk()/N_hover, "[m^2]")
# r_out = np.sqrt((disk.A_disk()/N_hover) / (np.pi*(1-D_inner_ratio**2)))
print("Disk area per propeller:", disk.A/N_hover, "[m^2]")
r_out = np.sqrt((disk.A/N_hover) / (np.pi*(1-D_inner_ratio**2)))
print("Outer radius of the propellers:", r_out, "[m]")
print("Hub radius of propellers:", r_out*D_inner_ratio, "[m]")
print("Cruise speed:", V_cruise, "[m/s]")
# print("v0 for hover:", disk.v_0_hover(), "[m/s]")
print("Jet speed cruise:", disk.v_e_cr(), "[m/s]")
print("Cruise propulsive efficiency:", disk.eff_cruise(), "[-]")
print("Ideal power for cruise:", disk.P_ideal(), "[W]")
print("Actual power for cruise:", disk.P_actual(), "[W]")
