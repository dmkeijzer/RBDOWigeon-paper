import numpy as np
from pdffit import distfit as pf
import multiprocessing as mp
import os
import sys
import matplotlib.pyplot as plt


class RandVar():
    def __init__(self, data):
        self.max_in = np.max(data)
        self.best_fit, self.params  = pf.BestFitDistribution(list(data)).best_fit_distribution()[0][0:2]

        self.arg = self.params[:-2]
        self.loc = self.params[-2]
        self.scale =  self.params[-1]
    
    def ppf(self, r=0.9):
        return self.best_fit.ppf(r, loc= self.loc, scale = self.scale, *self.arg)

    def plot_cdf_pdf(self, xlabel= "Energy [KwH]"):

        x = np.linspace(0, self.max_in ,  100000)
        pdf = self.best_fit.pdf(x, loc= self.loc, scale= self.scale, *self.arg)
        cdf = self.best_fit.cdf(x, loc= self.loc, scale= self.scale, *self.arg)

        plt.clf()
        plt.plot(x, pdf, "k-.", label= "pdf")
        plt.xlabel(xlabel)
        plt.ylabel("PDF")
        plt.legend()
        plt.twinx()
        plt.plot(x, cdf, "k-", label= "cdf")
        plt.legend()
        plt.ylabel("CDF")
        plt.show()
    
    

if __name__ == "__main__":
    test_arr =  np.random.randn(2000)
    test = RandVar(test_arr)
    pass


