/*
 * Cryptographic Wrapper for BWSI: Embedded Security and Hardware Hacking
 * Uses BearSSL
 *
 * Ted Clifford
 * (C) 2020
 * 
 * These functions wrap their respective BearSSL implementations in a simpler interface.
 * Feel free to modify these functions to suit your needs.
 */

#include "beaverssl.h"

/*
 * AES-128 CBC Encrypt 
 */
int aes_encrypt(char* key, char* iv, char* data, int len) {    
    br_block_cbcenc_class* ve = &br_aes_big_cbcenc_vtable;
    br_aes_gen_cbcenc_keys v_ec;
    const br_block_cbcenc_class **ec;

    ec = &v_ec.vtable;
    ve->init(ec, key, KEY_LEN);
    ve->run(ec, iv, data, len); 

    return 1;
}

/*
 * AES-128 CBC Decrypt
 */
int aes_decrypt(char* key, char* iv, char* ct, int len) {
    br_block_cbcdec_class* vd = &br_aes_big_cbcdec_vtable;
    br_aes_gen_cbcdec_keys v_dc;
    const br_block_cbcdec_class **dc;

    dc = &v_dc.vtable;
    vd->init(dc, key, KEY_LEN);
    vd->run(dc, iv, ct, len);

    return 1;
}

/*
 * AES-128 GCM Encrypt and Digest
 */
int gcm_encrypt_and_digest(char* key, char* iv, char* pt, int pt_len, char* aad, int aad_len, char* tag) {
    br_aes_ct_ctr_keys bc;
    br_gcm_context gc;
    br_aes_ct_ctr_init(&bc, key, KEY_LEN);
    br_gcm_init(&gc, &bc.vtable, br_ghash_ctmul32);

    br_gcm_reset(&gc, iv, IV_LEN);
    br_gcm_aad_inject(&gc, aad, aad_len);
    br_gcm_flip(&gc);
    br_gcm_run(&gc, 1, pt, pt_len);
    br_gcm_get_tag(&gc, tag);

    return 1;
}

/*
 * AES-128 GCM Decrypt and Verify
 */
int gcm_decrypt_and_verify(char* key, char* iv, char* ct, int ct_len, char* aad, int aad_len, char* tag) {
    br_aes_ct_ctr_keys bc;
    br_gcm_context gc;
    br_aes_ct_ctr_init(&bc, key, KEY_LEN);
    br_gcm_init(&gc, &bc.vtable, br_ghash_ctmul32);

    br_gcm_reset(&gc, iv, IV_LEN);         
    br_gcm_aad_inject(&gc, aad, aad_len);    
    br_gcm_flip(&gc);                        
    br_gcm_run(&gc, 0, ct, ct_len);   
    if (br_gcm_check_tag(&gc, tag)) {
        return 1;
    }
    return 0; 
}

/*
 * SHA-256 Hash
 */
int sha_hash(unsigned char* data, unsigned int len, unsigned char* out) {
    br_sha256_context csha;

    br_sha256_init(&csha);
    br_sha256_update(&csha, data, len);
    br_sha256_out(&csha, out);

    return 32;
}

/*
 * SHA-256 HMAC
 */
int sha_hmac(char* key, int key_len, char* data, int len, char* out) {
    br_hmac_key_context kc;
    br_hmac_context ctx;
    br_hmac_key_init(&kc, &br_sha256_vtable, key, key_len);
    br_hmac_init(&ctx, &kc, 0);
    br_hmac_update(&ctx, data, len);
    br_hmac_out(&ctx, out);

    return 32;
}
