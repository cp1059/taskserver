

import hashlib,binascii,os


def md5(str):
    return hashlib.md5(str.encode("utf8")).hexdigest()

def get_token():
    return binascii.hexlify(os.urandom(80)).decode()