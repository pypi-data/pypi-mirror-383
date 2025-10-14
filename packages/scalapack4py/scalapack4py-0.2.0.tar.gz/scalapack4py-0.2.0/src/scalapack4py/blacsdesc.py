from ctypes import cdll, CDLL, RTLD_LOCAL, Structure
from ctypes import POINTER, byref, c_int, c_int64, c_char, c_bool, c_char_p, c_double, c_void_p, CFUNCTYPE, py_object, cast, byref
import numpy as np
from numpy.ctypeslib import ndpointer

DLEN_ = 9
class blacs_desc(Structure): # https://www.netlib.org/scalapack/slug/node68.html
  _fields_ = [("dtype", c_int),
              ("ctxt", c_int),
              ("m", c_int),
              ("n", c_int),
              ("mb", c_int),
              ("nb", c_int),
              ("rsrc", c_int),
              ("csrc", c_int),
              ("lld", c_int)]
  def __init__(self, lib, blacs_ctx=-1, m=0, n=0, mb=1, nb=1, rsrc=0, csrc=0, lld=None, buf=None):
    super().__init__()
    self.lib = lib
    
    if buf is not None:
      if not hasattr(buf, '__get_index__'):
        buf = np.ctypeslib.as_array(buf, shape=(DLEN_,))
      self.dtype, self.ctxt, self.m, self.n, self.mb, self.nb, self.rsrc, self.csrc, self.lld = (*buf,)
      return # wrapped copy

    if blacs_ctx == -1: # stub for non-participating process
      self.dtype=1
      self.ctxt=blacs_ctx
      self.m = 0
      self.n = 0
      self.mb = 0
      self.nb = 0
      self.rsrc = 0
      self.csrc = 0
      self.lld = 0
      return # default, zero-intitalized

    assert m > 0, m
    assert n > 0, n
    if lld is None: # calc default lld
      nprow, _, myrow, _ = self.lib.blacs_gridinfo(blacs_ctx)
      lld = self.lib.numroc(m, mb, myrow, rsrc, nprow)
      lld = max(1, lld) # ldd is not less than 1

    self.lib.descinit(self, m, n, mb, nb, rsrc, csrc, blacs_ctx, lld)
    
  @property
  def myrow(self):
    _, _, myrow, _ = self.lib.blacs_gridinfo(self.ctxt)
    return myrow

  @property
  def mycol(self):
    _, _, _, mycol = self.lib.blacs_gridinfo(self.ctxt)
    return mycol

  @property
  def nprow(self):
    nprow, _, _, _ = self.lib.blacs_gridinfo(self.ctxt)
    return nprow

  @property
  def npcol(self):
    _, npcol, _, _ = self.lib.blacs_gridinfo(self.ctxt)
    return npcol

  @property
  def is_distributed(self):
    nprow, npcol, _, _ = self.lib.blacs_gridinfo(self.ctxt)
    return (nprow * npcol) > 1

  @property
  def locrow(self):
    nprow, _, myrow, _ = self.lib.blacs_gridinfo(self.ctxt)
    return self.lib.numroc(self.m, self.mb, myrow, self.rsrc, nprow)

  @property
  def loccol(self):
    _, npcol, _, mycol = self.lib.blacs_gridinfo(self.ctxt)
    return self.lib.numroc(self.n, self.nb, mycol, self.csrc, npcol)

  def alloc_zeros(self, dtype):
    res = self.alloc(dtype)
    res[:,:] = 0
    return res
  
  def alloc(self, dtype):
    return np.ndarray(shape=(self.locrow, self.loccol), order='F', dtype=dtype)

  def __repr__(self):
    return f"{self.dtype} {self.ctxt} {self.m} {self.n} {self.mb} {self.nb} {self.rsrc} {self.csrc} {self.lld}"
