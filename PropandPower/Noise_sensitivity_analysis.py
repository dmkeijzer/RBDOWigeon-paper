import Noise as brr
from constants import *
import Aero_tools as at
import numpy as np
import ActuatorDisk as AD

# ISA
g0 = 9.80665
ISA = at.ISA(h_cruise)
a = ISA.soundspeed()

disk = AD.ActDisk(TW_ratio, MTOW/g0, V_e_LTO, V_cruise, MTOW/LD_ratio, D_loading)

if Prop_config == 1 or Prop_config == 2:
    disk_A_per_prop = disk.A/N_hover
    print("Disk area per propeller:", disk_A_per_prop, "[m^2]")
    r_out = np.sqrt(disk_A_per_prop / (np.pi*(1-D_inner_ratio**2)))
    print("Outer radius of the propellers:", r_out, "[m]")
    print(" ")

# Engine sizing for config 3:
xc_wing_eng_start = 0.2
xc_wing_eng_end = 0.8
xb_wing_eng_start = 0.2
taper = c_t/c_r
b = np.sqrt(2*AR*S_front)

if Prop_config == 3:
    r_out_wing_eng = ((xc_wing_eng_end-xc_wing_eng_start)*c_r/2 - (xc_wing_eng_end-xc_wing_eng_start)*(1-taper)*c_r*xb_wing_eng_start/2) / \
                     (1 + 2*(xc_wing_eng_end-xc_wing_eng_start)*(1-taper)/b**2)
    print("The outer radius of the wing propeller is:", r_out_wing_eng, "[m]")

    wing_prop_hub_ratio = 0.2
    area_wing_prop = np.pi * (r_out_wing_eng**2 - (wing_prop_hub_ratio*r_out_wing_eng)**2)
    area_tilt_eng = (disk.A - 2*area_wing_prop)/4
    r_out = np.sqrt(area_tilt_eng / (np.pi * (1 - D_inner_ratio**2)))
    print("The outer radius of each of the tilting engines is:", r_out, "[m]")


# Sensitivity study of the noise formulas
P_br_cruise = P_cr_estim/N_cruise
P_br_hover = P_hover_estim/N_hover

noise = brr.Noise(P_br_cruise, 2*r_out, num_blades, N_cruise, N_hover, rpm, a)

print("Noise level in cruise:", noise.SPL_cr())
print("Noise level in hover:", noise.SPL_hover())
