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

RESP_OK = b'\x00'
FRAME_SIZE = 16
def send_hash(ser, signed_hash, debug=False):
    
    # Send signed hash to bootloader.
    if debug:
        print(metadata)
    
    ser.write(signed_hash)
    # Wait for an OK from the bootloader.
    resp = ser.read()
    if resp != RESP_OK:
        raise RuntimeError("ERROR: Bootloader responded with {}".format(repr(resp)))

        
def send_metadata(ser, metadata, debug=False):
    """
    f = unencrypted firmware
    F = encrypted firmware
    signed(hash(metadata| IV | F)) | version | size(f) | size(F) | IV | F
    
    """
    version, firmware_size, encrypted_firm_size = struct.unpack_from('<HHH', metadata)
    print(f'Version: {version}\nFirmware Size: {firmware_size} bytes\nEncrypted Firmware size: {encrypted_firm_size}')

#     # Handshake for update
#     ser.write(b'U')
    
#     print('Waiting for bootloader to enter update mode...')
#     while ser.read(1).decode() != 'U':
#         pass

    # Send size and version to bootloader.
    if debug:
        print(metadata)

    ser.write(metadata)

    # Wait for an OK from the bootloader.
    resp = ser.read()
    if resp != RESP_OK:
        raise RuntimeError("ERROR: Bootloader responded with {}".format(repr(resp)))


def send_frame(ser, frame, debug=False):
    if frame
    ser.write(frame)  # Write the frame...

    if debug:
        print(frame)

    resp = ser.read()  # Wait for an OK from the bootloader

    time.sleep(0.1)

    if resp != RESP_OK:
        raise RuntimeError("ERROR: Bootloader responded with {}".format(repr(resp)))

    if debug:
        print("Resp: {}".format(ord(resp)))


def main(ser, infile, debug):
    # Open serial port. Set baudrate to 115200. Set timeout to 2 seconds.
    with open(infile, 'rb') as fp:
        firmware_blob = fp.read()

    signed_hash = firmware_blob[:256]
    metadata = firmware_blob[256:262]
    iv = firmware_blob[262:278]
    firmware = firmware_blob[278:]
    
    # Handshake for update
    ser.write(b'U')
    
    print('Waiting for bootloader to enter update mode...')
    while ser.read(1).decode() != 'U':
        pass
    
    send_hash(ser, signed_hash, debug=debug)
    send_metadata(ser, metadata, debug=debug)

    for idx, frame_start in enumerate(range(0, len(firmware), FRAME_SIZE)):
        data = firmware[frame_start: frame_start + FRAME_SIZE]

        # Get length of data.
        length = len(data)
        frame_fmt = '>H{}s'.format(length)

        # Construct frame.
        frame = struct.pack(frame_fmt, length, data)

        if debug:
            print("Writing frame {} ({} bytes)...".format(idx, len(frame)))

        send_frame(ser, frame, debug=debug)

    print("Done writing firmware.")

    # Send a zero length payload to tell the bootlader to finish writing it's page.
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
    ser = Serial(args.port, baudrate=115200, timeout=2)
    main(ser=ser, infile=args.firmware, debug=args.debug)



