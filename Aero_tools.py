import numpy as np
from constants import*
import warnings


class ISA:
    """
    Calculates the atmospheric parameters at a specified altitude h (in meters).
    An offset in sea level temperature can be specified to allow for variations.

    Note: Since our aircraft probably doesn't fly too high, this is only valid in the troposphere

    Verified by comparison to: https://www.digitaldutch.com/atmoscalc/
    """

    def __init__(self, h, T_offset=0):

        # Constants
        self.a = -0.0065    # [K/m]     Temperature lapse rate
        self.g0 = 9.80665   # [m/s^2]   Gravitational acceleration
        self.R = 287        # [J/kg K]  Specific gas constant
        self.gamma = 1.4    # [-]       Heat capacity ratio

        # Sea level values
        self.rho_SL = 1.225                                 # [kg/m^3]  Sea level density
        self.p_SL   = 101325                                # [Pa]      Sea level pressure
        self.T_SL   = 288.15 + T_offset                     # [K]       Sea level temperature
        self.mu_SL  = 1.7894E-5                             # [kg/m/s] Sea Level Dynamic Viscosity 1.81206E-5
        self.a_SL   = np.sqrt(self.gamma*self.R*self.T_SL)  # [m/s] Sea level speed of sound

        self.h = h  # [m]       Altitude

        # Throw an error if the specified altitude is outside of the troposphere
        if np.any(h) > 11000:
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

    def soundspeed(self):
        a = self.a_SL * np.sqrt(self.T/self.T_SL)
        return a

    def viscosity_dyn(self):
        mu = self.mu_SL * (self.T / self.T_SL) ** (1.5) * (self.T_SL + 110.4) / (self.T + 110.4)
        # 1.458E-6 * self.T ** 1.5 / (self.T + 110.4) # Sutherland Law, using Sutherland's constant S_mu = 110.4 for air
        return mu


class speeds:
    """
    Class that contains all the relevant speeds.

    TO DO:
        - Add climb and cruise speed (once drag polar is done)
        - Add aircraft parameters from datafile
    """
    def __init__(self, altitude, m):

        # To be added from datafile:
        self.CLmax  = 1.5
        self.S      = 10

        self.rho    = ISA(altitude).density()
        self.W      = m*g

    def stall(self):
        return np.sqrt(2*self.W/(self.rho*self.S*self.CLmax))

    def climb(self):
        # !!!! IMPLEMENT !!!
        return 50

    def cruise(self):
        # !!!! IMPLEMENT !!!!
        # ADD WIND EFFECT
        return 60



