#!/usr/bin/env python
import getopt, sys
import binascii
import struct
import array
import os

import pureelib.plumbing.subspecs as plumbing_subspecs
import pureelib.plumbing.common as plumbing_common

# Print all information about the given headers
def puree_show(headers,show_sensitive_data):

    # Show puree_salt
    puree_salt = headers[0]
    print("    salt: " + plumbing_common.to_hex(puree_salt))

    # Show box_one
    box_one = headers[1]
    subspec_name = plumbing_subspecs.subspec_id_to_name(box_one.subspec)
    subspec_id_and_name = plumbing_common.to_hex(box_one.subspec) + (" # " + subspec_name if subspec_name else "")
    print("    box_one:")
    if(box_one.total_slots>0):
        print("      subspec     : " + subspec_id_and_name)
        print("      used_slots  : " + str(box_one.used_slots))
        print("      total_slots : " + str(box_one.total_slots))
    else:
        print("      subspec: " + subspec_id_and_name)

    # If subspec is disk_aes256_cbc_essiv_sha256, show its details
    if box_one.subspec in plumbing_subspecs.all_subspec_ids():
        # Show box_two
        box_two = headers[2]
        print("    box_two:")
        print("      logical_start_sector : " + str(box_two.logical_start_sector))
        print("      num_sectors          : " + str(box_two.num_sectors))
        print("      key                  : " + (plumbing_common.to_hex(box_two.key) if show_sensitive_data else "("+str(len(box_two.key))+" bytes)"))
    # If subspec is not supported, give an error
    else:
        raise ValueError('Unsupported subspec (' + plumbing_common.to_hex(box_one.subspec)+")")
