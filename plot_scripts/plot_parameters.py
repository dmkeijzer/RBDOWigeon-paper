import sys
import os
import pathlib as pl

sys.path.append(str(list(pl.Path(__file__).parents)[1]))
os.chdir(str(list(pl.Path(__file__).parents)[1]))

from modules.plotting.npz_reader import npz_tool
import modules.plotting.csv_baseline_reader as csv


# Plot RBDO based optimization
mcs_ploter = npz_tool(True)
mcs_ploter.analyze_all()

print(f"Plot the RBDO based optimization successfully of {os.path.split(csv.data['mcs']['dir'])[-1]}")

# Plot basline
csv.write_all_parameters()
csv.plot_design_params(True)
csv.plot_energy_phases(True)
csv.plot_pie_chart_energy(True)

print(f"Plot the baseline  optimization successfully of {os.path.split(csv.data['baseline']['dir'])[-1]}")


