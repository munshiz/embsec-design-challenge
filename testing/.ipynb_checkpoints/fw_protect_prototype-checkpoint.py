from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Util import Padding
from Crypto.Signature import pkcs1_15
import struct
"""

"""
def protect_firmware(infile, outfile, version, message):
    with open(infile, 'rb') as f: #gets firmware
        fw = f.read()
        
    metadata = struct.pack("<HH", version, len(fw)) #packs metadata: version, length  of unencrypted firmware
    fw = fw + message.encode() + b'\00' #adds message to end of firmware
    
    with open("secret_build_output.txt", 'rb') as sec_output:
        aes_key = sec_output.read(16) #get symmetric key
        rsa_key = RSA.import_key(sec_output.read()) #get private key
        
    cipher = AES.new(aes_key, AES.MODE_CBC) #creates AES object
    
    encrypted_fw = cipher.encrypt(Padding.pad(fw, AES.block_size)) #encrypts
    
    metadata += struct.pack("<H", len(encrypted_fw)) #adds the length of encrypted firmware to metadata
    
    hashed_fw = SHA256.new(data = metadata + cipher.iv + encrypted_Fw) #hashes the metadata, IV, and encrypted firmware
    
    signature = pkcs1_15.new(rsa_key).sign(hashed_fw) #signs the hashed firmware
    
    fw_blob = signature + metadata + cipher.iv + encrypted_fw #creates blob to be sent to bootloader
    
    with open(outfile, "w+b") as out: #writes firmware blob to another file
        out.write(fw_blob)
    return 0
