import numpy as np


def norm(a):
    """normalizes a string by its average and sd"""
    a=(np.array(a)-np.average(a))/np.std(a)
    return a