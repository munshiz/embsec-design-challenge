# design-challenge-the-shifters
design-challenge-the-shifters created by GitHub Classroom

Upon entering our repository, you will see a few folders: bootloader, firmware, testing, and tools. The bootloader folder contains everything needed for the 
bootloader, including bootloader.c (this contains most of the bootloader functionality: receiving data, and authenticating and decrypting it).

The firmware folder just has all of the firmware stuff.

The testing folder contains all of the testing that we did for individual tools and cryptographic primitives. There is no code in here that is actually being 
executed or run.

The tools folder contains all of the tools that you saw in the original design diagram flow: bootloader build (bl_build), firmware protect (fw_protect), 
and firmware update (fw_update).

The bootloader build tool simply builds the bootloader and provisions the keys: AES symmetric key, RSA private key (for signing), RSA public modulus and 
exponent (for authentication). The modulus and exponent are written to the Makefile so that bootloader.c can see it.

The firmware protect tool takes in the unencrypted firmware file and generates a firmware blob according to the following protocol:

 - f = unencrypted firmware
 - F = encrypted firmware
metadata = version | size(f) | size(F)
signed(hash(metadata | IV | F)) | metadata | IV | F

The firmware update tool sends the output of the above process to the bootloader in frames.

This protocol is used because it creates authenticity, integrity, and privacy. By signing the hash of the metadata, AES IV, and encrypted firmware, we confirm 
that the data was not changed in transmission to the bootloader and that it came from the factory.
