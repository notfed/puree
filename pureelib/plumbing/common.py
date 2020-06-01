#!/usr/bin/env python3
import getopt, sys
import binascii
import struct
import array
import os
import getpass
import ctypes
import hashlib
import pysodium
import argon2

# Common helper functions

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def to_hex(ba):
    return binascii.hexlify(bytearray(ba)).decode()

def from_hex(s):
    return bytearray.fromhex(s)

def u8_to_be(n):
    return struct.pack('>B', n)

def u8_from_be(a):
    return struct.unpack('>B', a)[0]

def u16_to_be(n):
    return struct.pack('>H', n)

def u16_from_be(a):
    return struct.unpack('>H', a)[0]

def u32_to_be(n):
    return struct.pack('>I', n)

def u32_from_be(a):
    return struct.unpack('>I', a)[0]

def u64_to_be(n):
    return struct.pack('>Q', n)

def u64_from_be(a):
    return struct.unpack('>Q', a)[0]

def __check(code):
    if code != 0:
        raise ValueError

# ctypes imports

def bytearray_to_char_array(ba):
    return (ctypes.c_char * len(ba)).from_buffer(bytearray(ba))

# Common boxing/unboxing functions

def encrypt_box(box_key,box_number,plaintext_header_packed):
    r = pysodium.crypto_aead_chacha20poly1305_encrypt(bytearray_to_char_array(plaintext_header_packed),None,u64_to_be(box_number),box_key)
    return r

def decrypt_box(box_key,header_number,ciphertext_header_packed):
    try:
        return pysodium.crypto_aead_chacha20poly1305_decrypt(bytearray_to_char_array(ciphertext_header_packed),None,u64_to_be(header_number),box_key)
    except ValueError:
        raise ValueError('Failed to decrypt disk.  Either (A) the device is not formatted with PUREE, (B) the password is invalid, or (C) the disk has been corrupted.')

# Common Password Functions

def read_password_from_file(p):
    # Read the password from the password file
    password = None
    with open(p, 'r') as f:
        password = f.read()
    return password

# Functions for deriving pwhash

parameter_char_lookup = { # TODO: Start with alpha
        'a': {'p': 0,  'm': 0, 't': 0},
        'b': {'p': 1,  'm': 16, 't': 1},
        'c': {'p': 1,  'm': 18, 't': 1},
        'd': {'p': 4,  'm': 18, 't': 4},
        'e': {'p': 1,  'm': 20, 't': 1},
        'f': {'p': 4,  'm': 20, 't': 4},
        'g': {'p': 1,  'm': 22, 't': 1},
        'h': {'p': 4,  'm': 22, 't': 4},
        'i': {'p': 1,  'm': 24, 't': 1},
        'j': {'p': 4,  'm': 24, 't': 4},
}

def prompt_for_password(prompt,prompt_confirm):
    if sys.stdin.isatty():
        password1 = getpass.getpass(prompt)
        if(prompt_confirm):
            password2 = getpass.getpass("Choose a password (again to confirm): ")
            if(password1 != password2):
                raise ValueError("puree: error: passwords don't match")
        password_verify(password1)
    else:
        raise ValueError("puree: error: password was not supplied via tty or command-line argument")
    return password1

def prompt_for_password_or_read_from_file(password_file, prompt="Choose a password: ", prompt_confirm="Choose a password (again to confirm): "):
    if(password_file):
        password = read_password_from_file(password_file) 
    else:
        password = prompt_for_password(prompt,prompt_confirm)
    return password
    

def password_verify(password):
    if len(password)==0 or not parameter_char_lookup.get(password[0]):
        raise ValueError("puree: error: password's first digit must be a parameter char ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', or 'i')")

def calculate_pwhash_parameters(password):
    c = password[0] if len(password)>0 else "-"
    t = parameter_char_lookup
    password_verify(password)
    return [t[c]['p'],t[c]['m'],t[c]['t']]


def calculate_pwhash(salt,password,pwhash_parameters):
    pwhash = None
    t = pwhash_parameters[0]
    m = 2**(pwhash_parameters[1])
    p = pwhash_parameters[2]
    if(t==0):
        pwhash = hashlib.blake2b(salt+password.encode("utf-8"), digest_size=32).digest()
    else:
        pwhash = argon2.low_level.hash_secret_raw(
            password.encode('utf-8'), salt,
            time_cost=t, memory_cost=m, parallelism=p, hash_len=32, 
            type=argon2.low_level.Type.ID
        )
    return pwhash
