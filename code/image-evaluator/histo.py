#!/usr/bin/python

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import sys

def main():
    data = np.loadtxt('histo2.txt')
    plt.hist(data, bins=5, range=[1, 6])
    plt.savefig(sys.argv[1])
    
if __name__ == "__main__":
    main()

