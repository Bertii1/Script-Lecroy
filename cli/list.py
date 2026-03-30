# educational use only
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sys import argv, exit
import lec.db
import json

if len(argv)!=2:
	exit("Usage: "+argv[0]+" <options.cfg>")

db = lec.db.fromfile(argv[1])

options_list = []
for idx in sorted(db.options.keys()):
    code = "%02X-%08X" % (idx>>32, idx & 0xFFFFFFFF)
    name = db.options[idx].name
    desc = db.options[idx].description
    options_list.append({"code": code, "key": name, "description": desc})

with open('opzioni.json', 'w') as f:
    json.dump(options_list, f, indent=2)

for idx in sorted(db.options.keys()):
		print ("%02X-%08X %-20s %s" % (idx>>32, idx & 0x0FFFFFFFF, db.options[idx].name, db.options[idx].description))