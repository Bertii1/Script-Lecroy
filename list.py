# educational use only
from sys import argv, exit
import lec.db

if len(argv)!=2:
	exit("Usage: "+argv[0]+" <options.cfg>")

db = lec.db.fromfile(argv[1])

for idx in sorted(db.options.keys()):
		print ("%02X-%08X %-20s %s" % (idx>>32, idx & 0x0FFFFFFFF, db.options[idx].name, db.options[idx].description))