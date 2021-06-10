"""
File created for incorporating other systems that require power
"""

class Power_Budget:
    def __init__(self):
        # Constant required power
        self.avionics = 252  # [W]
        self.airco = 3000  # [W]
        self.battery_cooling = 30 # [W] Per 72 kg.
        self.autopilot = 151  # [W]
        self.trim = 54  # [W]
        self.passenger_power = 400  # [W]
        self.external_lights = 117  # [W]
        self.deice = 3000  # [W]

        # Non continuous power
        self.landing_gear = 50  # [W]
        self.wing_rot_mech = 3000  # [W]

    def P_continuous(self, m):
        return self.avionics + self.airco + self.battery_cooling * m / 72 + self.autopilot + self.trim + self.passenger_power \
               + self.external_lights + self.deice

    def E_landing_gear(self, t_lg_rot):
        return self.landing_gear * t_lg_rot

    def E_wing_rot(self, t_transition):
        return self.wing_rot_mech * t_transition
