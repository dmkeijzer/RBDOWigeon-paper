import openmdao.api as om
import numpy as np
#from stab_and_ctrl.xcg_limits import xf, xr, zf, zr, xcg_range, Arange, bmax, crmaxf, crmaxr
import constants_final as const
import integration_class_ar_input as int_class


class design_optimization(om.ExplicitComponent):

    def setup(self):

        # Design variables
        self.add_input('AR1')
        self.add_input('AR2')
        self.add_input('Sr_Sf')
        self.add_input('xr')

        # Constant inputs
        self.add_input('xf')
        self.add_input('zf')
        self.add_input('zr')
        self.add_input('max_power')
        self.add_input('MTOM')
        self.add_input('V_cr')
        self.add_input('h_cr')
        self.add_input('C_L_cr')
        self.add_input('CLmax')
        self.add_input('prop_radius')
        self.add_input('de_da')
        self.add_input('Sv')
        self.add_input('V_stall')

        # Outputs used as constraints, these come from stability
        self.add_output('mass')
        self.add_output('CM_alpha')
        self.add_output('ctrl_mar')
        self.add_output('time')
        self.add_output('MTOM_nc')
        self.add_output('Energy')

        self.add_output('Cost_func')

    def setup_partials(self):

        # Partial derivatives are done using finite difference
        self.declare_partials('*', '*', 'fd')

    def compute(self, inputs, outputs):

        MTOM = inputs['MTOM'][0]
        V_cr = inputs['V_cr'][0]
        h_cr = inputs['h_cr'][0]
        C_L_cr = inputs['C_L_cr'][0]
        CLmax = inputs['CLmax'][0]
        prop_radius = inputs['prop_radius'][0]
        de_da = inputs['de_da'][0]
        Sv = inputs['Sv'][0]
        V_stall = inputs['V_stall'][0]
        max_power = inputs['max_power'][0]
        xf = inputs['xf'][0]
        xr = inputs['xr'][0]
        zf = inputs['zf'][0]
        zr = inputs['zr'][0]

        AR_wing1 = inputs['AR1'][0]
        AR_wing2 = inputs['AR2'][0]
        Sr_Sf = inputs['Sr_Sf'][0]
        s1 = (1 + Sr_Sf)**-1
        max_thrust_stall = MTOM*const.g*0.1

        initial_estimate = [MTOM, 0, V_cr, h_cr, C_L_cr, CLmax, prop_radius, de_da, Sv, V_stall, max_power, AR_wing1,
                            AR_wing2, Sr_Sf, s1, xf, zf, xr, zr, max_thrust_stall]
        # print('Trying out optimization',initial_estimate)
        # Optimisation class
        optimisation_class = int_class.RunDSE(initial_estimate)

        # Run the file for # iterations
        N_iter = 15
        optim_outputs, internal_inputs, other_outputs = optimisation_class.multirun(N_iter, optim_inputs=[])

        # inputs['MTOM'] = internal_inputs[0]
        # inputs['V_cr'] = internal_inputs[2]
        # inputs['h_cr'] = internal_inputs[3]
        # inputs['C_L_cr'] = internal_inputs[4]
        # inputs['CLmax']  = internal_inputs[5]
        # inputs['prop_radius'] = internal_inputs[6]
        # inputs['de_da'] = internal_inputs[7]
        # inputs['Sv'] = internal_inputs[8]
        # inputs['V_stall'] = internal_inputs[9]
        # inputs['max_power'] = internal_inputs[10]
        # inputs['xf'] = internal_inputs[15]
        # inputs['xr'] = internal_inputs[17]
        # inputs['zf'] = internal_inputs[16]
        # inputs['zr'] = internal_inputs[18]

        # inputs['AR1'] = internal_inputs[11]
        # inputs['AR2'] = internal_inputs[12]
        # inputs['Sr_Sf'] = internal_inputs[13]

        print('===== Progress update =====')
        print('MTOM:        ', optim_outputs[0])
        print('MTOM (nc):   ', optim_outputs[5])
        print('CM_alpha:    ', optim_outputs[3])
        print('ctrl margin: ', optim_outputs[4])

        outputs['mass'] = optim_outputs[0]
        outputs['Energy'] = optim_outputs[1]
        outputs['time'] = optim_outputs[2]
        outputs['CM_alpha'] = optim_outputs[3]
        outputs['ctrl_mar'] = optim_outputs[4]
        outputs['MTOM_nc'] = optim_outputs[5]

        outputs['Cost_func'] = optim_outputs[1]


prob = om.Problem()
prob.model.add_subsystem('Integrated_design', design_optimization())#, promotes_inputs=['AR1',
                                                                                      # 'AR2',
                                                                                      # 'Sr_Sf',
                                                                                      # 'zr',
                                                                                      # 'xf',
                                                                                      # 'zf',
                                                                                      # 'max_power',
                                                                                      # 'MTOM',
                                                                                      # 'V_cr',
                                                                                      # 'h_cr',
                                                                                      # 'C_L_cr',
                                                                                      # 'CLmax',
                                                                                      # 'prop_radius',
                                                                                      # 'de_da',
                                                                                      # 'Sv',
                                                                                      # 'V_stall'])

# Initial values for the optimization TODO: Improve initial values
prob.model.set_input_defaults('Integrated_design.AR1', 6.8)
prob.model.set_input_defaults('Integrated_design.AR2', 6.8)
prob.model.set_input_defaults('Integrated_design.Sr_Sf', 1.)
prob.model.set_input_defaults('Integrated_design.xr', 6.1)
prob.model.set_input_defaults('Integrated_design.xf', 0.5)   # Change
prob.model.set_input_defaults('Integrated_design.zr', 1.7)
prob.model.set_input_defaults('Integrated_design.zf', 0.3)
prob.model.set_input_defaults('Integrated_design.max_power', 1.5e6)
prob.model.set_input_defaults('Integrated_design.MTOM', 2800.)
prob.model.set_input_defaults('Integrated_design.V_cr', 66.)
prob.model.set_input_defaults('Integrated_design.h_cr', 1000)
prob.model.set_input_defaults('Integrated_design.C_L_cr', 0.8)
prob.model.set_input_defaults('Integrated_design.CLmax', 1.68)
prob.model.set_input_defaults('Integrated_design.prop_radius', 0.55)
prob.model.set_input_defaults('Integrated_design.de_da', 0.25)
prob.model.set_input_defaults('Integrated_design.Sv', 1.1)
prob.model.set_input_defaults('Integrated_design.V_stall', 40.)

# Define constraints TODO: Probably better to define them in a central file, like constants
prob.model.add_constraint('Integrated_design.CM_alpha', upper = 0.1)
prob.model.add_constraint('Integrated_design.MTOM', upper = 3175.)
prob.model.add_constraint('Integrated_design.ctrl_mar', upper = 0.)


# Stability constraints
# TODO: if these bounds are changed in the integrated program, change the references

# Select an appropriate optimizer TODO: Change if better algorithms are found
# prob.driver = om.pyOptSparseDriver()
# prob.driver.options['optimizer'] = "ALPSO"

prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'COBYLA'

prob.model.add_design_var('Integrated_design.AR1')
prob.model.add_design_var('Integrated_design.AR2')
prob.model.add_design_var('Integrated_design.Sr_Sf')
prob.model.add_design_var('Integrated_design.xr')

prob.model.add_objective('Integrated_design.Cost_func')

prob.setup()
prob.run_driver()
