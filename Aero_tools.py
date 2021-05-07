import numpy as np


class ISA:
    """
    Calculates the atmospheric parameters at a specified altitude h (in meters).
    An offset in sea level temperature can be specified to allow for variations.

    Note: Since our aircraft probably doesn't fly too high, this is only valid in the troposphere
    """

    def __init__(self, h, T_offset=0):
        # Sea level values
        self.rho_SL = 1.225  # [kg/m^3]  Sea level density
        self.p_SL = 101325  # [Pa]      Sea level pressure
        self.T_SL = 288.15 + T_offset  # [K]       Sea level temperature

        # Constants
        self.a = -0.0065  # [K/m]     Temperature lapse rate
        self.g0 = 9.80665  # [m/s^2]   Gravitational acceleration
        self.R = 287  # [J/kg K]  Specific gas constant

        self.h = h  # [m]       Altitude

        # Throw an error if the specified altitude is outside of the troposphere
        if h > 11000:
            raise ValueError('The specified altitude is outside the range of this class')

        self.T = self.T_SL + self.a * self.h  # [K] Temperature at altitude h, done here because it is used everywhere

    def temperature(self):
        return self.T

    def pressure(self):
        p = self.p_SL * (self.T / self.T_SL) ** (-self.g0 / (self.a * self.R))
        return p

    def density(self):
        rho = self.rho_SL * (self.T / self.T_SL) ** (-self.g0 / (self.a * self.R) - 1)
        return rho
