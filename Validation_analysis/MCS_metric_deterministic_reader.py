import sys
import os
import matplotlib.pyplot as plt
import pickle
import pathlib as pl

sys.path.append(str(list(pl.Path(__file__).parents)[1]))


def determinisic_energy_pdf_cdf_plot(save_bool, return_data = False):

    metric_path = os.path.join(os.path.dirname(__file__), "deterministic_mcs_metric_storage")
    download_path = os.path.join(os.path.expanduser("~"), "Downloads")

    for file in os.listdir(metric_path):
        if "energy_rv" in file:
            with open(os.path.join(metric_path, file), "rb") as f:
                energy_rv = pickle.load(f)

    x, pdf, cdf = energy_rv.plt()

    if return_data:
        return  x, pdf, cdf

    plt.clf()
    plt.figure(figsize=(10,6))
    plt.plot(x/3.6e6, pdf*3.6e6, "-.", label= "pdf")
    plt.xlabel("Energy [KwH]")
    plt.ylabel("PDF")
    handles1, labels1 = plt.gca().get_legend_handles_labels()
    plt.grid(lw=0.8, alpha=0.8)
    plt.twinx()
    plt.plot(x/3.6e6, cdf, "-", color="C1", label= "cdf")
    plt.ylabel("CDF")
    handles2, labels2 = plt.gca().get_legend_handles_labels()
    handles = handles1 + handles2
    labels = labels1 + labels2

    # Create the legend and title
    plt.legend(handles, labels)
    plt.suptitle("Deterministic design")

    if save_bool:
        plt.savefig(os.path.join(download_path, "deterministic_MCS") + "_PdfCdf_" +  ".pdf", bbox_inches= "tight")
    else:
        plt.show()


determinisic_energy_pdf_cdf_plot(True)