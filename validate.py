# educational use only
from sys import argv, exit
import lec.key
import lec.db

if not len(argv) in (2, 3):
	exit("Usage: "+argv[0]+" <key> [options.cfg]")


iid, flags, mask = lec.key.decode(argv[1])
print ("ScopeID: %06X\nFlags:\t %02X\nMask:\t %08X" % (iid, flags, mask))

if len(argv)==3:
	db = lec.db.fromfile(argv[2])
	print ("Options:")
	page = flags & 0x43
	for i in range(32):
		bmsk = 1<<i
		if mask & bmsk:
			idx = (page<<32) | bmsk
			print("%02X-%08X" % (page, bmsk), end=' ')
			if idx in db.options:
				print("%-20s %s" % (db.options[idx].name, db.options[idx].description))
			else:
				print("Unknown option")