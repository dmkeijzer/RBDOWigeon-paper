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

dir_path_mcs = data["mcs"]["dir"]
dir_path_baseline = data["baseline"]["dir"]
label_mcs =  os.path.split(dir_path_mcs)[-1][3:]
label_baseline =  os.path.split(dir_path_baseline)[-1][3:]

dump_path_tables_mcs = os.path.join(dir_path_mcs, "tables")
dump_path_plots_mcs = os.path.join(dir_path_mcs, "plots")

dump_path_tables_baseline = os.path.join(dir_path_baseline, "tables")
dump_path_plots_baseline = os.path.join(dir_path_baseline, "plots")

converg_arr_mcs = np.load(os.path.join(dir_path_mcs, "mcs_convergence" + label_mcs + ".npy")) # Convergence array 

plt.plot(converg_arr_mcs/3.6e6, "<-")
plt.xlabel(r" $n_{th}$ chunk of iterations")
plt.ylabel(r"$\sigma$")
plt.savefig(os.path.join(dump_path_plots_mcs, "mcs_convergence" + label_mcs + ".pdf"))


mission_samples_mcs_arr = np.load(os.path.join(dir_path_mcs, "sample_history" + label_mcs + ".npy"), allow_pickle=True)
mission_results_mcs_arr = np.load(os.path.join(dir_path_mcs, "mission_results" + label_mcs + ".npy"), allow_pickle=True)

mission_samples_baseline_arr = np.load(os.path.join(dir_path_baseline, "mcs_metric", "mcs_metric_samples" + label_baseline + ".npy"), allow_pickle=True)
mission_results_baseline_arr = np.load(os.path.join(dir_path_baseline, "mcs_metric", "mcs_metric_results" + label_baseline + ".npy"), allow_pickle=True)

# Format data for visualization for both mcs and baseline
combined_arr_mcs = np.hstack((mission_samples_mcs_arr, mission_results_mcs_arr)) # horizontal stack mission samples and their results
combined_arr_mcs[:,0] = combined_arr_mcs[:,0]/1000 # Convert to km
combined_arr_mcs[:,6] = combined_arr_mcs[:,6]/3.6e6 # Convert to kwh
sort_arr_mcs = np.argsort(combined_arr_mcs[:, 6]) # Get correct order of rows small to large energies
combined_arr_sorted_mcs = combined_arr_mcs[sort_arr_mcs, :] # Shift the rows in the correct order

combined_arr_baseline = np.hstack((mission_samples_baseline_arr, mission_results_baseline_arr)) # horizontal stack mission samples and their results
combined_arr_baseline[:,0] = combined_arr_baseline[:,0]/1000 # Convert to km
combined_arr_baseline[:,6] = combined_arr_baseline[:,6]/3.6e6 # Convert to kwh
sort_arr_baseline = np.argsort(combined_arr_baseline[:, 6]) # Get correct order of rows small to large energies
combined_arr_sorted_baseline = combined_arr_baseline[sort_arr_baseline, :] # Shift the rows in the correct order

# Format for correlation coefficient
corr_data_mcs = np.hstack((np.reshape(mission_results_mcs_arr[:,0], (-1,1)).astype("float64"), mission_samples_mcs_arr.astype("float64")), dtype= "float64")
corr_matrix_mcs = np.round(np.corrcoef(corr_data_mcs, rowvar= False), 3)

corr_data_baseline = np.hstack((np.reshape(mission_results_baseline_arr[:,0], (-1,1)).astype("float64"), mission_samples_baseline_arr.astype("float64")), dtype= "float64")
corr_matrix_baseline = np.round(np.corrcoef(corr_data_baseline, rowvar= False), 3)

# Writing results to excel and save matrix data in txt file
cols = ["Rng", "Ltr Cr", "Tr Heigt", "Ltr Height", "Ltr Hover", "Cr H", "E", "Total time", "Max power", "Max thrust", "Time cruise", "Energy dist"] # Labels for all the columns
pd.DataFrame(combined_arr_sorted_mcs, columns= cols).to_excel(os.path.join(dump_path_tables_mcs, "mission_samples_sorted" + label_mcs + ".xlsx"), columns = cols) # Write to excel file for easy read
pd.DataFrame(combined_arr_sorted_baseline, columns= cols).to_excel(os.path.join(dump_path_tables_baseline, "mission_samples_sorted" + label_baseline + ".xlsx"), columns = cols) # Write to excel file for easy read

corr_matrix_mcs = np.vstack((np.reshape(np.array(["E"] + cols[:6]), (1,-1)), corr_matrix_mcs))
corr_matrix_mcs = np.hstack((np.reshape(np.array(["_", "E"] + cols[:6]), (-1,1)), corr_matrix_mcs))

corr_matrix_baseline = np.vstack((np.reshape(np.array(["E"] + cols[:6]), (1,-1)), corr_matrix_baseline))
corr_matrix_baseline = np.hstack((np.reshape(np.array(["_", "E"] + cols[:6]), (-1,1)), corr_matrix_baseline))

with open(os.path.join(dump_path_tables_mcs, "correlation_matrix" + label_mcs + ".txt"), "w") as f:
    f.write(np.array2string(corr_matrix_mcs, max_line_width=200, precision= 3))

with open(os.path.join(dump_path_tables_baseline, "correlation_matrix" + label_baseline + ".txt"), "w") as f:
    f.write(np.array2string(corr_matrix_baseline, max_line_width=200, precision= 3))
