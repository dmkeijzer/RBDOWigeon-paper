import numpy as np
from pdffit import distfit as pf
import multiprocessing as mp
import os
import matplotlib.pyplot as plt
import scipy

class RandVar():
    def __init__(self, data):
        self.min = np.min(data)
        self.max = np.max(data)
        self.best_fit, self.params  = pf.BestFitDistribution(list(data)).best_fit_distribution()[0][0:2]

        self.arg = self.params[:-2]
        self.loc = self.params[-2]
        self.scale =  self.params[-1]

        if (np.size(data[data == 0]) > (0.5*np.size(data))):
            self.data = data
        else:
            self.data = np.histogram(data, bins= "auto")
    
    def ppf(self, r=0.9):
        return self.best_fit.ppf(r, loc= self.loc, scale = self.scale, *self.arg)

    def get_expectation(self):
        return self.best_fit.expect(args= self.arg, loc= self.loc, scale= self.scale)
    
    def get_std(self):
        return self.best_fit.std(*self.arg, loc= self.loc, scale= self.scale)


    def plt(self):
        x = np.linspace(self.min, self.max ,  1000)
        pdf = self.best_fit.pdf(x, loc= self.loc, scale= self.scale, *self.arg)
        cdf = self.best_fit.cdf(x, loc= self.loc, scale= self.scale, *self.arg)
        return x,pdf, cdf

        # plt.clf()
        # plt.plot(x, pdf, "k-.", label= "pdf")
        # plt.xlabel(xlabel)
        # plt.ylabel("PDF")
        # plt.legend()
        # plt.twinx()
        # plt.plot(x, cdf, "k-", label= "cdf")
        # plt.legend()
        # plt.ylabel("CDF")
        # plt.show()
    
    

if __name__ == "__main__":
    test_arr = np.random.randn(10000)
    test_instance = RandVar(test_arr)
    print(test_instance.best_fit)
    print(test_instance.params)
    print(test_instance.ppf())

    # test_arr = np.hsplit(np.random.randn(300,5), 5)
    # with mp.Pool(os.cpu_count()) as p:
    #     energy_stochvar, t_stochvar, power_stochvar, thrust_stochvar, t_cr_stochvar = p.map(StochVar, test_arr)
    
    # test_arr2 = np.array([np.array([i, 2*i, 3* i, np.array([i, i+ 1, i + 2])]) for i in range(100)])

    # print(test_arr2)
    # print(np.vstack(test_arr2[:,-1]))
    # print(np.hsplit(np.vstack(test_arr2[:,-1]), 3))



    # with mp.Pool(os.cpu_count()) as p:
    #     Ecruise_stochvar, Eclimb_stochvar, Edesc_stochvar, Eloit_cr_stochvar, Eloit_hov_stochvar = p.map(StochVar, test_arr2)

    #     Eclimb_stochvar.plot_cdf_pdf()
    #     Edesc_stochvar.plot_cdf_pdf()
    #     Eloit_hov_stochvar.plot_cdf_pdf()


