from Crypto.PublicKey import RSA

def generate_export():
    key = RSA.generate()
    print(key)