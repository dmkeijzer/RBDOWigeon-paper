from Flight_performance_final import mission, evtol_performance, Drag
from Aero_tools import speeds

# TODO: Change later
from Preliminary_Lift.main_aero import Cl_alpha_curve, CD_a_w, CD_a_f, alpha_lst, Drag

# ========== Inputs ==========
# TODO: Make consistent with the sizing done in midterm new
mass = 2300
cruising_alt = 300
cruise_speed = 62
CL_max = 1.7
wing_surface = 14
EOM = 1500
A_disk = 8
P_max  = 1.4e6

# Energy estimation and plotting
mission_profile = mission(mass, cruising_alt, cruise_speed, CL_max, wing_surface, A_disk = A_disk, P_max = P_max,
                          plotting = True)

E_tot, t_tot, max_power = mission_profile.total_energy()

print('Total energy', E_tot/1e6, 'MJ')
print("Total time", t_tot/3600, 'hr')
print("Max power", max_power/1e3, 'kW')

# Other performance estimates
performance = evtol_performance(cruising_alt, cruise_speed, wing_surface, CL_max, mass, battery_capacity = E_tot,
                                EOM = EOM, A_disk = A_disk, P_max = P_max, loiter_time = 30*60)

# Performance things
performance.power_polar(cruising_alt)
V_climb = performance.climb_performance()
performance.vertical_climb()
performance.payload_range()

# Optimal speeds
V = speeds(cruising_alt, mass, CL_max, wing_surface, Drag)

print("===== Optimal speeds =====")
print("Stall speed:", V.stall())
print("Cruise speed:", V.cruise()[0])
print("Climb speed:", V_climb)
