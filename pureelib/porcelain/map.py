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
import pureelib.plumbing.unpack as punpack
import pureelib.porcelain.help as porcelain_help

# Explain command-line options to user
def explain_options():
    print(
'''usage: puree map [-v] [-p <password_file>] <cipherdevice> <plaindevice>

For more information, type 'puree help'.''')
    sys.exit(2)

def puree_map(argv):

    # Validate root 

    # Parse options
    try:
        options_tuples, arguments = getopt.gnu_getopt(argv[2:], "dnp:v", [])
        options = dict(options_tuples)
    except getopt.error as err:
        explain_options()
    if len(arguments)<2:
        explain_options()

    # Put options in variables
    device = arguments[0]
    plaindevice = arguments[1]
    password_file = options.get('-p')
    verbose = (options.get('-v') != None)

    # Validate and strip '/dev/mapper' from plaindevice
    if not plaindevice.startswith('/dev/mapper/'):
        raise ValueError("puree: error: <plaindevice> must begin with '/dev/mapper/...'")
    plaindevice = plaindevice[len('/dev/mapper/'):]
    if len(plaindevice)==0:
        raise ValueError("puree: error: <plaindevice> must be of the form '/dev/mapper/...'")

    # If password_file was not supplied, read the password from it
    password = plumbing_common.prompt_for_password_or_read_from_file(password_file, "Password: ",None)
    
    # Read the device header
    headers = punpack.puree_unpack(device,password)
    salt = headers[0]
    box1 = headers[1]
    box2 = headers[2]

    # Show header information
    if verbose:
        print("The disk contains the following header information:")
        print("")
        plumbing_show.puree_show(headers,verbose)

    # Assert that the subspec is supported
    subspec_id = box1.subspec
    subspec_name = plumbing_subspecs.subspec_id_to_name(subspec_id)
    if subspec_name == None:
        raise ValueError("Unsupported subspec: " + plumbing_common.to_hex(box1.subspec))

    # Determine the dm-crypt cipher name
    cipher_name = None
    if subspec_id == plumbing_subspecs.DiskAes256XtsPlain64.subspec_id():
        cipher_name = 'aes-xts-plain64'
    elif subspec_id == plumbing_subspecs.DiskAes128XtsPlain64.subspec_id():
        cipher_name = 'aes-xts-plain64'
    elif subspec_id == plumbing_subspecs.DiskAes256CbcEssivSha256BoxTwo.subspec_id():
        cipher_name = 'aes-cbc-essiv:sha256'
    elif subspec_id == plumbing_subspecs.DiskAes128CbcEssivSha256BoxTwo.subspec_id():
        cipher_name = 'aes-cbc-essiv:sha256'
    else:
        raise ValueError("Unsupported subspec: " + plumbing_common.to_hex(box1.subspec))

    # Map the device
    logical_start_sector = str(box2.logical_start_sector)
    num_sectors = str(box2.num_sectors)
    key = plumbing_common.to_hex(box2.key)
    table = ('0 %s crypt %s %s 0 %s %s' \
              % (num_sectors,cipher_name,key,device,logical_start_sector))
    exit_code = subprocess.call(['dmsetup','create', str(plaindevice), '--table', table])

    # Show device name
    if(exit_code == 0):
        print("Device mapped as '/dev/mapper/" + plaindevice + "'.")
    else:
        plumbing_common.eprint("puree: error: failed to map device", exit_code)
