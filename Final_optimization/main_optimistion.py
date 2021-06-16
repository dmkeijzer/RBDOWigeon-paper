import integration_class_ar_input as int_class

# Initial estimates
MTOM = 3000
V_cr = 75
h_cr = 1000
C_L_cr = 0.8
CLmax = 1.7
prop_radius = 0.55
de_da = 0.25
Sv = 1.1
V_stall = 40
max_power = 2000000
AR_wing1 = 10
AR_wing2 = 10
Sr_Sf = 1
s1 = 0.5

# Positions of the wings [horizontally, vertically]
xf = 0.5
zf = 0.3
xr = 7
zr = 1.7

# Spans
b1 = None
b2 = None

# Initial estimates for the variables
initial_estimate = [MTOM, 0, V_cr, h_cr, C_L_cr, CLmax, prop_radius, de_da, Sv, V_stall, max_power, AR_wing1,
                    AR_wing2, Sr_Sf, s1, xf, zf, xr, zr, b1, b2,  # Parameters used to replace wing_optimization:
                    ]

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
