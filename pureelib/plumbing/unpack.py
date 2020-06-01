#!/usr/bin/env python
import getopt, sys
import binascii
import struct
import array
import os

import pureelib.plumbing.subspecs as plumbing_subspecs
import pureelib.plumbing.common as plumbing_common

# TODO: Support password slots
# TODO: Support anti-forensic region
# TODO: Support subvolumes

# Given device d and password p, extract, decrypt and return header objects
def puree_unpack(device,password):

    # Read first sector from the disk
    with open(device, 'rb') as f:
        f.seek(0)
        prefetch_size = 512 # TODO: With anti-forensic region, should pre-fetch 1MiB
        root_sector = f.read(prefetch_size)
    if(len(root_sector)<512):
        raise RuntimeError("Can't read header: device is smaller than than 512 bytes.")

    # Read salt
    offset_salt_start = 0
    offset_salt_end = 24
    salt = root_sector[offset_salt_start:offset_salt_end]

    # Calculate box_key
    pwhash_parameters = plumbing_common.calculate_pwhash_parameters(password)
    pwhash = plumbing_common.calculate_pwhash(salt,password,pwhash_parameters)
    box_key = pwhash

    # Read, decrypt, and unpack box_one
    offset_box1_start = offset_salt_end
    offset_box1_end = offset_box1_start + plumbing_subspecs.PureeBoxOne.get_ciphertext_size()
    box_one_enc = root_sector[offset_box1_start:offset_box1_end]
    box_one_packed = plumbing_common.decrypt_box(box_key,1,box_one_enc)
    box_one = plumbing_subspecs.PureeBoxOne.unpack(box_one_packed)

    # Verify subspec
    if box_one.subspec not in plumbing_subspecs.all_subspec_ids():
        raise ValueError('Unsupported subspec: '+plumbing_common.to_hex(box_one.subspec))

    # Unpack box2, with highly-coupled assumptions about which subspecs we support
    offset_box2_start = offset_box1_end
    offset_box2_end = offset_box2_start + 16 + box_one.len_of_box_2 
    box_two_enc = root_sector[offset_box2_start:offset_box2_end]
    box_two_packed = plumbing_common.decrypt_box(box_key,2,box_two_enc)
    if box_one.subspec == plumbing_subspecs.DiskAes256CbcEssivSha256BoxTwo.subspec_id():
        box_two = plumbing_subspecs.DiskAes256CbcEssivSha256BoxTwo.unpack(box_two_packed)
    elif box_one.subspec == plumbing_subspecs.DiskAes256XtsPlain64.subspec_id():
        box_two = plumbing_subspecs.DiskAes256XtsPlain64.unpack(box_two_packed)
    elif box_one.subspec == plumbing_subspecs.DiskAes128CbcEssivSha256BoxTwo.subspec_id():
        box_two = plumbing_subspecs.DiskAes128CbcEssivSha256BoxTwo.unpack(box_two_packed)
    elif box_one.subspec == plumbing_subspecs.DiskAes128XtsPlain64.subspec_id():
        box_two = plumbing_subspecs.DiskAes128XtsPlain64.unpack(box_two_packed)
    else:
        raise ValueError('Unsupported subspec: '+plumbing_common.to_hex(box_one.subspec))

    # Return the salt, box_one, box_two
    return [salt,box_one,box_two]

