# educational use only
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sys import argv, exit
import lec.key

##################################################################################

if len(argv)!=4:
	exit("Usage: "+argv[0]+" <ScopeID> <flags> <mask>")

print (lec.key.encode(int(argv[1], 16), int(argv[2], 16), int(argv[3], 16)))