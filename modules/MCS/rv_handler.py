import numpy as np
from pdffit import distfit as pf
import multiprocessing as mp
import os
import matplotlib.pyplot as plt
import scipy as sp


class RandVar:
    def __init__(self, data):
        self.min = np.min(data)
        self.max = np.max(data)
        self.best_fit, self.params = pf.BestFitDistribution(
            list(data)
        ).best_fit_distribution()[0][0:2]

        self.arg = self.params[:-2]
        self.loc = self.params[-2]
        self.scale = self.params[-1]

        if np.size(data[data == 0]) > (0.5 * np.size(data)):
            self.data = data
        else:
            self.data = np.histogram(data, bins="auto")

    def ppf(self, r=0.9):
        """Percent point function, i.e the inverse of the cumulatitive distribution function

        :param r: Left tail probabilty, defaults to 0.9
        :type r: float, optional
        :return:  Corresponding value to the left tail probability
        :rtype:  float
        """
        return self.best_fit.ppf(r, loc=self.loc, scale=self.scale, *self.arg)

    def get_expectation(self):
        """Returns the expectation of the random variable

        :return: Expectation
        :rtype: float
        """
        return self.best_fit.expect(
            args=self.arg, loc=self.loc, scale=self.scale, lb=self.min, ub=self.max
        )

    def get_std(self):
        """Returns the standard deviaton of the random variable

        :return: standard deviation
        :rtype: float
        """
        return self.best_fit.std(*self.arg, loc=self.loc, scale=self.scale)

    def plt(self):
        """Returns the plotting data of the pdf and cdf of the random variable for the fitting range of data contained within it

        :return:  x axis and y axis data for both pdf and cdf.
        :rtype: tuple of nd.array
        """
        x = np.linspace(self.min, self.max, 8000)
        pdf = self.best_fit.pdf(x, loc=self.loc, scale=self.scale, *self.arg)
        cdf = self.best_fit.cdf(x, loc=self.loc, scale=self.scale, *self.arg)
        return x, pdf, cdf
