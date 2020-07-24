// DOCUMENTATION NEEDED
/* 
 * Wrapper around a bearssl implementation of RSA signing
 * Made by Tom Hughes
 *
*/
#include "snakessl.h"
#include <stdio.h>

int verify_rsa_signature(unsigned char *signature, unsigned char *modulus, unsigned char *exponent, uint16_t exp_size, unsigned char *data, uint16_t data_size){
    
    br_rsa_public_key pk;
    pk.n = modulus;
    pk.nlen = MODULUS_SIZE;
    pk.e = exponent;
    pk.elen = (size_t) exp_size;
    
    unsigned char new_hash_buffer[HASH_SIZE];
    unsigned char unsigned_hash_buffer[HASH_SIZE];
    
    sha_hash(data, data_size, new_hash_buffer);
    if(!br_rsa_i32_pkcs1_vrfy(signature, MODULUS_SIZE, BR_HASH_OID_SHA256, HASH_SIZE, &pk, unsigned_hash_buffer)){
        return -1;
    }
    for(int i = 0; i < HASH_SIZE; i++){
        if(new_hash_buffer[i] != unsigned_hash_buffer[i]) return 0;
    }
    return 1;
}
