# cython: language_level=3
# cython: embedsignature=False
# cython: boundscheck=False

# Cython imports
from libc.stdint cimport *
from cpython cimport Py_buffer
from cpython cimport PyObject_GetBuffer
from cpython cimport PyBuffer_Release
from cpython cimport PyBUF_SIMPLE
from cpython cimport PyObject_CopyData

# Python imports
from hashlib import blake2s

import cython


cdef extern from "_bswap.h":
    uint64_t ntoh64(const uint64_t)


cdef inline void hash_key(object key, uint64_t* h1, uint64_t* h2):
    # generate 16+ bytes of hash for key
    hashes = blake2s(key.encode('utf-8')).digest()
    # retrieve 2 hash values
    cdef Py_buffer view
    PyObject_GetBuffer(hashes, &view, PyBUF_SIMPLE)
    h1[0] = ntoh64((<uint64_t*>view.buf)[0])
    h2[0] = ntoh64((<uint64_t*>view.buf)[1])
    PyBuffer_Release(&view)


cdef class BloomFilterBase:
    cdef uint64_t num_bits
    cdef int num_hashes
    cdef uint8_t* data
    cdef Py_buffer view

    def __init__(self, num_bits, num_hashes, data):
        self.num_bits = num_bits
        self.num_hashes = num_hashes
        PyObject_GetBuffer(data, &self.view, PyBUF_SIMPLE)
        self.data = <uint8_t*> self.view.buf

    def __dealloc__(self):
        PyBuffer_Release(&self.view)

    @cython.cdivision(True)
    def __iadd__(self, key):
        f = self.data
        cdef uint64_t b=self.num_bits, h1=0, h2=0, index, x
        cdef uint8_t y
        cdef int k
        hash_key(key, &h1, &h2)
        for k in range(self.num_hashes):
            index = (h1 + k * h2) % b
            x = index >> 3
            y = 1 << (index & 7)
            f[x] |= y
        return self

    @cython.cdivision(True)
    def __contains__(self, key):
        f = self.data
        cdef uint64_t b=self.num_bits, h1=0, h2=0, index, x
        cdef uint8_t y
        cdef int k
        hash_key(key, &h1, &h2)
        for k in range(self.num_hashes):
            index = (h1 + k * h2) % b
            x = index >> 3
            y = 1 << (index & 7)
            if f[x] & y <= 0:
                return False
        return True
