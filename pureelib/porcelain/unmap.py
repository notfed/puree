#!/usr/bin/env python3
import getopt, sys
import binascii
import struct
import array
import subprocess

import pureelib.plumbing.format as plumbing_format
import pureelib.plumbing.subspecs as plumbing_subspecs
import pureelib.plumbing.common as plumbing_common
import pureelib.plumbing.show as plumbing_show

# Explain command-line options to user
def explain_options():
    print(
'''usage: puree unmap [-v] [-p <password_file>] <plaindevice>

For more information, type 'puree help'.''')
    sys.exit(2)

def puree_unmap(argv):

    # Parse options
    try:
        options_tuples, arguments = getopt.gnu_getopt(argv[2:], ":v", [])
        options = dict(options_tuples)
    except getopt.error as err:
        explain_options()

    if(len(arguments)<1):
        explain_options()

    # Put options in variables
    plaindevice = arguments[0]
    verbose = (options.get('-v') != None)

    # Unmap the device
    exit_code = subprocess.call(['dmsetup','remove', plaindevice])

    # Print results
    if(exit_code == 0):
        print("Successfully unmapped '" + plaindevice + "'.")
    else:
        plumbing_common.eprint("Failed to unmap device.")
