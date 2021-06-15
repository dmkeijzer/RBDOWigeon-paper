import integration_class as int_class

MTOM = internal_inputs[0]
V_cr = internal_inputs[2]
h_cr = internal_inputs[3]
C_L_cr = internal_inputs[4]
CLmax = internal_inputs[5]
prop_radius = internal_inputs[6]
de_da = internal_inputs[7]
Sv = internal_inputs[8]
V_stall = internal_inputs[9]
max_power = internal_inputs[10]
AR_wing1 = internal_inputs[11]
AR_wing2 = internal_inputs[12]
Sr_Sf = internal_inputs[13]
s1 = internal_inputs[14]

# Positions of the wings [horizontally, vertically]
xf = internal_inputs[15]
zf = internal_inputs[16]
xr = internal_inputs[17]
zr = internal_inputs[18]

# Spans
b1 = internal_inputs[19]
b2 = internal_inputs[20]

# Initial estimates for the variables
initial_estimate = [MTOM, 0, V_cr, h_cr, C_L_cr, CLmax, prop_radius, de_da, Sv, V_stall, max_power, AR_wing1,
                   AR_wing2, Sr_Sf, s1, xf, zf, xr, zr, b1, b2]

# Optimisation class
optimisation_class = int_class.RunDSE(initial_estimate)

# Run the file for # iterations
N_iter = 10
optim_outputs, internal_inputs, other_outputs = optimisation_class.multirun(N_iter, [])
