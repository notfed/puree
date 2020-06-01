import pureelib.plumbing.common as plumbing_common

class PureeBoxOne:

    @classmethod
    def get_ciphertext_size(cls):
        return 16 + cls.get_plaintext_size()
    @classmethod
    def get_plaintext_size(cls):
        return 8+1+1+2
    @classmethod
    def get_inner_size(self):
        return 8+1+1+2

    # property: byte[8] subspec 
    # property: byte[1] used_slots
    # property: byte[1] total_slots
    # property: byte[2] len_of_box_2
    @classmethod
    def unpack(cls,packed):
        if len(packed) != __class__.get_plaintext_size():
            raise RuntimeError("The PUREE header of this disk is corrupt.")
        r = PureeBoxOne()
        r.subspec = packed[0:8]
        r.used_slots = plumbing_common.u8_from_be(packed[8:9])
        r.total_slots = plumbing_common.u8_from_be(packed[9:10])
        r.len_of_box_2 = plumbing_common.u16_from_be(packed[10:12])
        return r

    def pack(self):
        return self.subspec \
              +plumbing_common.u8_to_be(self.used_slots) \
              +plumbing_common.u8_to_be(self.total_slots) \
              +plumbing_common.u16_to_be(self.len_of_box_2)

class DiskAes256CbcEssivSha256BoxTwo:

    @classmethod
    def subspec_name(clas):
        return 'aes256-cbc-essiv-sha256'
    @classmethod
    def subspec_id(cls):
        return bytearray.fromhex('9abf8b191e4a84a4')
    @classmethod
    def get_inner_size(self):
        return 32+8+8

    # property: byte[32] key 
    # property: byte[8]  logical_start_sector
    # property: byte[8]  num_sectors
    @classmethod
    def unpack(cls,packed):
        if(len(packed) != cls.get_inner_size()):
            raise RuntimeError("The PUREE header of this disk is corrupt.")
        r = DiskAes256CbcEssivSha256BoxTwo()
        r.key                  = packed[0:32]
        r.logical_start_sector = plumbing_common.u64_from_be(packed[32:40])
        r.num_sectors          = plumbing_common.u64_from_be(packed[40:48])
        return r
    def pack(self):
        return self.key \
             + plumbing_common.u64_to_be(self.logical_start_sector) \
             + plumbing_common.u64_to_be(self.num_sectors)

class DiskAes256XtsPlain64:
    
    @classmethod
    def subspec_name(clas):
        return 'aes256-xts-plain64'
    @classmethod
    def subspec_id(cls):
        return bytearray.fromhex('cf43556cf0b3ebb7')
    @classmethod
    def get_inner_size(self):
        return 64+8+8

    # property: byte[64] key 
    # property: byte[8]  logical_start_sector
    # property: byte[8]  num_sectors
    @classmethod
    def unpack(cls,packed):
        if(len(packed) != cls.get_inner_size()):
            raise RuntimeError("The PUREE header of this disk is corrupt.")
        r = DiskAes256XtsPlain64()
        r.key                  = packed[0:64]
        r.logical_start_sector = plumbing_common.u64_from_be(packed[64:72])
        r.num_sectors          = plumbing_common.u64_from_be(packed[72:80])
        return r
    def pack(self):
        return self.key \
             + plumbing_common.u64_to_be(self.logical_start_sector) \
             + plumbing_common.u64_to_be(self.num_sectors)
        
class DiskAes128CbcEssivSha256BoxTwo:

    @classmethod
    def subspec_name(clas):
        return 'aes128-cbc-essiv-sha256'
    @classmethod
    def subspec_id(cls):
        return bytearray.fromhex('f83789a7bf8f0e43')
    @classmethod
    def get_inner_size(self):
        return 16+8+8

    # property: byte[16] key 
    # property: byte[8]  logical_start_sector
    # property: byte[8]  num_sectors
    @classmethod
    def unpack(cls,packed):
        if(len(packed) != cls.get_inner_size()):
            raise RuntimeError("The PUREE header of this disk is corrupt.")
        r = DiskAes128CbcEssivSha256BoxTwo()
        r.key                  = packed[0:16]
        r.logical_start_sector = plumbing_common.u64_from_be(packed[16:24])
        r.num_sectors          = plumbing_common.u64_from_be(packed[24:32])
        return r
    def pack(self):
        return self.key \
             + plumbing_common.u64_to_be(self.logical_start_sector) \
             + plumbing_common.u64_to_be(self.num_sectors)

class DiskAes128XtsPlain64:

    @classmethod
    def subspec_name(clas):
        return 'aes128-xts-plain64'
    @classmethod
    def subspec_id(cls):
        return bytearray.fromhex('a9d4d04dfaf36314')
    @classmethod
    def get_inner_size(self):
        return 32+8+8

    # property: byte[32] key 
    # property: byte[8]  logical_start_sector
    # property: byte[8]  num_sectors
    @classmethod
    def unpack(cls,packed):
        if(len(packed) != cls.get_inner_size()):
            raise RuntimeError("The PUREE header of this disk is corrupt.")
        r = DiskAes128XtsPlain64()
        r.key                  = packed[0:32]
        r.logical_start_sector = plumbing_common.u64_from_be(packed[32:40])
        r.num_sectors          = plumbing_common.u64_from_be(packed[40:48])
        return r
    def pack(self):
        return self.key \
             + plumbing_common.u64_to_be(self.logical_start_sector) \
             + plumbing_common.u64_to_be(self.num_sectors)

# List all valid subspec names
def all_subspec_names():
    return [DiskAes256XtsPlain64.subspec_name(),
            DiskAes256CbcEssivSha256BoxTwo.subspec_name(),
            DiskAes128XtsPlain64.subspec_name(),
            DiskAes128CbcEssivSha256BoxTwo.subspec_name()]
    
# List all valid subspec ids
def all_subspec_ids():
    return [DiskAes256XtsPlain64.subspec_id(),
            DiskAes256CbcEssivSha256BoxTwo.subspec_id(),
            DiskAes128XtsPlain64.subspec_id(),
            DiskAes128CbcEssivSha256BoxTwo.subspec_id()]
    
# Find the subspec_id given the subspec_name
def subspec_name_to_id(name):
    if name == DiskAes256XtsPlain64.subspec_name():
        return DiskAes256XtsPlain64.subspec_id()
    elif name == DiskAes256CbcEssivSha256BoxTwo.subspec_name():
        return DiskAes256CbcEssivSha256BoxTwo.subspec_id()
    elif name == DiskAes128XtsPlain64.subspec_name():
        return DiskAes128XtsPlain64.subspec_id()
    elif name == DiskAes128CbcEssivSha256BoxTwo.subspec_name():
        return DiskAes128CbcEssivSha256BoxTwo.subspec_id()
    return None

# Find the subspec_name via subspec_id
def subspec_id_to_name(idd):
    if idd == DiskAes256XtsPlain64.subspec_id():
        return DiskAes256XtsPlain64.subspec_name()
    elif idd == DiskAes256CbcEssivSha256BoxTwo.subspec_id():
        return DiskAes256CbcEssivSha256BoxTwo.subspec_name()
    elif idd == DiskAes128XtsPlain64.subspec_id():
        return DiskAes128XtsPlain64.subspec_name()
    elif idd == DiskAes128CbcEssivSha256BoxTwo.subspec_id():
        return DiskAes128CbcEssivSha256BoxTwo.subspec_name()
    return None