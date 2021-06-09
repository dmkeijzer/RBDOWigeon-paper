"""
File created for incorporating other systems that require power
"""

class power_budget:
    def __init__(self):
        self.avionics = 252
        self.airco = 3000
        self.battery_cooling = 30*6
        self.autopilot = 151
        self.trim = 54
        self.landing_gear = 300
        self.passenger_power = 400
        self.external_lights = 117