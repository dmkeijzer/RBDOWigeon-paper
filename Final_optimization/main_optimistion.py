import integration_class_ar_input as int_class
import constants_final as const

# Initial estimates
MTOM = 2800
V_cr = 66
h_cr = 1000
C_L_cr = 0.8
CLmax = 1.68
prop_radius = 0.55
de_da = 0.25
Sv = 1.1
V_stall = 40
max_power = 1.5e6
AR_wing1 = 8
AR_wing2 = 9
Sr_Sf = 1.7
s1 = (1 + Sr_Sf)**-1

# Positions of the wings [horizontally, vertically]
xf = 0.5
zf = 0.3
xr = 6

zr = 1.7
max_thrust_stall = MTOM*const.g

# Initial estimates for the variables
initial_estimate = [MTOM, 0, V_cr, h_cr, C_L_cr, CLmax, prop_radius, de_da, Sv, V_stall, max_power, AR_wing1,
                    AR_wing2, Sr_Sf, s1, xf, zf, xr, zr, max_thrust_stall]

# Optimisation class
optimisation_class = int_class.RunDSE(initial_estimate)

# Run the file for # iterations
N_iter = 10
optim_outputs, internal_inputs, other_outputs = optimisation_class.multirun(N_iter, optim_inputs=[])

print(optim_outputs)
print("")
print(internal_inputs)
print("")
print(internal_inputs)
