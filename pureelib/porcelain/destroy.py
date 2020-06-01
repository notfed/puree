#!/usr/bin/env python3
import sys
import getopt
import binascii
import struct
import array
import getpass

import pureelib.plumbing.destroy as plumbing_destroy

# If no cipher was provided, explain command-line options to the user
def explain_options():
    print(
'''usage: puree destroy [-v] [-f] [-q] <device>

For more information, type 'puree help'.''')
    sys.exit(2)

def puree_destroy(argv):

    # Parse options
    try:
        options_tuples, arguments = getopt.gnu_getopt(argv[2:], "vfq")
        options = dict(options_tuples)
    except getopt.error as err:
        explain_options()

    # Get required arguments
    if len(arguments) < 1:
        explain_options()
    device = arguments[0]

    # Put options in variables
    v = (options.get('-v') != None)
    f = (options.get('-f') != None)
    q = (options.get('-q') != None)

    # Prompt user for confirmation
    if(not f):
        print(f"WARNING: This will DESTROY ALL DATA on the device '{device}'.")
        result = input("To proceed, type destroy in all caps: ")
        if(result != "DESTROY"):
            print("Aborting.")
            sys.exit(2)

    # Commence destruction
    plumbing_destroy.puree_destroy(device, v, q)

    # Done
    print("")
    print("Done. All data on the disk has been destroyed.")
