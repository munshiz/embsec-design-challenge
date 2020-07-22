"""
Firmware Bundle-and-Protect Tool

"""

"""
    Metadata(version number, size of encrypted firmware) will come prepended and a copy will come signed with the hash of the firmware.
    An unsigned metadata will come prepended to the signed hash in order for us to be able to display and send it here.
    
    The data looks like this:
    Old idea:
    plaintext(version | size(F)) | signed(hash(F) | version | size(F) | IV) | F
    
    New idea:
    f = unencrypted firmware
    F = encrypted firmware
    signed(hash(F)) | version | size(f) | message | len(F) | IV | F
    
    The size of the decrypted firmware will come in the encrypted metadata in the actual firmware. 
    The metadata appended to the hash will incorporate only a copy of the version number and a calculated size of the encrypted firmware,
    and will be the same metadata that will be prepended to the signed hash.
    
    This leaves us with 3 copies of the version number and 2 copies of the encrypted firmware's size, 
    and no need to change the send_metadata method.
    
"""

import argparse
import struct
#import cryptodome stuff
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import Crypto.signature
from Crypto.Hash import SHA256
import Crypto.Random


def protect_firmware(infile, outfile, version, message):
    # Load firmware binary from infile
    with open(infile, 'rb') as fp:
        firmware = fp.read()
    
    key = Crypto.Random.get_random_bytes(16)
    
    encrypted_firmware = AES.new(key, AES.MODE_CBC)
    iv = encrypted_firmware.iv
    
    plaintext_part_1 = version
    plaintext_part_2 = len(encrypted_firmware)
    
    hashed_firmware = SHA256.new()
    hashed_firmware.update(encrypted_firmware)
    
    rsa_key = RSA.generate(2048)
    

    # Append null-terminated message to end of firmware
    firmware_and_message = firmware + message.encode() + b'\00'

    # Pack version and size into two little-endian shorts
    metadata = struct.pack('<HH', version, len(firmware))

    # Append firmware and message to metadata
    firmware_blob = metadata + firmware_and_message

    # Write firmware blob to outfile
    with open(outfile, 'wb+') as outfile:
        outfile.write(firmware_blob)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Firmware Update Tool')
    parser.add_argument("--infile", help="Path to the firmware image to protect.", required=True)
    parser.add_argument("--outfile", help="Filename for the output firmware.", required=True)
    parser.add_argument("--version", help="Version number of this firmware.", required=True)
    parser.add_argument("--message", help="Release message for this firmware.", required=True)
    args = parser.parse_args()

    protect_firmware(infile=args.infile, outfile=args.outfile, version=int(args.version), message=args.message)
