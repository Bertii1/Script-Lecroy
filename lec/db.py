# educational use only
from crypto import decrypt
from struct import unpack
from cStringIO import StringIO
import os

def fsize(hf):
	pos = hf.tell()
	hf.seek(0, os.SEEK_END)	
	size = hf.tell()
	hf.seek(pos)
	return size


def DecryptFile(hfi, hfo):
	size = fsize(hfi)
	for i in xrange(0, size, 8):
		hfo.write(decrypt(hfi.read(8)))

############################################################################

TypeShort = 2
TypeInt = 3
TypeStr = 8


class LicError(Exception):
	pass


class LicReader(object):
	def __init__(self, fname):
		hfi = open(fname, "rb")
		hfo = StringIO()
		DecryptFile(hfi, hfo)
		hfi.close()
		plain_cfg = hfo.getvalue()
		hfo.close()

		self.hf = StringIO(plain_cfg)
		self.size = fsize(self.hf)
		self.nomore = False


	def get(self):
		if self.nomore:
			return None, None
		if self.hf.tell()>=self.size:
			raise LicError("Unexpected EOF")
		t = unpack("<H", self.hf.read(2))[0]
		if t==0x00: # end
			self.nomore = True
			self.hf.close()
			return None, None
		elif t==2:
			v = unpack("<H", self.hf.read(2))[0]
			return TypeShort, v
		elif t==0x03:	# uint
			v = unpack("<L", self.hf.read(4))[0]
			return TypeInt, v
		elif t==0x08: # UTF-16LE string
			l = unpack("<L", self.hf.read(4))[0]
			v = self.hf.read(l).decode('UTF-16', 'ignore').encode('ASCII', 'ignore')
			return TypeStr, v
		else:
			raise LicError("Unsupported type %02X" % (t))

	def GetShort(self):
		t, v = self.get()
		if not t:
			return None
		if t!=TypeShort:
			raise LicError("Got unexpected type %d instead of Short" % t)
		return v

	def GetInt(self):
		t, v = self.get()
		if not t:
			return None
		if t!=TypeInt:
			raise LicError("Got unexpected type %d instead of Int" % t)
		return v

	def GetStr(self):
		t, v = self.get()
		if not t:
			return None
		if t!=TypeStr:
			raise LicError("Got unexpected type %d instead of Str" % t)
		return v


class LicCategory(object):
	def __init__(self, reader):
		self.idx = reader.GetInt()
		self.guid = reader.GetStr()
		self.name = reader.GetStr()
		self.description = reader.GetStr()
		self.flags = reader.GetShort()

	def __str__(self):
		return "Category: %6d | %04X | %s | %s | %s" % (self.idx, self.flags, self.guid, self.name, self.description)


class LicComponent(object):
	def __init__(self, reader):
		self.idx = reader.GetInt()
		self.name = reader.GetStr()
		self.description = reader.GetStr()
		self.format = reader.GetStr()
		self.flags = reader.GetShort()
		self.fqn = reader.GetStr()
		self.code1 = reader.GetStr()
		self.code2 = reader.GetStr()
		self.category_idx = reader.GetInt()
		self.flags2 = reader.GetShort()
		self.s1 = reader.GetStr()
		self.s2 = reader.GetStr()


	def __str__(self):
		return "Component: %6d | %s | %s | %s | %04X | %s | %s | %s | cat_%d | %04X | %s | %s" % (self.idx, self.name, self.description, self.format, self.flags, self.fqn, self.code1, self.code2, self.category_idx, self.flags2, self.s1, self.s2)


class LicComponentV2(object):
	def __init__(self, reader):
		self.idx = reader.GetInt()
		self.name = reader.GetStr()
		self.description = reader.GetStr()
		self.format = reader.GetStr()
		self.flags = reader.GetShort()
		self.fqn = reader.GetStr()
		self.code1 = reader.GetStr()
		self.code2 = reader.GetStr()
		self.category_idx = reader.GetInt()
		self.flags2 = reader.GetShort()
		self.s1 = reader.GetStr()
		self.s2 = reader.GetStr()
		self.guid = reader.GetStr()


	def __str__(self):
		return "Component: %6d | %s | %s | %s | %04X | %s | %s | %s | cat_%d | %04X | %s | %s | %s" % (self.idx, self.name, self.description, self.format, self.flags, self.fqn, self.code1, self.code2, self.category_idx, self.flags2, self.s1, self.s2, self.guid)


class LicProcToCat(object):
	def __init__(self, reader):
		self.u0 = reader.GetInt()
		self.idx = reader.GetInt()
		self.u2 = reader.GetInt()
		self.u3 = reader.GetInt()

	def __str__(self):
		return "ProcToCat: %6d | %08X | %d | %d" % (self.idx, self.u0, self.u2, self.u3)


