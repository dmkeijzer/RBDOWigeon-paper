import openmdao.api as om
import numpy as np
from stab_and_ctrl.xcg_limits import xf, xr, zf, zr, xcg_range, Arange, bmax, crmaxf, crmaxr

class design_optimization(om.ExplicitComponent):

    def setup(self):

        # Changing input parameters
        self.add_input('Tail-cone_length', units = 'm')
        self.add_input('Wing_surface', units = 'm^2')
        self.add_input('Aspect_ratio_front', units = None)
        self.add_input('Aspect_ratio_rear', units = None)
        self.add_input('Relative_wing_size', units = None)  # Not really sure in what format this will be
        self.add_input('Wing_position_1', units = 'm')
        self.add_input('Wing_position_2', units = 'm')

        # Output
        self.add_output('time', units = 's')
        self.add_output('energy', units = None)  # Need to decide on Wh or J
        self.add_output('mass', units = 'kg')
        self.add_output('Cost_func')

        # Outputs used as constraints, these come from stability
        self.add_output('xf', units = 'm')
        self.add_output('xr', units = 'm')
        self.add_output('zf', units = 'm')
        self.add_output('zr', units = 'm')
        self.add_output('crmaxf', units = 'm')
        self.add_output('crmaxr', units = 'm')
        self.add_output('bmax', units = 'm')
        self.add_output('x_cg_range', units = 'm')
        self.add_output('A_range', units = None)

    def setup_partials(self):

        # Partial derivatives are done using finite difference
        self.declare_partials('*', '*', 'fd')

    def compute(self, inputs, outputs):

        outputs['xf'] = None
        outputs['xr'] = None
        outputs['zf'] = None
        outputs['zr'] = None
        outputs['crmaxf'] = None
        outputs['crmaxr'] = None
        outputs['bmax'] = None
        outputs['x_cg_range'] = None
        outputs['A_range'] = None

        raise NotImplementedError


prob = om.Problem()
prob.model.add_subsystem('Integrated_design', design_optimization(), promotes_inputs=['Tail_cone_length,'
                                                                                      'Wing_surface',
                                                                                      'Aspect_ratio_front',
                                                                                      'Aspect_ratio_rear',
                                                                                      'Relative_wing_size',
                                                                                      'Wing_position_1',
                                                                                      'Wing_position_2'])

# Initial values for the optimization TODO: Improve initial values
prob.model.set_input_defaults('Tail_cone_length', 2)
prob.model.set_input_defaults('Wing_surface', 14)
prob.model.set_input_defaults('Aspect_ratio_front', 8)
prob.model.set_input_defaults('Aspect_ratio_rear', 8)
prob.model.set_input_defaults('Relative_wing_size', None)   # Change
prob.model.set_input_defaults('Wing_position_1', 1)
prob.model.set_input_defaults('Wing_position_2', 8)

# Define constraints TODO: Probably better to define them in a central file, like constants
prob.model.add_constraint('Integrated_design.time', upper = 3, units = 'hr')
prob.model.add_constraint('Integrated_design.mass', upper = 3175, units = 'kg')

# Stability constraints
# TODO: if these bounds are changed in the integrated program, change the references
prob.model.add_constraint('Integrated_design.xf', lower = xf[0], upper = xf[1], units = 'kg')
prob.model.add_constraint('Integrated_design.xr', lower = xr[0], upper = xr[1], units = 'kg')
prob.model.add_constraint('Integrated_design.zf', lower = zf[0], upper = zf[1], units = 'kg')
prob.model.add_constraint('Integrated_design.zr', lower = zr[0], upper = zr[1], units = 'kg')
prob.model.add_constraint('Integrated_design.crmaxf', upper = crmaxf, units = 'kg')
prob.model.add_constraint('Integrated_design.crmaxr', upper = crmaxr, units = 'kg')
prob.model.add_constraint('Integrated_design.bmax', upper = bmax, units = 'kg')
prob.model.add_constraint('Integrated_design.x_cg_range', lower = xcg_range[0], upper = xcg_range[1], units = 'kg')
#prob.model.add_constraint('Integrated_design.A_range', lower = xf[0], upper = xf[1], units = 'kg')

# Select an appropriate optimizer TODO: Change if better algorithms are found
prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'COBYLA'

# Define design variables TODO: Add appropriate constraints
prob.model.add_design_var('Tail_cone_length', lower = 0)
prob.model.add_design_var('Wing_surface', lower = 0)
prob.model.add_design_var('Aspect_ratio_front')
prob.model.add_design_var('Aspect_ratio_rear')
prob.model.add_design_var('Relative_wing_size')   # Change
prob.model.add_design_var('Wing_position_1', lower = 0)
prob.model.add_design_var('Wing_position_2', lower = 0)

prob.model.add_objective('cruise.D/L')

prob.setup()
prob.run_driver()
