# import numpy as np


class Battery:
    """This class is to estimate the parameters of a battery"""
    def __init__(self, sp_en_den, vol_en_den, tot_energy, cost, DoD, P_den, P_max):
        """
        :param sp_en_den:
        :param vol_en_den:
        :param tot_energy:
        :param cost:
        :param DoD:
        :param P_den:
        :param P_max:
        """
        self.sp_en_den = sp_en_den
        self.energy = tot_energy
        self.vol_en_den = vol_en_den
        self.cost = cost
        self.DoD = DoD
        self.P_den = P_den
        self.P_max = P_max

    def mass(self):
        """
        :param energy: Required total energy for the battery [Wh]
        :param sp_en_den: Specific energy density of the battery [Wh/kg]
        :return: Mass of the battery
        """
        m_en = self.energy/self.sp_en_den
        m_p = self.P_max/self.P_den
        bat_mass = max(m_en,m_p)
        return bat_mass

    def volume(self):
        """
        :param energy: Required total energy for the battery [Wh]
        :param vol_en_den: Volumetric energy density of the battery [Wh/l]
        :return: Volume of the battery [m^3]
        """
        return self.energy/self.vol_en_den * 0.001

    def price(self):
        """
        :param energy: Required total energy for the battery [Wh]
        :param cost: Cost per Wh of the battery [US$/Wh]
        :return: Approx cost of the battery [US$]
        """
        return self.energy*self.cost
