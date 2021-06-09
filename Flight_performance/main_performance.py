from Flight_performance_final import mission, evtol_performance
from Aero_tools import speeds


# ========== Inputs ==========
# TODO: Make consistent with the sizing done in midterm new
mass = 2600
cruising_alt = 1000
cruise_speed = 62
CL_max = 1.7
wing_surface = 14
EOM = 2000
battery_capacity = 400e6

# Energy estimation and plotting
mission_profile = mission(mass, cruising_alt, cruise_speed, CL_max, wing_surface, plotting = True)

E_tot, t_tot = mission_profile.total_energy()

# Other performance estimates
performance = evtol_performance(cruising_alt, cruise_speed, wing_surface, CL_max, mass, battery_capacity, EOM,
                                loiter_time = 30*60)

# Performance things
performance.climb_performance()
performance.vertical_climb()
performance.payload_range()
