import sys
import os
import matplotlib.pyplot as plt
import pickle
import numpy as np
import pathlib as pl
import yaml

sys.path.append(str(list(pl.Path(__file__).parents)[1]))
os.chdir(str(list(pl.Path(__file__).parents)[1]))


def determinisic_energy_pdf_cdf_plot(save_bool, return_data=False):

    with open(
        os.path.realpath(r"input/environment_variables_plotting.yml"), "r"
    ) as yamlfile:
        data = yaml.safe_load(yamlfile)

    metric_path = os.path.join(data["baseline"]["dir"], "mcs_metric")
    # download_path = os.path.join(os.path.expanduser("~"), "Downloads")

    if not os.path.exists(metric_path):
        raise Exception("mcs_metric has not yet been computed for this run")
    else:
        pass

    for file in os.listdir(metric_path):
        if "energy_rv" in file:
            with open(os.path.join(metric_path, file), "rb") as f:
                energy_rv = pickle.load(f)

    x, pdf, cdf = energy_rv.plt()

    if return_data:
        return x, pdf, cdf

    plt.clf()
    plt.figure(figsize=(10, 6))
    plt.plot(x / 3.6e6, pdf * 3.6e6, "-.", label="pdf")
    plt.xlabel("Energy [KwH]")
    plt.ylabel("PDF")
    handles1, labels1 = plt.gca().get_legend_handles_labels()
    plt.grid(lw=0.8, alpha=0.8)
    plt.twinx()
    plt.plot(x / 3.6e6, cdf, "-", color="C1", label="cdf")
    plt.ylabel("CDF")
    handles2, labels2 = plt.gca().get_legend_handles_labels()
    handles = handles1 + handles2
    labels = labels1 + labels2

    # Create the legend and title
    plt.legend(handles, labels)
    plt.suptitle("Deterministic design")

    # Create storage location for data from mcs metrci
    if os.path.exists(os.path.join(data["baseline"], "plots")):
        pass
    else:
        os.mkdir(os.path.join(data["baseline"], "plots"))

    if save_bool:
        plt.savefig(
            os.path.join(data["baseline"], "plots") + "_PdfCdf_" + ".pdf",
            bbox_inches="tight",
        )
    else:
        plt.show()


def pie_chart_energy():
    plt.clf()
    plt.figure(figsize=(10, 10))
    # sizes = np.array(self.df["Energy_dist"][self.conv_lst])[-1]
    with open(
        os.path.realpath(r"input/environment_variables_plotting.yml"), "r"
    ) as yamlfile:
        data = yaml.safe_load(yamlfile)

    metric_path = os.path.join(data["baseline"]["dir"], "mcs_metric")
    label = os.path.split(data["baseline"]["dir"])[-1][3:]

    if not os.path.exists(metric_path):
        raise Exception("mcs_metric has not yet been computed for this run")
    else:
        pass

    dump_path = os.path.join(data["baseline"]["dir"], "plots")

    with open(os.path.join(metric_path, "Ecruise_rv" + label + ".pkl"), "rb") as f:
        Ecruise_rv = pickle.load(f)
    with open(os.path.join(metric_path, "Eclimb_rv" + label + ".pkl"), "rb") as f:
        Eclimb_rv = pickle.load(f)
    with open(os.path.join(metric_path, "Edesc_rv" + label + ".pkl"), "rb") as f:
        Edesc_rv = pickle.load(f)
    with open(os.path.join(metric_path, "Eloit_cr_cv" + label + ".pkl"), "rb") as f:
        Eloit_cr_rv = pickle.load(f)
    with open(os.path.join(metric_path, "Eloit_hov_rv" + label + ".pkl"), "rb") as f:
        Eloit_hov_rv = pickle.load(f)

    lst = [Ecruise_rv, Eclimb_rv, Edesc_rv, Eloit_cr_rv, Eloit_hov_rv]

    sizes = [i.get_expectation() for i in lst]
    labels = ["Cruise", "Climb", "Descend", "Loiter cruise", "Loiter Hover"]
    annotations = []
    for i, phase in enumerate(lst):
        std = phase.best_fit.std(*phase.arg, loc=phase.loc, scale=phase.scale)
        if i != 4:
            annotations.append(
                f"{labels[i]} STD ={np.round(std / 3.6e6, 2)} [kWh]\n{labels[i]} Expectation ={np.round(sizes[i] / 3.6e6, 2)} [kWh]"
            )
        else:
            annotations.append(f"Loiter Hover\nSee energy phase plots")

    # Plotting actual data
    plt.pie(sizes, autopct="%1.1f%%", explode=[0.1, 0.1, 0.1, 0.2, 0.05], startangle=90)

    # Add annotations to the data
    radii = [1.3, 1.4, 1.36, 1.37, 1.22]
    deltax = [-0.19, 0.2, 0.1, 0.2, -0.1]
    deltay = [-0.05, -0.2, -0.1, -0.05, -0.1]
    for i, radius, annotation, dx, dy in zip(
        list(range(len(radii))), radii, annotations, deltax, deltay
    ):
        angle = (
            90
            + sum(sizes[:i]) / sum(sizes) * 360
            + (sizes[i]) / (sum(sizes)) * 360 * 1 / 2
        )
        x = radius * np.cos(np.radians(angle)) + dx
        y = radius * np.sin(np.radians(angle)) + dy
        # plt.annotate(annotation, (x, y), ha='center', va='center')
        plt.text(x, y, annotation, ha="center", va="center")

    # plt.suptitle(self.title)
    plt.savefig(os.path.join(dump_path, "pie_chart_mcs") + ".pdf", bbox_inches="tight")


def hover_loiter_energy():

    metric_path = os.path.join(
        os.path.dirname(__file__), "deterministic_mcs_metric_storage"
    )
    download_path = os.path.join(os.path.expanduser("~"), "Downloads")

    with open(os.path.join(metric_path, "Eloit_hov_rv.pkl"), "rb") as f:
        Eloit_hov_rv = pickle.load(f)

    plt.figure(figsize=(10, 10))
    hist, edges, patches = plt.hist(
        Eloit_hov_rv.data / 3.6e6,
        density=True,
        lw=2,
        rwidth=0.85,
        color="lightsteelblue",
        edgecolor="k",
    )
    plt.ylim([0, 1.1 * np.max(hist[1:])])
    plt.title("Loiter hover conf")
    plt.xlabel("Energy [KwH]")
    plt.ylabel("[-]")
    plt.grid(lw=0.8, alpha=0.8)
    plt.savefig(
        os.path.join(download_path, "deterministic_metric_hover_loiter")
        + "_barchart"
        + ".pdf",
        bbox_inches="tight",
    )
