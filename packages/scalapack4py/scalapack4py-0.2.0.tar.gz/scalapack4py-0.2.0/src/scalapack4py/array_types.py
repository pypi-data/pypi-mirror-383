from ctypes import cdll, CDLL, RTLD_LOCAL, Structure
from ctypes import POINTER, byref, c_int, c_int64, c_char, c_bool, c_char_p, c_double, c_void_p, CFUNCTYPE, py_object, cast, byref
import numpy as np
from numpy.ctypeslib import ndpointer

def nullable_ndpointer(*args, **kwargs):
  # solution from here: https://stackoverflow.com/a/37664693/3213940
  # TODO look for this isssue: https://github.com/numpy/numpy/issues/6239
  base = ndpointer(*args, **kwargs)
  def from_param(cls, obj):
    if obj is None:
      return obj
    return base.from_param(obj)
  return type(base.__name__, (base,), {'from_param': classmethod(from_param)})

def ctypes2ndarray(data, shape):
  '''
     Convert ctypes POINTER(c_double) to ndarray of complex128 or float64 
     depending on shape dimensionality, that can be 2 (float64) or 3 (complex128)
  '''
  res = np.ctypeslib.as_array(data, shape=shape)
  if len(shape) == 3:
    res = res.view(np.complex128).reshape((shape[0], shape[1]))

  assert len(res.shape) == 2
  return res
