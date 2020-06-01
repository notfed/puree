#!/usr/bin/env python3
import getopt, sys
import binascii
import struct
import array

import pureelib.plumbing.format as plumbing_format
import pureelib.plumbing.subspecs as plumbing_subspecs
import pureelib.plumbing.common as plumbing_common
import pureelib.plumbing.show as plumbing_show
import pureelib.plumbing.unpack as punpack

# Explain command-line options to user
def explain_options():
    print(
'''usage: puree info [-v] [-p <password_file>] <cipherdevice>

For more information, type 'puree help'.''')
    sys.exit(2)

def puree_info(argv):

    # Parse options
    try:
        options_tuples, arguments = getopt.gnu_getopt(argv[2:], "p:v", [])
        options = dict(options_tuples)
    except getopt.error as err:
        print ("puree: " + str(err) + "\n")
        explain_options()

    # Validate number of arguments
    if(len(arguments)<1):
        explain_options()

    # Put options in variables
    device = arguments[0]
    password_file = options.get("-p") 
    verbose = (options.get("-v")!=None)

    # Read password from file, or prompt for password
    password = plumbing_common.prompt_for_password_or_read_from_file(password_file,"Password: ",None)

    # Now, read the device header
    headers = punpack.puree_unpack(device,password)

    # Now, show header information
    print("The disk contains the following header information:")
    print("")
    plumbing_show.puree_show(headers,verbose)
