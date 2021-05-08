# import numpy as np


class Battery:
    """This class is to estimate the parameters of a battery"""
    def __init__(self,sp_en_den, energy):
        self.sp_en_den = sp_en_den
        self.energy = energy

    def mass(self):
        return self.energy / self.sp_en_den
