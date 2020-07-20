from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Util import Padding
from Crypto.Signature import pkcs1_15
import struct

def protect_firmware(infile, outfile, version, message):
    with open(infile, 'rb') as f:
        fw = f.read()
    metadata = struct.pack("<HH", version, len(fw))
    fw = fw + message.encode() + b'\00'
    with open("secret_build_output.txt", 'rb') as sec_output:
        aes_key = sec_output.read(16)
        rsa_key = RSA.import_key(sec_output.read()) #get private key
    cipher = AES.new(aes_key, AES.MODE_CBC)
    encrypted_fw = cipher.encrypt(Padding.pad(fw, AES.block_size))
    metadata += struct.pack("<H", len(encrypted_fw))
    hashed_fw = SHA256.new(data=metadata + encrypted_Fw)
    signature = pkcs1_15.new(rsa_key).sign(hashed_fw)
    fw_blob = signature + metadata + encrypted_fw
    with open(outfile, "w+b") as out:
        out.write(fw_blob)
    return 0
