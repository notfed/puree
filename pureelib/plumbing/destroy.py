#!/usr/bin/env python
import getopt, sys
import binascii
import struct
import array
import os
import pysodium

import pureelib.plumbing.subspecs as plumbing_subspecs
import pureelib.plumbing.common as plumbing_common

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def blockdev_size(path):
    """Return device size in bytes.
    """
    with open(path, 'rb') as f:
        return f.seek(0, 2) or f.tell()

# Format a disk wih the given data and specified subspec
def puree_destroy(d, # device
                  v,  # show verbose output
                  q   # just destroy first and last MiB
                  ):

    # Calculate how many multiples of 1GiB (and after that, remaining 1MiB) that are on the disk
    device_bytes = blockdev_size(d)
    if device_bytes%1048576!=0:
        raise RuntimeError("Refusing to destroy device: device size isn't a multiple of 1MiB, which is irregular.")
    device_mibs = device_bytes//1048576
    device_gibs_total = device_mibs//1024
    device_gibs_remaining_mibs = device_mibs%1024

    # Quick destroy
    if(q):
        with open(d, 'wb') as f:
            # Destroy first 1MiB
            f.seek(0)
            f.write(pysodium.randombytes(1048576))
            # Destroy last 1MiB
            f.seek(device_bytes-1048576)
            f.write(pysodium.randombytes(1048576))
    # Destroy ENTIRE DISK
    else:
        with open(d, 'wb') as f:
            f.seek(0)
            for g in range(0,device_gibs_total):
                for m in range(0,1024):
                    f.write(pysodium.randombytes(1048576))
                printProgressBar(g, device_gibs_total, prefix = 'Progress:', suffix = 'Complete', length = 50)
            for m in range(0,device_gibs_remaining_mibs):
                f.write(pysodium.randombytes(1048576))
            printProgressBar(device_gibs_total, device_gibs_total, prefix = 'Progress:', suffix = 'Complete', length = 50)
