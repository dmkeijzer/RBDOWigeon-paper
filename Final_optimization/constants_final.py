import numpy as np

# Physics
g = 9.80665                 # [m/s^2]
gamma = 1.4                 # [-]
R = 287                     # [J/kg/K]
rho_0 = 1.225               # [kg/m^3]

# General
n_pax = 5                               # Number of passengers
m_pax = 88                              # Max per pax
m_cargo_per_pax = 7                     # [kg] Cargo mass per pax
m_cargo_tot = m_cargo_per_pax*n_pax     # [kg] Total cargo mass

cargo_pos = 6       # [m] Cargo position

# Fuselage
w_fuselage = 1.38           # [m]
h_fuselage = 1.7            # [m]
l_nosecone = 2.5            # [m]
l_cylinder = 2              # [m]
# l_tailcone = 2.7            # [m]
upsweep = 8.43*np.pi/180    # [Degrees]

# Aerodynamics
# s1 = 0.5                    # Fraction of total wing area for the 1st wing [-]
# s2 = 1-s1                   # Fraction of total wing area for the 2nd wing [-]
sweepc41 = 0                # Sweep angle at quarter chord for 1st wing [rad]
sweepc42 = 0                # Sweep angle at quarter chord for the 2nd wing
k = 0.634 * 10**(-5)        # Smooth paint from adsee 2 L2  smoothness factor[-]
flamf = 0.1                 # From ADSEE 2 L2 GA aircraft [-]
IF_f = 1                    # From ADSEE 2 L2 Interference factor fuselage [-]
IF_w = 1.1                  # From ADSEE 2 L2 Interference factor wing [-]
IF_v = 1.04                 # From ADSEE 2 L2 Interference factor vertical tail [-]
flamw = 0.35                # From ADSEE 2 L2 GA aircraft
Abase = 0                   # Base area of the fuselage [m2]
tc = 0.12                   # NACA0012 for winglets and Vtail [-]
xcm = 0.3                   # NACA0012 for winglets and Vtail [-]
k_wl = 2.4                  # Constant for winglets (could be changed to 2 if we need extra eff)
Vr_Vf_2 = 1                 # Speed ratio between wing 1 and 2
e_f = 0.65                  # Oswald efficiency for front wing
e_r = 0.65                  # Oswald efficiency for rear wing

# Propulsion
xi_0 = 0.1         # Dimensionless radius of the hub (r_hub/R)
c_fp = 0.3         # [m] Horizontal clearance between the widest part of the fuselage and the radius of the inboard prop
c_pp = 0.3         # [m] Horizontal clearance between the propellers (closest point, tip to tip)
eff_prop = 0.83    # [-] Propeller efficiency during normal flight
eff_hover = 0.88   # [-] Propeller efficiency during hover
# TODO: revise
eff_eng_bat = 0.7  # [-] Efficiency from batteries to engines (including engine, battery, and electronics efficiencies)
sp_mass_en = 1/3500     # [kg/W] TODO: placeholder

# Power
sp_en_den = 450     # [Wh/kg] Specific energy density
vol_en_den = 900    # [Wh/l] Volumetric energy density
bat_cost = 100      # [$/kWh] Cost of batteries in US dollars per kilogram
DoD = 0.8           # [-] Depth of Discharge of the total battery
P_den = 10000       # [W/kg] Power density of battery
EOL_C = 0.8         # [-] Fraction of initial capacity that is available at end-of-life

# Stability
fus_back_bottom = []
fus_back_top = []
turn_over = np.radians(55)      # Turn-over angle
pitch_lim = np.radians(20)      # Pitch limit
lat_lim = np.radians(20)        # lateral ground clearance angle
min_ng_load = 0.1               # minimum fraction of the total weight to be carried by the nose gear

