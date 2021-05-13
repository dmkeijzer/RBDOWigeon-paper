"""
This program evaluates the propulsive performance of an eVTOL following the
procedure obtained from "Architectural performance assessment of an electric
vertical take-off and landing (e-VTOL) aircraft based on a ducted vectored thrust concept (2021)"
"""
import numpy as np
from constants import *
import json
from Aero_tools import ISA

class PropulsionHover:

    def __init__(self, MTOM, n, A, eff_bat_el, eff_el_mo, eff_mo_sha, eff_sha_flo, eff_flo_jet, vj, m_dot_h, rho):
        """
        :param MTOM:        Maximum take off mass [kg]
        :param n:           Number of engines
        :param A:           Area per engine [m^2]8
        :param eff_bat_el:  Efficiency from battery to electronics
        :param eff_el_mo:   Efficiency from electronics to motors
        :param eff_mo_sha:  Efficiency from motors to shaft
        :param eff_sha_flo: Efficiency from shaft to flow
        :param eff_flo_jet: Efficiency from flow to jet
        :param vj:          Jet speed [m/s]
        :param m_dot_h:     Mass flow at hover [kg/s]
        """
        self.MTOM = MTOM
        self.n = n
        self.A = A
        self.eta_B = eff_bat_el
        self.eta_PE = eff_el_mo
        self.eta_M = eff_mo_sha
        self.eta_F = eff_sha_flo
        self.eta_D = eff_flo_jet
        self.eff_hover = eff_bat_el * eff_el_mo * eff_mo_sha * eff_sha_flo * eff_flo_jet
        self.vj = vj
        self.m_dot = m_dot_h
        self.rho = rho
        self.g = 9.80665
        self.T_h = self.g*self.MTOM

    def P_h_ducted(self):
        return (0.5*self.T_h**(3/2) / np.sqrt(self.rho * self.n * self.A)) / self.eff_hover

    def P_h_open(self):
        return self.T_h**(3/2) / np.sqrt(2 * self.rho * self.n * self.A)

class PropulsionCruise:

    def __init__(self, MTOM, n, A, eff_bat_el, eff_el_mo, eff_mo_sha, eff_sha_flo, eff_flo_jet, eff_jet_air,
                 rho, v_cruise, drag):
        """
        :param MTOM: Maximum take off mass [kg]
        :param n: Number of engines
        :param A: Area per engine [m^2]8
        :param eff_bat_el:  Efficiency from battery to electronics
        :param eff_el_mo:   Efficiency from electronics to motors
        :param eff_mo_sha:  Efficiency from motors to shaft
        :param eff_sha_flo: Efficiency from shaft to flow
        :param eff_flo_jet: Efficiency from flow to jet
        :param eff_jet_air: Efficiency from jet to aircraft
        """
        self.MTOM = MTOM
        self.n = n
        self.A = A
        self.eta_B = eff_bat_el
        self.eta_PE = eff_el_mo
        self.eta_M = eff_mo_sha
        self.eta_F = eff_sha_flo
        self.eta_D = eff_flo_jet
        self.eff_cruise = eff_bat_el * eff_el_mo * eff_mo_sha * eff_sha_flo * eff_flo_jet * eff_jet_air
        self.v_cruise = v_cruise
        self.drag = drag

    def P_cr(self):
        return self.drag * self.v_cruise / self.eff_cruise

class ActuatorDisk:

    def __init__(self, D_inner_ratio, D_prop_pure_hover_ratio):
        """
        :param D_prop_inner: diameter of a propeller [m]
        :param TWratio: Thurst-to-weight ratio [-]
        :param V_e_LTO: Exit speed at LTO conditions [m/s]
        :param D_prop_pure_hover: diameter of propeller for pure hover (config 3) [m]
        """

        # Class specific data not in .json
        self.D_inner_ratio = D_inner_ratio
        self.D_prop_pure_hover_ratio = D_prop_pure_hover_ratio

        # Extracting Propulsion data
        self.n_prop_cruise = N_cruise
        self.n_prop_hover = N_hover
        self.TWratio = TW_ratio
        self.V_e_LTO = V_e_LTO

        # Extracting aerodynamic data
        self.CD = 0.01808  # CD
        self.c_r = c_r

        # Extracting performance data
        self.S = S
        self.V_cruise = V_cruise
        self.h_cruise = h_cruise

        # Atmospherics
        atm_flight  = ISA(self.h_cruise)    # atmospheric conditions during flight   # Idk if this actually works
        atm_LTO     = ISA(0)         # atmospheric conditions at landing and take-off (assumed sea-level)
        self.rho_flight = atm_flight.density()
        self.rho_LTO    = atm_LTO.density()

    def D_prop_outer(self):
        if self.n_prop_cruise == self.n_prop_hover:
            A_indiv = self.A_hover() / self.n_prop_hover
            D_prop_outer = np.sqrt(4 * A_indiv / (np.pi * (1 - self.D_inner_ratio)))
        else:
            N_prop_pure_hover = self.n_prop_hover - self.n_prop_cruise
            D_prop_pure_hover = self.D_prop_pure_hover_ratio * self.c_r
            A_pure_hover = N_prop_pure_hover * np.pi / 4 * D_prop_pure_hover * (1 - self.D_inner_ratio)
            A_remain = self.A_hover() - A_pure_hover
            A_indiv = A_remain/ self.n_prop_cruise
            D_prop_outer = np.sqrt ( 4 * A_indiv / (np.pi * (1 - self.D_inner_ratio)) )
        return D_prop_outer

    def V_e_cruise(self):
        A_tot = self.A_hover()
        return np.sqrt(self.V_cruise**2 * (self.S * self.CD + A_tot) / A_tot)

    def P_ideal(self):
        return 0.25 * self.rho_flight * self.V_cruise**3 * self.S * self.CD * (np.sqrt(self.CD * self.S / self.A_hover() + 1) + 1)

    def eff(self):
        return 2 / (1 + self.V_e_cruise()/self.V_cruise)

    def A_hover(self):
        return MTOW * self.TWratio * 2 / (self.rho_LTO * self.V_e_LTO**2)
