
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pathlib as pl
import numpy as np

sys.path.append(str(list(pl.Path(__file__).parents)[1]))


from MCS_metric_deterministic_reader import determinisic_energy_pdf_cdf_plot
from npz_reader import npz_tool

npz_path_robust = r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\Monte_carlo_Jun_4_19.15_2023.npz"
npz_path_non_robust = r"C:\Users\damie\OneDrive\Desktop\Damien\Wigeon_proj\logs\valid_data\Monte_Carlo\run_8_Mar_15_16.17\Monte_carlo_Mar_15_16.17_2023.npz"
download_path = os.path.join(os.path.expanduser("~"), "Downloads")


npz_reader = npz_tool(npz_path_robust, save_bool= False)

x_deter, pdf_deter, cdf_deter = determinisic_energy_pdf_cdf_plot(False, return_data= True)
x_mcs, pdf_mcs, cdf_mcs, dist= npz_reader.energy_pdf_cdf_plot(return_data=True)

sns.set(style="white")

plt.clf()
plt.figure(figsize=(10,6))
plt.plot(x_deter/3.6e6, pdf_deter, "-.", label= "PDF Deterministic Design")
plt.plot(x_mcs/3.6e6, pdf_mcs, "-", color="C1", label= "PDF MCS Design ")
plt.vlines([dist.ppf(0.9)/3.6e6], 0, pdf_mcs[np.where(np.abs(x_mcs - dist.ppf(0.9)) < 100000)[0]], color="red", alpha=0.3)
plt.fill_between(x_mcs/3.6e6, pdf_mcs, np.zeros(np.size(x_mcs)), where= (x_mcs > dist.ppf(0.9)), color='red', alpha=0.3)
plt.xlabel("Energy [KwH]")
plt.ylabel("PDF [-]")
plt.grid(lw= 0.8, alpha= 0.8)
plt.legend()
plt.suptitle("MCS vs Deterministic")

plt.savefig(os.path.join(download_path, "comparison_robust_optimizer") + "_Pdf_" +  ".pdf", bbox_inches= "tight")

plt.clf()
plt.figure(figsize=(10,6))
plt.plot(x_deter/3.6e6, cdf_deter, "-.", label= "CDF Deterministic Design")
plt.plot(x_mcs/3.6e6, cdf_mcs, "-", color="C1", label= "CDF MCS Design ")
plt.vlines([dist.ppf(0.9)/3.6e6], 0, pdf_mcs[np.where(np.abs(x_mcs - dist.ppf(0.9)) < 100000)[0]], color="red", alpha=0.3)
plt.fill_between(x_mcs/3.6e6, pdf_mcs, np.zeros(np.size(x_mcs)), where= (x_mcs > dist.ppf(0.9)), color='red', alpha=0.3)
plt.xlabel("Energy [KwH]")
plt.ylabel("PDF [-]")
plt.grid(lw= 0.8, alpha= 0.8)
plt.legend()
plt.suptitle("MCS vs Deterministic")

plt.savefig(os.path.join(download_path, "comparison_robust_optimizer") + "_Pdf_" +  ".pdf", bbox_inches= "tight")