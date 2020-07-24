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
    # WARNING: ADD DOCUMENTATION
	return "{" + ",".join([hex(c) for c in binary_string]) + "}"


def make_bootloader():
    """
    Build the bootloader from source.
    
    This also loads all keys (symmetric and non-symmetric) into secret_build_output.txt

    Return:
        True if successful, False otherwise.
    """
    # Change into directory containing bootloader.
    bootloader = FILE_DIR / '..' / 'bootloader'
    os.chdir(bootloader)
    
    rsa_key = RSA.generate(2048) # generates an RSA key
    #need to provision: RSA modulus, exponent, exponent size
    modulus = rsa_key.publickey().n
    exponent = rsa_key.publickey().e
    exponent_size = 8

    # f = open('mykey.pem','wb')
    # f.write(rsa_key.export_key('PEM'))
    # f.close()
    aes_key = AES.get_random_bytes(16) # generates a random 16 byte AES key

    # print('BEFORE WRITING: \n')
    # print('RSA key: ', rsa_key)
    # print('AES key: ', aes_key)

    with open('secret_build_output.txt', 'w+b') as fh: # writes the AES and RSA public key in the {secret_build_output.txt} file
        fh.write(aes_key)
        fh.write(rsa_key.export_key())

    subprocess.call('make clean', shell=True)
#     status = subprocess.call('make')
#     status = subprocess.call('make KEY=VALUE', shell=True)
    status = subprocess.call(f'make AES_KEY={to_c_array(aes_key)} MODULUS={to_c_array((rsa_key.publickey().n).to_bytes(256, "big"))} EXPONENT={to_c_array(struct.pack(">Q", rsa_key.publickey().e))} EXP_SIZE=8', shell=True)

    # Return True if make returned 0, otherwise return False.
    return (status == 0)


if __name__ == '__main__':
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
    