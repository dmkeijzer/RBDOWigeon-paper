import Aero_tools as at

cruise_height = 3000

ISA = at.ISA(cruise_height)

print(ISA.viscosity_dyn(), ISA.density())

ISA = at.ISA(0)

print(ISA.viscosity_dyn(), ISA.density())

