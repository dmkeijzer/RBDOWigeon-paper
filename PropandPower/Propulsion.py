"""
This program evaluates the propulsive performance of an eVTOL following the
procedure obtained from "Architectural performance assessment of an electric
vertical take-off and landing (e-VTOL) aircraft based on a ducted vectored thrust concept (2021)"
"""
import numpy as np
import os
import json

root_path = os.path.join(os.getcwd(), os.pardir)
datafile = open(os.path.join(root_path, "inputs_config_1.json"), "r")
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

    def __init__(self,D_prop_outer, D_prop_inner,n_prop,datafile):
        """
        :param D_prop_outer: diameter of a propeller [m]
        :param D_prop_inner: diameter of a propeller [m]
        :param n_prop: number of propellers [-]
        """

        # Class specific data not (yet) in .json
        self.D_prop_outer = D_prop_outer
        self.D_prop_inner = D_prop_inner
        self.n_prop = n_prop

        # Read data from json file
        self.data = json.load(datafile)
        datafile.close()

        # Extracting aerodynamic data
        aero = self.data["Aerodynamics"]
        self.CD = 0.02 #aero["CD"]

        # Extracting performance data
        perf = self.data["Flight performance"]
        self.S = 25 #perf["S"]
        self.V_0 = 50 # perf["V_cruise"]
        self.h = 1000 #perf["h_cruise"]

        # Atmospherics
        atm_flight  = ISA(self.h)    # atmospheric conditions during flight   # Idk if this actually works
        atm_LTO     = ISA(0)    # atmospheric conditions at landing and take-off (assumed sea-level)
        self.rho_flight = atm_flight.density()
        self.rho_LTO    = atm_LTO.density()

    def A_prop(self):
        return np.pi / 4 * (self.D_prop_outer**2 - self.D_prop_inner**2)

    def V_e(self):
        A_tot = self.A_prop() * self.n_prop
        return np.sqrt(self.V_0**2 * (self.S * self.CD + A_tot) / A_tot)

    def P_ideal(self):
        return 0.25 * self.rho_flight * self.V_0**3 * self.S * self.CD * (np.sqrt(self.CD * self.S / self.A_prop() + 1) + 1)

# print("Exit speed:", ActuatorDisk(0.50,0.49,10,datafile).V_e(), "[m/s]")
#
# print(ActuatorDisk(0.50,0.1,10,datafile).P_ideal())

