#!/usr/bin/env python3
import sys
import getopt
import binascii
import struct
import array
import getpass

import pureelib.plumbing.format as plumbing_format
import pureelib.plumbing.subspecs as plumbing_subspecs
import pureelib.plumbing.common as plumbing_common
import pureelib.plumbing.show as plumbing_show

# If no cipher was provided, explain command-line options to the user
def explain_options():
    print(
'''usage: puree format [-v] [-p <password_file>] [-f] <device> <subspec> ...

For more information, type 'puree help'.''')
    sys.exit(2)

def puree_format(argv):

    # List of valid subspecs
    subspecs = plumbing_subspecs.all_subspec_names()

    # Parse options
    try:
        options_tuples, arguments = getopt.gnu_getopt(argv[2:], "c:p:Wfv")
        options = dict(options_tuples)
    except getopt.error as err:
        print ("puree:  " + str(err) + "\n")
        explain_options()

    # Prompt for cipher if not provided as argument
    if len(arguments)==0:
        explain_options()
    # If they didn't supply a subspec, we'll help them out
    elif len(arguments) == 1:
        device = arguments[0]
        print("Valid subspecs: ")
        subspecs_map = sorted({(v,k) for v, k in enumerate(subspecs)}, key=lambda x:x[0])
        for subspec in subspecs_map:
            print(f"    {str(subspec[0]+1)}    {subspec[1]}")
        entry = input("Choose a subspec: ")
        subspec = None
        for s in subspecs_map:
            if(str(s[0]+1)==entry or s[1]==entry):
                subspec = s[1]
        if(subspec not in subspecs):
            raise ValueError(f"Not a valid subspec: '{entry}'")
    # Get required arguments
    elif len(arguments) >= 2:
        device = arguments[0]
        subspec = arguments[1]

    # Put options in variables
    password_file = options.get('-p')
    h = (options.get('-h') != None)
    y = (options.get('-f') != None)
    v = (options.get('-v') != None)

    # Read password from file, or prompt for password
    password = plumbing_common.prompt_for_password_or_read_from_file(password_file)

    # Assert that all required options were provided
    if not subspec or not device or (not password_file and not password):
        explain_options()

    # Prompt user for confirmation
    print("You have chosen to format device '"+device+"' with the following options:")
    print("")
    print("    subspec: " + subspec)
    if(password_file):
        print("    Password File: " + password_file)
    if y:
        print("    Not prompting for confirmation.")
    if(not y):
        print("")
        print(f"WARNING: This will DESTROY data on the device '{device}'.")
        result = input("To proceed, type yes in all caps: ")
        if(result != "YES"):
            print("Aborting.")
            sys.exit(2)

    # Format the disk
    with open(device,'r+b') as f:
        headers = plumbing_format.puree_format(f,None,subspec,password_file,password,False,h,v)

    # If -v was chosen, show all the variables
    if(v):
        print("")
        print("Done. The disk was successfully formatted with the following header information:")
        print("")
        plumbing_show.puree_show(headers,v)
    else:
        print("")
        print("Done. The disk was successfully formatted.")
