#!/usr/bin/env python
"""
Bootloader Build Tool

This tool is responsible for building the bootloader from source and copying
the build outputs into the host tools directory for programming.
"""
import argparse
import os
import pathlib
import shutil
import subprocess

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Util import Padding
from Crypto.Signature import pkcs1_15
from Crypto.Util.Padding import unpad
import struct

FILE_DIR = pathlib.Path(__file__).parent.absolute() # defines the path to the file directory


def copy_initial_firmware(binary_path):
    """
    Copy the initial firmware binary to the bootloader build directory
    Arguments:
    {binary_path} is the path to the firmware binary
    Return:
        None
    """
    # Change into directory containing tools
    os.chdir(FILE_DIR)
    bootloader = FILE_DIR / '..' / 'bootloader'
    shutil.copy(binary_path, bootloader / 'src' / 'firmware.bin') # WARNING: ADD DOCUMENTATION


def to_c_array(binary_string):
    # this method helps export keys to the  makefile so that they can be read in by the bootloader
    # it is called in the make_bootloader method
    # argument {binary_string} is the thing to be put into a c array
	return "{" + ",".join([hex(c) for c in binary_string]) + "}"


def make_bootloader():
    """
    Build the bootloader from source.
    
    This also loads all keys (symmetric and non-symmetric) into secret_build_output.txt

    Return:
        True if successful, False otherwise.
    """
    # Change into directory containing bootloader.
    rsa_key = RSA.generate(2048) # generates a private RSA key object so that a public exponent and modulus can be created
    #need to provision: RSA modulus, exponent, exponent size
    
    # public RSA modulus
    modulus = rsa_key.publickey().n
    # public RSA exponent
    exponent = rsa_key.publickey().e
    # size of exponent, for later use in authentication
    exponent_size = 8

    
    aes_key = AES.get_random_bytes(16) # generates a random 16 byte AES key


    with open('secret_build_output.txt', 'wb+') as fh: # writes the AES and RSA private key in the {secret_build_output.txt} file
        print("test")
        fh.write(aes_key)                              # this allows the fw_protect tool to import these keys and encrypt/sign data
        fh.write(rsa_key.export_key())
        
    bootloader = FILE_DIR / '..' / 'bootloader'
    os.chdir(bootloader)
    
    
    subprocess.call('make clean', shell=True) #allows us to pass in arguments to the make file
    #sets all variables in makefile according to ones above (the aes symmetric key, modulus, exponent, and exponent size)
    status = subprocess.call(f'make KEY={to_c_array(aes_key)} MOD={to_c_array((rsa_key.publickey().n).to_bytes(256, "big"))} EXP={to_c_array(struct.pack(">Q", rsa_key.publickey().e))} E_SIZE=8', shell=True)

    # Return True if make returned 0, otherwise return False.
    return (status == 0)


if __name__ == '__main__':
    # some stuff for building the bootloader
    parser = argparse.ArgumentParser(description='Bootloader Build Tool')
    parser.add_argument("--initial-firmware", help="Path to the the firmware binary.", default=None)
    args = parser.parse_args()
    if args.initial_firmware is None:
        binary_path = FILE_DIR / '..' / 'firmware' / 'firmware' / 'gcc' / 'main.bin'
    else:
        binary_path = os.path.abspath(pathlib.Path(args.initial_firmware))

    if not os.path.isfile(binary_path):
        raise FileNotFoundError(
            "ERROR: {} does not exist or is not a file. You may have to call \"make\" in the firmware directory.".format(
                binary_path))

    copy_initial_firmware(binary_path)
    make_bootloader()
    