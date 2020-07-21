/*
 * Cryptographic Wrapper for BWSI: Embedded Security and Hardware Hacking
 * Uses BearSSL
 *
 * Ted Clifford
 * (C) 2020
 *
 */

#include "bearssl.h"

#define KEY_LEN 16  // Length of AES key (16 = AES-128)
#define IV_LEN 16   // Length of IV (16 is secure)

/*
 * AES-128 CBC Encrypt 
 * Parameters:
 * key - encryption key
 * iv - initialization vector
 * data - buffer of data to encrypt, ciphertext replaces the unencrypted data in this buffer
 * len - length of data (in bytes) (must be multiple of 16)
 * 
 * Returns:
 * 1 if encryption is successful
 */
int aes_encrypt(char* key, char* iv, char* data, int len);

/*
 * AES-128 CBC Decrypt
 * Parameters:
 * key - decryption key
 * iv - initialization vector
 * data - buffer of data to decrypt, plaintext replaces the encrypted data in this buffer 
 * len - length of data (in bytes) (must be multiple of 16)
 * 
 * Returns:
 * 1 if decryption is successful
 */
int aes_decrypt(char* key, char* iv, char* data, int len);

/*
 * AES-128 GCM Encrypt and Digest
 * Parameters:
 * key - encryption key
 * iv - initialization vector
 * pt - buffer of data to encrypt, ciphertext replaces the plaintext data in this buffer 
 * pt_len - length of plaintext (in bytes) (must be multiple of 16)
 * aad - buffer of additional authenticated data to add to tag
 * aad_len - length of aad (in bytes)
 * tag - output buffer for tag
 * 
 * Returns:
 * 1 if encryption is successful
 */
int gcm_encrypt_and_digest(char* key, char* iv, char* pt, int pt_len, char* aad, int aad_len, char* tag);

/*
 * AES-128 GCM Decrypt and Verify
 * Parameters:
 * key - decryption key
 * iv - initialization vector
 * ct - buffer of data to decrypt, plaintext replaces the ciphertext data in this buffer 
 * ct_len - length of ciphertext (in bytes) (must be multiple of 16)
 * aad - buffer of additional authenticated data to add to tag
 * aad_len - length of aad (in bytes)
 * tag - input buffer for tag
 * 
 * Returns:
 * 1 if tag is verified
 * 0 if tag is not verified
 * 
 * Note: Data will still be decrypted in place even if tag is not verified, it is up to you if you use it.
 */
int gcm_decrypt_and_verify(char* key, char* iv, char* ct, int ct_len, char* aad, int aad_len, char* tag);

/*
 * SHA-256 Hash
 * Parameters:
 * data - buffer of data to hash
 * len - length of data (in bytes)
 * out - output buffer for hash (must be size in bytes of hash output)
 * 
 * Returns:
 * Length of hash
 */
int sha_hash(unsigned char* data, unsigned int len, unsigned char* out);

/*
 * SHA-256 HMAC
 * Parameters:
 * key - HMAC key
 * key_len - length of key (in bytes)
 * data - data buffer to verify
 * len - length of data (in bytes)
 * out - output buffer for HMAC (must be size in bytes of output)
 * 
 * Returns:
 * Length of HMAC
 */
int sha_hmac(char* key, int key_len, char* data, int len, char* out);

