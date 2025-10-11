from struct import Struct
from hashlib import blake2s


__all__ = ('BloomFilterBase',)


class BloomFilterBase:
    def __init__(self, num_bits, num_hashes, data):
        self.num_bits = num_bits
        self.num_hashes = num_hashes
        self._data = data

    def __iadd__(self, key, __struct=Struct('>QQ')):
        f = self._data
        b = self.num_bits
        h1, h2 = __struct.unpack_from(blake2s(key.encode('utf-8')).digest())
        for k in range(self.num_hashes):
            # simulate uint64 value range of native code:
            # logical AND with max uint64 == 2**64-1
            index = (h1 + k * h2 & 18446744073709551615) % b
            x = index >> 3
            y = 1 << (index & 7)
            f[x] |= y
        return self

    def __contains__(self, key, __struct=Struct('>QQ')):
        f = self._data
        b = self.num_bits
        h1, h2 = __struct.unpack_from(blake2s(key.encode('utf-8')).digest())
        for k in range(self.num_hashes):
            # simulate uint64 value range of native code:
            # logical AND with max uint64 == 2**64-1
            index = (h1 + k * h2 & 18446744073709551615) % b
            x = index >> 3
            y = 1 << (index & 7)
            if not f[x] & y:
                return False
        return True
