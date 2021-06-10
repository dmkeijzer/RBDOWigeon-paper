""" New weight estimation file """
import numpy as np

class Wing:
    # Roskam method (not accurate because does not take into account density of material but good enough for comparison
    def __init__(self, mtom, S1, S2, n_ult, A, pos = [], wmac = 0.8, toc = 0.17):
        self.S1_ft, self.S2_ft, self.S1, self.S2 = S1 * 3.28084 ** 2, S2 * 3.28084 ** 2, S1, S2
        self.n_ult, self.A = n_ult, A
        self.mtow_lbs = 2.20462 * mtom
        self.pos1, self.pos2 = pos
        self.wweight1 = 0.04674*(self.mtow_lbs**0.397)*(self.S1_ft**0.36)*(self.n_ult**0.397)*(self.A**1.712)
        self.wweight2 = 0.04674*(self.mtow_lbs**0.397)*(self.S2_ft**0.36)*(self.n_ult**0.397)*(self.A**1.712)
        self.mass = [self.wweight1, self.wweight2]
        self.moment = np.array(self.mass)*np.array(pos)
        self.wmac, self.toc = wmac, toc

class Fuselage:
    # Roskam method (not accurate because does not take into account density of material but good enough for comparison
    def __init__(self, mtom, Pmax, lf, npax, pos, wf=1.55):
        self.mtow_lbs = 2.20462 * mtom
        self.lf_ft, self.lf = lf*3.28084, lf
        self.Pmax_ft = Pmax*3.28084
        self.pos = pos
        self.npax = npax
        self.fweight_high = 14.86*(self.mtow_lbs**0.144)*((self.lf_ft/self.Pmax_ft)**0.778)*(self.lf_ft**0.383)*(self.npax**0.455)
        self.fweight_low = 0.04682*(self.mtow_lbs**0.692)*(self.Pmax_ft**0.379)*(self.lf_ft**0.590)
        self.fweight = (self.fweight_high + self.fweight_low)/2
        self.mass = self.fweight*0.453592
        self.moment = self.mass * self.pos
        self.wf = wf

class LandingGear:
    def __init__(self, mtom, pos):
        self.mass = 0.04*mtom
        self.pos = pos
        self.moment = self.mass * self.pos

class Propulsion:

    def __init__(self, n_prop, m_prop = [], pos_prop = []):
        self.nprop = n_prop
        self.wprop = np.array(m_prop)
        self.pos_prop = np.array(pos_prop)
        self.moment_prop = self.wprop*self.pos_prop
        self.mass = np.sum(self.wprop)
        self.moment = np.sum(self.wprop*self.pos_prop)

