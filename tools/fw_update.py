#!/usr/bin/env python
"""
Firmware Updater Tool

A frame consists of two sections:
1. Two bytes for the length of the data section
2. A data section of length defined in the length section

[ 0x02 ]  [ variable ]
--------------------
| Length | Data... |
--------------------

In our case, the data is from one line of the Intel Hex formated .hex file

We write a frame to the bootloader, then wait for it to respond with an
OK message so we can write the next frame. The OK message in this case is
just a zero
"""

import argparse
import struct
import time

from serial import Serial

"""
f = unencrypted firmware
F = encrypted firmware
metadata = version | size(f) | size(F)
signed(hash(metadata | IV | F)) | metadata | IV | F
"""
RESP_OK = b'\x00'
FRAME_SIZE = 16
def send_hash(ser, signed_hash, debug=False):
    """
    Sends signed hash of the firmware, IV, and metadata over serial to the bootloader.
    The data looks like this: signed(hash(metadata | IV | F))
    After sending the signed hash, waits for confirmation from the bootloader.
    
    Returns: 0 if a confirmation is recieved from the bootloader. Otherwise throws an error.
    Outputs: sends signed hash over serial
    
    Arguments:
    {ser}: serial write
    {signed_hash}: the signed hash from the main method to be sent
    {debug}: if this is set to true, it allows us to see the metadata (for debugging purposes)
    
    """
    
    # Send signed hash to bootloader.
    if debug:
        print(metadata)
    
    ser.write(signed_hash) # actually sends the signed hash
    
    # Wait for an OK from the bootloader.
    resp = ser.read()
    if resp != RESP_OK:
        raise RuntimeError("ERROR: Bootloader responded with {}".format(repr(resp)))
    else:
        return 0

        
def send_metadata(ser, metadata, debug=False):
    """
    Prints plaintext metadata and sends it to the bootloader.
    The data looks like this: version | size(f) | size(F)
    After sending the metadata, waits for confirmation from the bootloader
    
    Returns: 0 if a confirmation is recieved from the bootloader. Otherwise throws an error.
    Outputs: sends plaintext metadata over serial
    
    Arguments:
    {ser}: serial write functionality
    {metadata}: the data to be sent, from the main function
    {debug}: if this is set to true, it allows us to see the metadata (for debugging purposes)
    
    """
    
    
    version, firmware_size, encrypted_firm_size = struct.unpack_from('<HHH', metadata)
    print(f'Version: {version}\nFirmware Size: {firmware_size} bytes\nEncrypted Firmware size: {encrypted_firm_size}')

#     # Handshake for update                                      #old code: moved to main
#     ser.write(b'U')
    
#     print('Waiting for bootloader to enter update mode...')
#     while ser.read(1).decode() != 'U':
#         pass

    # Send size and version to bootloader.
    if debug:
        print(metadata)

    ser.write(metadata) # send metadata to bootloader

    # Wait for an OK from the bootloader.
    resp = ser.read()
    if resp != RESP_OK:
        raise RuntimeError("ERROR: Bootloader responded with {}".format(repr(resp)))
    else:
        return 0

def send_iv(ser, iv, debug=False):
    """
    Prints plaintext AES IV and sends it to the bootloader.
    After sending the IV, waits for confirmation from the bootloader
    
    Returns: 0 if a confirmation is recieved from the bootloader. Otherwise throws an error.
    Outputs: sends plaintext AES IV over serial
    
    Arguments:
    {ser}: serial write functionality
    {iv}: the data to be sent, from the main function
    {debug}: if this is set to true, it allows us to see the iv (for debugging purposes)
    
    """
    if debug:
        print(iv)
    ser.write(iv)
    
    resp = ser.read()
    if resp != RESP_OK:
        raise RuntimeError("ERROR: Bootloader responded with {}".format(repr(resp)))
    else:
        return 0
    
def send_frame(ser, frame, debug=False):
    """
    Sends a frame of data to the bootloader.
    If the bootloader does not confirm, raises an error.
    The structure of the frames is explained at the top of the page
    
    Returns: 0 if a confirmation is recieved from the bootloader. Otherwise throws an error.
    Outputs: sends a frame over serial
    """
    
    ser.write(frame)  # Write the frame...

    if debug:
        print(frame)

    resp = ser.read()  # Wait for an OK from the bootloader

    time.sleep(0.1)

    if debug:
        print("Resp: {}".format(ord(resp))) # if debug is enabled, print the bootloader's response
    
    if resp != RESP_OK:
        raise RuntimeError("ERROR: Bootloader responded with {}".format(repr(resp)))
    else:
        return 0

def main(ser, infile, debug):
    """
    Arguments are:
    {ser}: serial read/write
    {infile}: the entire firmware blob (created by fw_protect.py) to be sent to the bootloader
    {outfile}:
    """
    
    with open(infile, 'rb') as fp:
        firmware_blob = fp.read() # read firmware blob from {infile}

    # declares a bunch of variables for use in send_hash, send_metadata, and send_iv methods
    signature_length = 256 # the signature is 256 bytes long
    metadata_length = 6 # the metadata is 6 bytes long
    iv_length = 16 # the IV is 16 bytes long
    
    # signed(hash(metadata | IV | F)) | metadata | IV | F
    metadata_start = signature_length # the metadata begins after the signature
    iv_start = metadata_start + metadata_length # the IV begins after the metadata
    firmware_start = iv_start + iv_length # the firmware begins after the IV
    
    #assignments to corresponding sections of the {firmware_blob}
    signed_hash = firmware_blob[signature_length] # starts in the beginning
    metadata = firmware_blob[metadata_start : iv_start]
    iv = firmware_blob[iv_start : firmware_start]
    firmware = firmware_blob[firmware_start: ]
    
    # Handshake for update
    ser.write(b'U')
    
    print('Waiting for bootloader to enter update mode...')
    while ser.read(1).decode() != 'U':
        pass
    
    send_hash(ser, signed_hash, debug=debug) # send the signed hash
    send_metadata(ser, metadata, debug=debug) # send the metadata
    send_iv(ser, iv, debug=debug) #sends AES IV
    for idx, frame_start in enumerate(range(0, len(firmware), FRAME_SIZE)): 
        # breaks up  data to be sent into 16 byte frames for the bootloader to take in
        data = firmware[frame_start: frame_start + FRAME_SIZE]

        # Get length of data.
        length = len(data)
        frame_fmt = '>H{}s'.format(length)

        # Construct frame.
        frame = struct.pack(frame_fmt, length, data)

        if debug:
            print("Writing frame {} ({} bytes)...".format(idx, len(frame)))

        send_frame(ser, frame, debug=debug) # sends frame
    print("Done writing firmware.")
    
    # Send a zero length payload to tell the bootlader to finish writing its page.
    ser.write(struct.pack('>H', 0x0000))

    return ser


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Firmware Update Tool')

    parser.add_argument("--port", help="Serial port to send update over.",
                        required=True)
    parser.add_argument("--firmware", help="Path to firmware image to load.",
                        required=True)
    parser.add_argument("--debug", help="Enable debugging messages.",
                        action='store_true')
    args = parser.parse_args()

    print('Opening serial port...')
    # Open serial port. Set baudrate to 115200. Set timeout to 2 seconds.
    ser = Serial(args.port, baudrate=115200, timeout=2)
    main(ser=ser, infile=args.firmware, debug=args.debug)



