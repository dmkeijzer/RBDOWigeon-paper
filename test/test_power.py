import unittest
import PropandPower.battery as bat
# import PropandPower.redundancy_battery_config as red

class testpower(unittest.TestCase):
    def test_bat_size(self):
        # Example variables
        sp_en_den = 40
        vol_en_den = 17
        tot_energy = 250
        cost = 0.5
        DoD = 0.9
        P_den = 19
        P_max = 1
        safety = 1.5
        EOL_C = 0.85

        P_max_crazy = 13245
        # Size batteries with values and check if it's correct
        sample_bat_size = bat.Battery(sp_en_den, vol_en_den, tot_energy, cost, DoD, P_den, P_max, safety, EOL_C)
        sample_bat_size_crazypower = bat.Battery(sp_en_den, vol_en_den, tot_energy, cost, DoD, P_den, P_max_crazy, safety, EOL_C)

        # Test battery mass test
        self.assertAlmostEqual(sample_bat_size.mass(), 12.255, places = 2) # Size for energy
        self.assertAlmostEqual(sample_bat_size_crazypower.mass(), 1366.873, places = 2)  # Size for energy

        # Test volume
        self.assertAlmostEqual(sample_bat_size.volume(), 0.028835, places = 5)

        # Test price
        self.assertAlmostEqual(sample_bat_size.price(), 0.245098, places=3)



