import sys
import matplotlib.pyplot as plt
import numpy as np
from performance_analysis import mission_analysis, initial_sizing

sys.path.append("../data/")

# Initial data
cruising_alt    = 400           # [m] Estimated cruising altitude
energy          = 100*3.6e6     # [J] Energy capacity of the aircraft
data_path       = "../data/inputs_config_1.json"

# ================== Run the initial sizing ====================
perf = initial_sizing(cruising_alt, data_path)
WS, WP = perf.sizing()
perf.testing()

# ======================== Climb chart =========================
climb_analysis  = mission_analysis(data_path, cruising_alt, 360, energy)
climb_analysis.climb_perf_chart()

# ===== Energy needed and distribution for normal mission ======
Energy_analysis  = mission_analysis(data_path, cruising_alt, 360, energy, save_data = True)
E_tot = Energy_analysis.total_energy(300e3, pie = True)
print("Total energy needed: ", E_tot, "J")
# ================= Payload range diagram ======================
# Range of payloads
m_PL        = np.arange(0, 400, 10)
analysis    = mission_analysis(data_path, cruising_alt, m_PL, energy)

# Different weight breakdowns
tot_weight      = analysis.W
empty_weight    = analysis.EOW
max_weight      = analysis.MTOW
payload_weight  = m_PL*9.81

ranges = analysis.range()/1e3

plt.plot(ranges, tot_weight)
plt.plot(ranges, np.ones(np.size(tot_weight))*empty_weight, color = 'black')
plt.plot(ranges, np.ones(np.size(tot_weight))*max_weight, color = 'black')
plt.fill_between(ranges, np.ones(np.size(tot_weight))*empty_weight, np.zeros(np.size(tot_weight)), color = 'red',
                 alpha = 0.5)
plt.fill_between(ranges, np.ones(np.size(tot_weight))*max_weight, np.ones(np.size(tot_weight))*1e9, color = 'red',
                 alpha = 0.5)

plt.ylim(0.98*empty_weight, 1.02*max_weight)
plt.xlim(min(ranges), max(ranges))
plt.ylabel('Aircraft weight [N]')
plt.xlabel('Cruise range [km]')
plt.grid()
plt.show()
