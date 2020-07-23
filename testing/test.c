#include <stdio.h>
#include <stdint.h>

#include "snakessl.h"


int main(){
    
    FILE *hash_file = fopen("hash_file.bin", "rb");
    unsigned char signed_hash[256];
    fread(signed_hash, 1, 256, hash_file);
    fclose(hash_file);
    
    FILE *public_key_file = fopen("public_key_file.bin", "rb");
    unsigned char exponent[8];
    uint16_t exp_size = 8;
    fread(exponent, 1, 8, public_key_file);
    unsigned char modulus[256];
    fread(modulus, 1, 256, public_key_file);
    fclose(public_key_file);
    
    unsigned char *data = "this is a test string to be hashed. compress me!";
    for(int i = 0; i < 256; i++){
        printf("0x%x/", signed_hash[i]);
    }
    printf("\n0x");
    for(int i = 0; i < 256; i++){
        printf("%x", modulus[i]);
    }
    printf("yo\n");
    /*
    for(int i = 0; i < exp_size; i++){
        if(exponent[i] == 0x0){
            printf("0x00/");
        } else if(exponent[i] == 0x1){
            printf("0x01/");
        } else {
            printf("error: %ud", exponent[i]);
        }
    }
    */
    printf("%d", verify_rsa_signature(signed_hash, modulus, exponent, exp_size, data, 49));
    printf("\n");
    return 0;
}