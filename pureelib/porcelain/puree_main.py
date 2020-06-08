#!/usr/bin/env python3
import getopt, sys
import pysodium
import binascii
import struct
import array
import signal
import sys
import argon2
import getopt
import subprocess

import pureelib.plumbing.subspecs as plumbing_subspecs
import pureelib.plumbing.common as plumbing_common

import pureelib.porcelain.help as porcelain_help
import pureelib.porcelain.format as porcelain_format
import pureelib.porcelain.info as porcelain_info
import pureelib.porcelain.map as porcelain_map
import pureelib.porcelain.unmap as porcelain_unmap
import pureelib.porcelain.destroy as porcelain_destroy

# If no cipher was provided, explain command-line options to the user
def explain_options():
    print(
'''usage: 
       puree format  [-v] [-p <password_file>] [-f] <device> <subspec> ...
       puree map     [-v] [-p <password_file>] <cipherdevice> <plaindevice>
       puree unmap   [-v] [-p <password_file>] <plaindevice>
       puree info    [-v] [-p <password_file>] <cipherdevice>
       puree destroy [-v] [-a] [-f] <device>

For more information, type 'puree help'.''')
    sys.exit(2)

def signal_handler(sig, frame):
    print("")
    sys.exit(0)

def main():

    signal.signal(signal.SIGINT, signal_handler)

    # Initialize Pysodium randomness
    pysodium.sodium_init()

    # See if we're in verbose mode
    v = False
    if "-v" in sys.argv[2:]:
        v = True

    try:
        # Pass control over to sub-porcelain
        if(len(sys.argv)<=1):
            explain_options()
        # Show Version
        elif(sys.argv[1] == '--version' or sys.argv[1] == '-version' or sys.argv[1] == 'version'):
            print("1.0.2")
        # Show Man Page
        elif(porcelain_help.asked_for_help(sys.argv[1:])):
            porcelain_help.show_help()
            return 0
        # Invoke Porcelain
        elif(sys.argv[1] == 'format'):
            porcelain_format.puree_format(sys.argv)
        elif(sys.argv[1] == 'info'):
            porcelain_info.puree_info(sys.argv)
        elif(sys.argv[1] == 'map'):
            porcelain_map.puree_map(sys.argv)
        elif(sys.argv[1] == 'unmap'):
            porcelain_unmap.puree_unmap(sys.argv)
        elif(sys.argv[1] == 'destroy'):
            porcelain_destroy.puree_destroy(sys.argv)
        else:
            explain_options()

    except ValueError as e:
        if(v):
            raise e
        print(e)
        sys.exit(2)
    except Exception as e:
        if(v):
            raise e
        print(e)
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print(e)
