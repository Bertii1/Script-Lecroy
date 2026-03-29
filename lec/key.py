# educational use only
from crypto import encrypt, decrypt
from binascii import hexlify, unhexlify
from struct import pack, unpack


def decode(ok):
	pt = decrypt(unhexlify(ok.replace("-", "")))
	# convert to iid, flags, mask
	b0, b1, b2, flags, mask = unpack(">BBBBL", pt)
	if flags & 0x40:
		iid = (b1<<16) | (b0<<8) | b2
	else:
		iid = (b0<<16) | (b1<<8) | b2
	return iid, flags, mask


def encode(iid, flags, mask):
	b0 = iid>>16
	b1 = (iid>>8) & 0x0FF
	b2 = iid & 0x0FF
	if flags & 0x40:
		iid = (b1<<16) | (b0<<8) | b2
	else:
		iid = (b0<<16) | (b1<<8) | b2

	pt = pack(">LL", (iid<<8)+flags, mask)
	res = hexlify(encrypt(pt)).upper()
	return res[0:4]+"-"+res[4:8]+"-"+res[8:12]+"-"+res[12:16]

__all__ = ["decode", "encode"]