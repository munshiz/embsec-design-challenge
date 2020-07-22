/* 
 * Wrapper around a bearssl implementation of RSA signing
 * Made by Tom Hughes
 *
 * Note: there is no use or implementation of ssl in this file
 *
*/
#include <stdint.h>
#include "bearssl.h"
#include "beaverssl.h"

#define MODULUS_SIZE 256
#define HASH_SIZE 32

/*
 * PKCS#1 v1.5 signature verification
 * Parameters:
 * signature: the signed hash
 * modulus: the rsa modulus, using MODULUS_SIZE bytes
 * exponent: the public exponent in big endian format. leading 0 bytes are allowed.
 * exp_size: size of the exponent in bytes
 * data: the data authenticity to be checked
 * data_len: the length of the data
 *
 * return values:
 * 1: successful verification
 * 0: failure, data may have been tampered with. you are advised to send a snarky response to the sender and reset the chip.
 * 
 * returns -1 on bearssl failure from user input error.
*/
int verify_rsa_signature(unsigned char *signature, unsigned char *modulus, unsigned char *exponent, uint16_t exp_size, unsigned char *data, uint16_t data_size);