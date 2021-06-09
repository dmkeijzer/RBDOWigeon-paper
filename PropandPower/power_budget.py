"""
File created for incorporating other systems that require power
"""


class power_budget:
    def __init__(self):
        # Constant required power
        self.avionics = 252  # [W]
        self.airco = 3000  # [W]
        self.battery_cooling = 30 * 6  # [W]
        self.autopilot = 151  # [W]
        self.trim = 54  # [W]
        self.passenger_power = 400  # [W]
        self.external_lights = 117  # [W]
        self.deice = 3000  # [W]

        # Non continuous power
        self.landing_gear = 300  # [W]
        self.wing_rot_mech = 3000 # [W]

    def P_continuous(self):
        return