class LicOption(object):
	def __init__(self, reader):
		self.db_key = reader.GetInt()
		self.name = reader.GetStr()
		self.page = reader.GetInt()
		self.bit = reader.GetInt()
		self.idx = (1<<self.bit) | ((self.page & 3)<<32) | ((self.page & 4)<<36)
		self.flags1 = reader.GetShort()
		self.flags2 = reader.GetShort()
		self.description = reader.GetStr()
		self.u0 = reader.GetInt()
		self.flags3 = reader.GetShort()
		self.flags4 = reader.GetShort()
		self.flags5 = reader.GetShort()
		self.flags6 = reader.GetShort()


	def __str__(self):
		return "Option: %02X-%08X | %6d | %s | %s | %d | %04X %04X %04X %04X %04X %04X " % (self.idx>>32, self.idx & 0xFFFFFFFF, self.db_key, self.name, self.description, self.u0, self.flags1, self.flags2, self.flags3, self.flags4, self.flags5, self.flags6)


class LicEnabCompWithOpt(object):
	def __init__(self, reader):
		self.idx = reader.GetInt()
		self.u0 = reader.GetInt()
		self.u1 = reader.GetInt()
		self.flags = reader.GetShort()

	def __str__(self):
		return "EnabCompWithOpt: %6d | %d | %d | %04X" % (self.idx, self.u0, self.u1, self.flags)


class LicA(object):
	def __init__(self, reader):
		self.idx = reader.GetInt()
		self.u0 = reader.GetInt()
		self.u1 = reader.GetInt()
		self.flags = reader.GetShort()
		self.u2 = reader.GetInt()

	def __str__(self):
		return "LicA: %6d | %d | %d | %04X | %d" % (self.idx, self.u0, self.u1, self.flags, self.u2)


class LicB(object):
	def __init__(self, reader):
		self.idx = reader.GetInt()
		self.u0 = reader.GetInt()
		self.u1 = reader.GetInt()

	def __str__(self):
		return "LicB: %6d | %d | %d" % (self.idx, self.u0, self.u1)


class LicFlag(object):
	def __init__(self, reader):
		self.idx = reader.GetInt()
		self.flags = reader.GetShort()

	def __str__(self):
		return "Flag: %6d | %04X" % (self.idx, self.flags)


class LicC(object):
	def __init__(self, reader):
		self.idx = reader.GetInt()
		self.u0 = reader.GetInt()
		self.u1 = reader.GetInt()

	def __str__(self):
		return "LicC: %6d | %d | %d" % (self.idx, self.u0, self.u1)

#############################################################################

def LoadGroup(reader, cls):
	num = reader.GetInt()
	group = dict()
	for i in xrange(num):
		obj = cls(reader)
		group[obj.idx] = obj
	return group

#############################################################################

def PrintGroup(grp):
	for idx in sorted(grp.keys()):
		print (grp[idx])

#############################################################################

class LicDB(object):
	def __init__(self, reader):
		# CategoryMap
		self.categories = LoadGroup(reader, LicCategory)
		# ComponentMap
		self.components = LoadGroup(reader, LicComponent)
		# ProcToCatMap
		self.proc2cats = LoadGroup(reader, LicProcToCat)
		# OptionsMap
		self.options = LoadGroup(reader, LicOption)
		# EnabCompWithOpt
		self.ecwo0 = LoadGroup(reader, LicEnabCompWithOpt)
		# EnabCompWithOpt
		self.ecwo1 = LoadGroup(reader, LicEnabCompWithOpt)
		# ???
		self.a = LoadGroup(reader, LicA)
		# ???
		self.b = LoadGroup(reader, LicB)
		# ???
		self.flags = LoadGroup(reader, LicFlag)
		# ???
		self.c = LoadGroup(reader, LicC)

#############################################################################

class LicDBv2(object):
	def __init__(self, reader):
		# CategoryMap
		self.categories = LoadGroup(reader, LicCategory)
		# ComponentMap
		self.components = LoadGroup(reader, LicComponentV2)
		# ProcToCatMap
		self.proc2cats = LoadGroup(reader, LicProcToCat)
		# OptionsMap
		self.options = LoadGroup(reader, LicOption)
		# EnabCompWithOpt
		self.ecwo0 = LoadGroup(reader, LicEnabCompWithOpt)
		# EnabCompWithOpt
		self.ecwo1 = LoadGroup(reader, LicEnabCompWithOpt)
		# ???
		self.a = LoadGroup(reader, LicA)
		# ???
		self.b = LoadGroup(reader, LicB)
		# ???
		self.flags = LoadGroup(reader, LicFlag)
		# ???
		self.c = LoadGroup(reader, LicC)

#############################################################################

def fromfile(fname):
	try:
		return LicDB(LicReader(fname))
	except LicError:
		return LicDBv2(LicReader(fname))

#############################################################################

__all__ = ["LicReader", "LicDB", "fromfile"]

if __name__=="__main__":
	from sys import argv, exit
	
	if len(argv)!=2:
		exit("Usage: "+argv[0]+" <options.cfg>")

	# decrypt into str buf
	db = fromfile(argv[1])

	PrintGroup(db.options)