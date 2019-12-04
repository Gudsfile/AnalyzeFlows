__author__ = "Gudsfile and Wigow "

##########################
# IMPORT                 #
##########################

# 3rd party libs
import matplotlib.pyplot as plt
import numpy as np


##########################
# Functions              #
##########################

def create_graph_log(data: list, fig_name: str = 'graphs/graph_tmp'):
    """
    Create an histogram log scaled from the given data.

    :param data:
    :param fig_name:
    :return:
    """
    print(data)
    plt.xlabel('range')
    plt.ylabel('log(nb flows)')

    value_max = max(data)
    value_min = 0
    value_step = 1000 if len(data) >= 1000 else 1
    value_range = range(value_min, value_max, value_step)

    plt.hist(data, range=value_range, bins=value_range, log=True)
    log_bins = np.logspace(
        np.log10(value_range[0]),
        np.log10(value_range[-1]),
        len(value_range)
    )
    plt.hist(data, bins=log_bins, range=log_bins)
    # plt.xscale('log')

    plt.savefig(fig_name)
