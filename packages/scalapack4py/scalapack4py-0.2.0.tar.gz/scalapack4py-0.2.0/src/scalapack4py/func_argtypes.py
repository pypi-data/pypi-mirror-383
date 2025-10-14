from ctypes import cdll, CDLL, RTLD_LOCAL, Structure
from ctypes import POINTER, byref, c_int, c_int64, c_char, c_bool, c_char_p, c_double, c_void_p, CFUNCTYPE, py_object, cast, byref, pointer
import numpy as np
from numpy.ctypeslib import ndpointer
from .blacsdesc import blacs_desc
from .array_types import nullable_ndpointer, ctypes2ndarray

class SCALAPACKargs:

    def __init__(self, blacs):

        self.blacs = blacs

        # The following dictionary defines tuples consisting of:
        # 1) The symbol corresponding to the SCALAPACK function
        # 2) The Ctype of the return variable
        # 3) The Ctypes of the arguments of the function
        # 4) The type casting directives needed for each argument
        self.scalapack_funcs = \
            {"pdgemr2d" : (self.blacs.pdgemr2d_, None,
                           [POINTER(c_int), POINTER(c_int), 
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc), 
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            POINTER(c_int)],
                           [c_int, c_int, None, c_int, c_int, None, None, c_int, c_int, None, c_int]),

             "pzgemr2d" : (self.blacs.pzgemr2d_, None,
                           [POINTER(c_int), POINTER(c_int), 
                            nullable_ndpointer(dtype=np.complex128, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc), 
                            nullable_ndpointer(dtype=np.complex128, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            POINTER(c_int)],
                           [c_int, c_int, None, c_int, c_int, None, None, c_int, c_int, None, c_int]),

             "pdgemm"   : (self.blacs.pdgemm_, None,
                           [POINTER(c_char), POINTER(c_char), POINTER(c_int), POINTER(c_int),
                            POINTER(c_int), POINTER(c_double),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            POINTER(c_double),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc)],
                           [self.cast2pchar, self.cast2pchar, c_int, c_int, c_int, c_double, None,
                            c_int, c_int, None, None, c_int, c_int, None, c_double, None,
                            c_int, c_int, None]),

             "pdsytrd"  : (self.blacs.pdsytrd_, None,
                           [POINTER(c_char), POINTER(c_int),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int)],
                           [self.cast2pchar, c_int, None, c_int, c_int, None, None, None, None,
                            None, c_int, c_int]),
                           

             "pdgebrd"  : (self.blacs.pdgebrd_, None,
                           [POINTER(c_int), POINTER(c_int),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int)],
                           [c_int, c_int, None, c_int, c_int, None, None, None, None,
                            None, None, c_int, c_int]),

             "pdgehrd"  : (self.blacs.pdgehrd_, None,
                           [POINTER(c_int), POINTER(c_int), POINTER(c_int),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int)],
                           [c_int, c_int, c_int, None, c_int, c_int, None, None, None, c_int,
                            c_int]),

             "pdsyevx"  : (self.blacs.pdsyevx_, None,
                           [POINTER(c_char), POINTER(c_char), POINTER(c_char), POINTER(c_int),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            POINTER(c_double), POINTER(c_double), POINTER(c_int), POINTER(c_int),
                            POINTER(c_double), POINTER(c_int), POINTER(c_int),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            POINTER(c_double),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            POINTER(c_int),
                            nullable_ndpointer(dtype=np.int32, ndim=1, flags='F_CONTIGUOUS'),
                            POINTER(c_int),
                            nullable_ndpointer(dtype=np.int32, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.int32, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            POINTER(c_int)],
                           [self.cast2pchar, self.cast2pchar, self.cast2pchar, c_int,
                            None, c_int, c_int, None, c_double, c_double, c_int, c_int, c_double,
                            c_int, c_int, None, c_double, None, c_int, c_int, None, None,
                            c_int, None, c_int, None, None, None, c_int]),

             "pdgesvd" :  (self.blacs.pdgesvd_, None,
                           [POINTER(c_char), POINTER(c_char), POINTER(c_int), POINTER(c_int),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            nullable_ndpointer(dtype=np.float64, ndim=2, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int), POINTER(blacs_desc),
                            nullable_ndpointer(dtype=np.float64, ndim=1, flags='F_CONTIGUOUS'),
                            POINTER(c_int), POINTER(c_int)],
                           [self.cast2pchar, self.cast2pchar, c_int, c_int, None, c_int, c_int,
                            None, None, None, c_int, c_int, None, None, c_int, c_int,
                            None, None, c_int, c_int]),
             }

        self.check_match_argtypes_argcasts()

    def cast2char(self, char):
        return c_char(char.encode("UTF-8"))
        
    def cast2pchar(self, char):
        return pointer(c_char(char.encode("UTF-8")))

    def check_match_argtypes_argcasts(self):
        for funcname in self.implemented_funcs:
            args = self.scalapack_funcs[funcname][2]
            cast = self.scalapack_funcs[funcname][3]
            
            err_msg = f"Implementation error: {funcname} has {len(args)} args and {len(cast)} casts."
            assert len(args) == len(cast), err_msg

    @property
    def implemented_funcs(self):
        return self.scalapack_funcs.keys()
        
    def get_symbol(self, funcname):
        return self.scalapack_funcs[funcname][0]

    def get_restypes(self, funcname):
        return self.scalapack_funcs[funcname][1]

    def get_argtypes(self, funcname):
        return self.scalapack_funcs[funcname][2]

    def get_argcasts(self, funcname):
        return self.scalapack_funcs[funcname][3]