class Weight:

    def __init__(self, m_pax, wing, fuselage, landing_gear, propulsion, cargo_m, cargo_pos, battery_m, battery_pos, p_pax = []):
        self.m_pax, self.p_pax = m_pax, p_pax
        self.wing, self.fuselage, self.landing_gear, self.prop = wing, fuselage, landing_gear, propulsion
        # weights of components
        self.tot_m_pax = self.m_pax * 5
        self.wmass, self.fmass, self.lmass, self.pmass = np.sum(self.wing.mass), self.fuselage.mass, self.landing_gear.mass, self.prop.mass
        self.cmass, self.cpos = cargo_m, cargo_pos
        self.bmass, self.battery_pos = battery_m, battery_pos
        #moments of components
        self.moment_pax = np.sum(self.m_pax * np.array(self.p_pax))
        self.moment_w = np.sum(np.array(self.wing.moment))
        self.moment_f = self.fuselage.moment
        self.moment_l = self.landing_gear.moment
        self.moment_p = self.prop.moment
        self.moment_c = self.cmass * self.cpos
        self.moment_b = self.bmass * self.battery_pos
        #operational empty mass centre of gravity
        self.oem_cg = (self.moment_w + self.moment_f + self.moment_l + self.moment_p + self.moment_b) \
        /(self.wmass + self.pmass + self.lmass + self.fmass + self.bmass)

        self.mtom_cg = (self.moment_w + self.moment_f + self.moment_l + self.moment_p + self.moment_pax + self.moment_c + self.moment_b) \
        /(self.wmass + self.pmass + self.lmass + self.fmass + self.cmass + self.bmass + self.tot_m_pax)

        #masses
        self.oem = (self.wmass + self.pmass + self.lmass + self.fmass + self.bmass)
        self.mtom = (self.wmass + self.pmass + self.lmass + self.fmass + self.cmass + self.bmass + self.tot_m_pax)

    def print_weight_fractions(self):
        d = {}
        d["Front wing"] = [self.wing.mass[0], self.wing.mass[0]/self.oem, self.wing.mass[0]/self.mtom]
        d["Back wing"] = [self.wing.mass[1], self.wing.mass[1]/self.oem, self.wing.mass[1]/self.mtom]
        d['Fuselage'] = [self.fmass, self.fmass/self.oem, self.fmass/self.mtom]
        d['Landing gear'] = [self.lmass, self.lmass/self.oem, self.lmass/self.mtom]
        d['Propulsion'] = [self.pmass, self.pmass/self.oem, self.pmass/self.mtom]
        d['Cargo'] = [self.cmass, 0.0, self.cmass/self.mtom]
        d['Battery'] = [self.bmass, self.bmass/self.oem, self.bmass/self.mtom]
        d['Payload'] = [self.tot_m_pax, 0.0, self.tot_m_pax/self.oem]

        print("{:<15} {:<20} {:<25} {:<15}".format('Component', 'Mass[kg]', 'fraction of OEM', 'fraction of MTOM'))
        print('--------------------------------------------------------------------------------')
        for k, v in d.items():
            mass, oem_frac, mtom_frac = v
            print("{:<15} {:<20} {:<25} {:<15}".format(k, mass, oem_frac, mtom_frac))
        print('')
        print(f'Where OEM is {self.oem}kg with CG of {self.oem_cg}m, and MTOM is {self.mtom}kg with CG of {self.mtom_cg}m')
        # for key in d:
        #     d[key] = {k: list(i) if isinstance(i, np.ndarray) else i for k, i in zip(["mass", "fracOEM", "fracEM"], d[key])}
        # return d
    def MMI(self):
        # fuselage  - modeled as a hollow cylinder with wall thickness of 5 cm
        irad = (self.fuselage.wf/2 - 0.05)
        fus_mmi_y = self.fmass * (self.fuselage.lf**2 + 3*(self.fuselage.wf/2)**2 + 3*irad**2)/12
        fus_mmi_z = fus_mmi_y
        fus_mmi_x = self.fmass * ((self.fuselage.wf/2)**2 + irad**2)/2

        # wing - modeled as a prism with span, average thickness and width at mac
        t = self.wing.wmac * self.wing.toc
        span = np.sqrt(self.wing.A * self.wing.S1)

        wing_mmi_x, wing_mmi_y, wing_mmi_z = self.wing.mass[0]*(span**2 + t**2)/12, self.wing.mass[0]*(span**2 + self.wing.wmac**2)/12, \
                                             self.wing.mass[0] * (self.wing.wmac ** 2 + t ** 2) / 12

        # propulsion - modeled as a solid cylinder
        m_prop = self.pmass/self.prop.nprop
        lprop, rprop = 0.4, 0.12
        prop_mmi_x, prop_mmi_y, prop_mmi_z = m_prop*(rprop**2)/2, m_prop*(lprop**2 + 3 * rprop**2)/12, m_prop*(lprop**2 + 3 * rprop**2)/12
        print(m_prop)
        # battery - modeled as a prism
        lbat, tbat, wbat = 0.4*self.fuselage.lf, 0.2, 1
        bat_mmi_x, bat_mmi_y, bat_mmi_z = self.bmass*(wbat**2 + tbat**2)/12, self.bmass*(wbat**2 + lbat**2)/12, self.bmass*(tbat**2 + lbat**2)/12

        span = np.sqrt(self.wing.A*self.wing.S1)
        oem_mmi_x = fus_mmi_x + 2 * (
                    wing_mmi_x + self.wmass/2 * (1.705 /2)**2) + \
                    self.prop.nprop/4 * np.sum(m_prop * (np.sqrt((1.705/2)**2 +  (np.linspace(0.9, span/2, int(self.prop.nprop/4))) ** 2 ))** 2) + \
                                         self.prop.nprop * prop_mmi_x + bat_mmi_x + self.bmass * (1.705/2) ** 2
        oem_mmi_y = fus_mmi_y + 2* (wing_mmi_y + self.wmass/2*(self.wing.pos2/2)**2) +\
                    self.prop.nprop/4 * np.sum(m_prop * (np.sqrt((self.wing.pos2/2)**2 +  (np.linspace(0.9, span/2, int(self.prop.nprop/4))) ** 2))**2) +\
                                                         self.prop.nprop * prop_mmi_y + bat_mmi_y
        oem_mmi_z = fus_mmi_z + (wing_mmi_z + self.wmass/2 * (
            np.sqrt((1.705 / 2) ** 2 + (self.wing.pos2/2) ** 2)) ** 2) * 2 + bat_mmi_z + self.bmass * (1.705 / 2) ** 2 + (
                                m_prop * ((np.sqrt((1.705 / 2) ** 2 + (self.wing.pos2/2) ** 2)) ** 2) + prop_mmi_z) * self.prop.nprop
        oem_mmi_xy = (self.wmass/2 * (1.705 / 2) * self.wing.pos1/2) * 2 + self.prop.nprop * (m_prop * (1.705 / 2) * self.wing.pos1/2)
        return oem_mmi_x, oem_mmi_y, oem_mmi_z, oem_mmi_xy

if __name__ == '__main__':
    mtom = 3000 # maximum take-off mass from statistical data - Class I estimation
    S1, S2 = 5.5, 5.5 # surface areas of wing one and two
    A = 14 # aspect ratio of a wing, not aircraft
    n_ult = 3.2*1.5 # 3.2 is the max we found, 1.5 is the safety factor
    Pmax = 15.25 # this is defined as maximum perimeter in Roskam, so i took top down view of the fuselage perimeter
    lf = 7.2 # length of fuselage
    m_pax = 95 # average mass of a passenger according to Google
    n_prop = 16 # number of engines
    n_pax = 5 # number of passengers (pilot included)
    pos_fus = 3.6 # fuselage centre of mass away from the nose
    pos_lgear = 3.6 # landing gear position away from the nose
    pos_frontwing, pos_backwing = 0.2, 7 # positions of the wings away from the nose
    m_prop = [30]*16 # list of mass of engines (so 30 kg per engine with nacelle and propeller)
    pos_prop = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0, 7.0] # 8 on front wing and 8 on back wing
    wing = Wing(mtom, S1, S2, n_ult, A, [pos_frontwing, pos_backwing])
    fuselage = Fuselage(mtom, Pmax, lf, n_pax, pos_fus)
    lgear = LandingGear(mtom, pos_lgear)
    props = Propulsion(n_prop, m_prop, pos_prop)
    weight = Weight(m_pax, wing, fuselage, lgear, props, cargo_m = 85, cargo_pos = 6, battery_m = 400, battery_pos = 3.6, p_pax = [1.5, 3, 3, 4.2, 4.2])
    print(weight.print_weight_fractions())
    print(weight.MMI())