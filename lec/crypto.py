# educational use only
from Crypto.Cipher import Blowfish
from struct import pack, unpack

key_ct = b"\205\023\064\027\154\014\026\116\230\076\141\360\373\253\252\267"

key = bytes(c ^ 116 for c in reversed(key_ct))

cipher = Blowfish.new(key, Blowfish.MODE_ECB)


# reverse byte order of two dwords
def revd(blk):
	return pack(">LL", *unpack("<LL", blk))


def decrypt(blk):
	return revd(cipher.decrypt(revd(blk)))


def encrypt(blk):
	return revd(cipher.encrypt(revd(blk)))


__all__ = ["decrypt", "encrypt"]