import numpy as np
import matplotlib.pyplot as plt
import redundancy_battery_config as con

# Characteristics from the plane
V_motor = 500  # V
E_tot = 301.1111  # kWh
per_mot = 0.99
n_mot = 12  # Number of motors in aircraft
n_bat_mot = 2  # Number of batteries per motor

def Sens_C_cell(V_motor, E_tot, per_mot, n_mot, n_bat_mot, V_cell, c_lower, c_upper, n_calc):
    abs_incr_ar = np.zeros(n_calc)
    C_ar = np.linspace(c_lower, c_upper, n_calc)
    per_incr_ar = np.zeros(n_calc)

    for i, C in enumerate(C_ar):
        red = con.redundancy_power(V_motor, E_tot, V_cell, C, n_mot, n_bat_mot, per_mot)
        C_ar[i] = C
        abs_incr_ar[i] = red.increase()[0]
        per_incr_ar[i] = red.increase()[1]

    plt.plot(C_ar, per_incr_ar)

    plt.xlabel('Cell capacity [Ah]')
    plt.ylabel('Increase in cell count [-]')
    # plt.grid()
    plt.tight_layout(pad=0.05)
    # plt.savefig(self.path + 'time_sensitivity_altitude' + '.pdf')
    plt.show()

def Sens_V_cell(V_motor, E_tot, per_mot, n_mot, n_bat_mot, C_cell, V_lower, V_upper, n_calc):
    abs_incr_ar = np.zeros(n_calc)
    V_ar = np.linspace(V_lower, V_upper, n_calc)
    per_incr_ar = np.zeros(n_calc)

    for i, V in enumerate(V_ar):
        red = con.redundancy_power(V_motor, E_tot, V, C_cell, n_mot, n_bat_mot, per_mot)
        V_ar[i] = V
        abs_incr_ar[i] = red.increase()[0]
        per_incr_ar[i] = red.increase()[1]

    plt.plot(V_ar, per_incr_ar)

    plt.xlabel('Cell nominal voltage [V]')
    plt.ylabel('Increase in cell count [-]')
    # plt.grid()
    plt.tight_layout(pad=0.05)
    # plt.savefig(self.path + 'time_sensitivity_altitude' + '.pdf')
    plt.show()

sen_C = False
sen_V = True

if sen_C == True:
    n_calc = int(1E3)
    c_lower = 1
    c_upper = 7
    V_cell = 3.7  # V
    Sens_C_cell(V_motor, E_tot, per_mot, n_mot, n_bat_mot, V_cell, c_lower, c_upper, n_calc)

if sen_V == True:
    n_calc = 10000
    V_lower = 1.5
    V_upper = 7
    C_cell = 5  # Ah
    Sens_V_cell(V_motor, E_tot, per_mot, n_mot, n_bat_mot, C_cell , V_lower, V_upper, n_calc)