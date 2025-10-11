import os
from io import BytesIO
from math import ceil
from math import log
from struct import Struct
from pathlib import Path

try:
    if os.getenv('SIMPLEBLOOM_USEPY'):
        from ._pybloom import BloomFilterBase
        PURE_PYTHON = True
    else:
        from ._cbloom import BloomFilterBase
        PURE_PYTHON = False
except ImportError:
    from ._pybloom import BloomFilterBase
    PURE_PYTHON = True


MAGIC = b'SIMPBLOO'
HEADER = Struct(f'>{len(MAGIC)}sQQd')


class BloomFilter(BloomFilterBase):
    """
    A simple but fast bloom filter.
    Elements must be strings.

    Add an element and check whether it is contained::

        bf = BloomFilter(1000)
        bf += 'hellobloom'
        assert 'hellobloom' in bf

    ``false_positive_prob`` defaults to ``1 / num_elements``.

    The number of bits in the filter is
    ``num_bits = n * log(false_positive_prob) / log(1 / 2**log(2))``,
    rounded up to the next multiple of 8.

    The number of hash functions used is
    ``num_hashes = round(num_bits / num_elements * log(2))`` .

    Parameters:
        num_elements: expected max number of elements in the filter
        false_positive_prob: desired approximate false positive probability
    """
    def __init__(
            self,
            num_elements,
            false_positive_prob=None,
            _buffer=None,
            __header=HEADER,
    ):
        if num_elements < 2:
            raise ValueError('num_element < 2')
        if false_positive_prob is None:
            false_positive_prob = 1.0 / num_elements
        if not 0 < false_positive_prob < 1:
            raise ValueError('false_positive_prob must be in (0, 1)')
        false_positive_prob = float(false_positive_prob)

        self.num_elements = num_elements
        self.false_positive_prob = false_positive_prob

        ln2 = 0.6931471805599453
        num_bits = num_elements * log(false_positive_prob) / -0.4804530139182015
        num_bits = int(ceil(num_bits / 8) * 8)
        num_hashes = int(round(num_bits / num_elements * ln2))
        num_bytes = (num_bits >> 3) + (num_bits & 7 > 0)

        if _buffer is None:
            self._buffer = bytearray(__header.size + num_bytes)
            # writer header
            __header.pack_into(
                self._buffer, 0,
                MAGIC,
                __header.size + num_bytes,
                num_elements,
                false_positive_prob,
            )
        elif len(_buffer) != HEADER.size + num_bytes:
            raise ValueError(f'len(data) = {len(_buffer)} != len(filter) = {num_bytes}')
        else:
            self._buffer = _buffer

        super().__init__(num_bits, num_hashes, memoryview(self._buffer)[__header.size:])

    def __len__(self):
        return len(self._buffer) - HEADER.size

    @classmethod
    def __load(cls, fp, __header=HEADER):
        # read and check header
        header_data = fp.read(__header.size)
        magic, num_bytes, num_elements, false_positive_prob = \
            __header.unpack_from(header_data)
        if magic != MAGIC:
            raise ValueError('not a simplebloom file')

        # create buffer and copy header into it
        buffer = bytearray(num_bytes)
        buffer[:__header.size] = header_data

        # fill rest of buffer from file
        try:
            fp.readinto(memoryview(buffer)[__header.size:])
        except AttributeError:
            buffer[__header.size:] = fp.read()

        # make filter
        return cls(
            num_elements=num_elements,
            false_positive_prob=false_positive_prob,
            _buffer=buffer
        )

    # noinspection PyIncorrectDocstring
    @classmethod
    def load(cls, fp, __header=HEADER):
        """
        Load a filter from a path or file-like::

            bf = BloomFilter.load('bloom.filter')

            with open('bloom.filter', 'rb') as fp:
                bf = BloomFilter.load(fp)

        Parameters:
            fp: path or file-like
        """
        if isinstance(fp, (str, Path)):
            with open(fp, 'rb') as fp:
                # noinspection PyTypeChecker
                return cls.__load(fp)
        else:
            return cls.__load(fp)

    @classmethod
    def loads(cls, data):
        """
        Load a filter from a buffer::

            data = bf.dumps()
            bf = BloomFilter.loads(data)

        Parameters:
            data: filter data
        """
        return cls.__load(BytesIO(data))

    def dump(self, fp):
        """
        Dump filter to a path or file-like::

            bf.dump('bloom.filter')

            with open('bloom.filter', 'wb') as fp:
                bf.dump(fp)

        Parameters:
            fp: path or file-like
        """
        if isinstance(fp, (str, Path)):
            with open(fp, 'wb') as fp:
                fp.write(self._buffer)
        else:
            fp.write(self._buffer)

    def dumps(self):
        """
        Returns filter data as buffer::

            data = bf.dumps()
            bf = BloomFilter.loads(data)
        """
        return bytearray(self._buffer)
