import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
import os

sns.set_style("whitegrid")
alpha_level = 0.5

chunksize = 1000

# Generate samples for each distribution
trans_stoch = [
    stats.halfnorm.rvs(loc=95, scale=50, size=chunksize),
    stats.uniform.rvs(loc=300, scale=700, size=chunksize),
    stats.uniform.rvs(scale=600, size=chunksize),
    stats.genextreme.rvs(0.94, loc=309.40, scale=84.96, size=chunksize),
]

# Create a 2x2 matrix of subplots

# Plot first distribution
plt.hist(trans_stoch[0], bins=20, density=True, color="blue", alpha=alpha_level)
x = np.linspace(min(trans_stoch[0]), max(trans_stoch[0]), 1000)
pdf = stats.halfnorm.pdf(x, loc=95, scale=50)
plt.plot(x, pdf, color="red", label="Transition Height")
plt.xlabel("Height [m]")
plt.ylabel("Frequency [-]")
plt.legend()
plt.grid(alpha=0.7)
plt.savefig(
    os.path.join(os.path.expanduser("~"), "Downloads", "halfnormal_plot.pdf"),
    bbox_inches="tight",
)

plt.clf()

plt.hist(trans_stoch[3], bins=20, density=True, color="blue", alpha=alpha_level)
x = np.linspace(min(trans_stoch[3]), max(trans_stoch[3]), 1000)
pdf = stats.genextreme.pdf(x, 0.94, loc=309.40, scale=84.96)
plt.plot(x, pdf, color="red", label="Mission Range")
plt.xlim([0, max(x)])
plt.xlabel("Range [km]")
plt.ylabel("Frequency [-]")
plt.legend()
plt.grid(alpha=0.7)
plt.savefig(
    os.path.join(os.path.expanduser("~"), "Downloads", "genextreme_plot.pdf"),
    bbox_inches="tight",
)
