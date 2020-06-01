#!/usr/bin/env python
import getopt, sys
import binascii
import struct
import array
import os
import pysodium

import pureelib.plumbing.subspecs as plumbing_subspecs
import pureelib.plumbing.common as plumbing_common

# TODO: Support password slots
# TODO: Support subvolumes
# TODO: Support anti-forensic region
# TODO: Write end-of-disk shadow header

# Format a disk wih the given data and specified subspec
def puree_format(d, # device
                 c, # cipher
                 p, # password_file
                 password, # password
                 w, # warn on password changes
                 h, # derive key from password
                 v  # show verbose output
                 ):

    # Sanity checks
    blockdev_size = get_blockdev_size(d)
    mebibyte = 1048576 # bytes
    if(blockdev_size<=2*mebibyte):
        raise RuntimeError("Block device <cipherdevice> is too small (<=2MiB bytes) to format.")
    if(blockdev_size%512!=0):
        raise RuntimeError("Block device <cipherdevice> is not a multiple of 512, which is too weird to continue.")
    
    # Verify that the subspec is valid
    if plumbing_subspecs.subspec_name_to_id(c) == None:
        raise ValueError('Unsupported subspec: '+c)

    # Initialize Salt
    salt = pysodium.randombytes(24)

    # Read the password from the password file
    if(password == None):
        password = plumbing_common.read_password_from_file(p)

    # Calculate box_key
    # TODO: Support slots, so box_key can be found from multiple passwords
    #       For now, box_key == blake2b(salt||password)
    pwhash_parameters = plumbing_common.calculate_pwhash_parameters(password)
    pwhash = plumbing_common.calculate_pwhash(salt,password,pwhash_parameters)
    box_key = pwhash

    # Initialize Box Two (With highly-coupled assumptions about which subspecs we suppor)
    key_size = 0
    if c == plumbing_subspecs.DiskAes256XtsPlain64.subspec_name():
        box_two = plumbing_subspecs.DiskAes256XtsPlain64()
        key_size = 64
    elif c == plumbing_subspecs.DiskAes256CbcEssivSha256BoxTwo.subspec_name():
        box_two = plumbing_subspecs.DiskAes256CbcEssivSha256BoxTwo()
        key_size = 32
    elif c == plumbing_subspecs.DiskAes128XtsPlain64.subspec_name():
        box_two = plumbing_subspecs.DiskAes128XtsPlain64()
        key_size = 32
    elif c == plumbing_subspecs.DiskAes128CbcEssivSha256BoxTwo.subspec_name():
        box_two = plumbing_subspecs.DiskAes128CbcEssivSha256BoxTwo()
        key_size = 16
    else:
        raise ValueError('Unsupported subspec: '+c)
    box_two.logical_start_sector = (1*mebibyte)//512
    box_two.num_sectors = (blockdev_size-2*mebibyte)//512
    box_two.key  = pysodium.randombytes(key_size) 
    
    # Initialize Box One
    box_one = plumbing_subspecs.PureeBoxOne()
    box_one.subspec = plumbing_subspecs.subspec_name_to_id(c)
    if(box_one.subspec == None):
        raise ValueError('Unsupported subspec: '+c)
    box_one.total_slots = 0
    box_one.used_slots = 0
    box_one.len_of_box_2 = box_two.get_inner_size()

    # Encrypt Box One
    box_one_enc = plumbing_common.encrypt_box(box_key,1,box_one.pack())

    # Encrypt Box Two
    box_two_enc = plumbing_common.encrypt_box(box_key,2,box_two.pack())

    # Now, write to the disk
    with open(d, 'r+b') as f:
        f.seek(0)
        combined_header = salt + box_one_enc + box_two_enc
        mib = 1048576
        filler = pysodium.randombytes(mib - len(combined_header))
        f.write(combined_header+filler)

    # Return all headers
    return [salt,box_one,box_two]

def get_blockdev_size(path):
    """Return device size in bytes.
    """
    with open(path, 'rb') as f:
        return f.seek(0, 2) or f.tell()
