import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import re
import sys
import pathlib as pl
import seaborn as sns
import yaml

sys.path.append(str(list(pl.Path(__file__).parents)[1]))
os.chdir(str(list(pl.Path(__file__).parents)[1]))

with open(os.path.realpath(r'input\environment_variables_plotting.yml'), 'r') as yamlfile:
    data = yaml.safe_load(yamlfile)

dir_path = data["mcs"]["dir"]
label =  os.path.split(dir_path)[-1][3:]

converg_arr = np.load(os.path.join(dir_path, "mcs_convergence" + label + ".npy")) # Convergence array 

plt.plot(converg_arr/3.6e6, "<-")
plt.xlabel(r" $n_{th}$ chunk of iterations")
plt.ylabel(r"$\sigma$")
plt.show()
