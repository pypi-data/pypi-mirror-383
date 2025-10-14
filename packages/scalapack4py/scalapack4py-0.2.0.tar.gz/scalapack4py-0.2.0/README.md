# Dynamic ScaLAPACK wrapper for Python

Python wrapper for dynamically loaded ScaLAPACK and BLACS libraries

```
from scalapack4py import ScaLAPACK4py, parprint, ordprint
from ctypes import cast, py_object, CDLL, RTLD_GLOBAL

scalapack_lib = CDLL('libscalapack-openmpi.so.2.0', mode=RTLD_GLOBAL)
sl = ScaLAPACK4py(scalapack_lib)


descr = sl.wrap_blacs_desc(descr)
locshape = (descr.locrow, descr.loccol)
data = np.ctypeslib.as_array(data, shape=locshape)
sl.scatter(data_src, descr, data)

```

Or

```
# run as:  mpiexec -n 2 python3 -u test_scatter_complex.py
import numpy as np, os
from mpi4py import MPI
from scalapack4py import ScaLAPACK4py
from ctypes import CDLL, RTLD_GLOBAL, POINTER, c_int, c_double

sl = ScaLAPACK4py(CDLL('libscalapack-openmpi.so.2.0', mode=RTLD_GLOBAL))

n = 5
dtype=np.complex128
a = np.arange(n*n, dtype=dtype).reshape((n,n), order='F') * (MPI.COMM_WORLD.rank+1) if MPI.COMM_WORLD.rank==0 else None

print (a)

MP, NP = 2,1

ctx = sl.make_blacs_context(sl.get_default_system_context(), MP, NP)
descr = sl.make_blacs_desc(ctx, n, n)
print("descr", descr, descr.locrow, descr.loccol)

b = np.zeros((descr.locrow, descr.loccol), dtype=dtype)

sl.scatter_numpy(a, POINTER(c_int)(descr), b.ctypes.data_as(POINTER(c_double)), b.dtype)
print (b)


c = sl.gather_numpy(POINTER(c_int)(descr), b, (n, n))
print (c)

```

A streamlined interface to scalapack4py is provided by NPScal, which
replicates many of the arithmatic operators implemented for ndarrays

```
from numpy.random import RandomState
from scalapack4py.scalapack4py import ScaLAPACK4py
from scalapack4py.npscal import NPScal
from scalapack4py.npscal import CTXT_Register, DESCR_Register, BLACSDESCRManager, BLACSContextManager
from scalapack4py.npscal.index_utils.npscal_select import diag
from scalapack4py.npscal.utils import find_squarest_grid
from mpi4py import MPI

from ctypes import RTLD_GLOBAL, POINTER, c_int, c_double, CDLL
import numpy as np
import os

sl = ScaLAPACK4py(CDLL(scalapack_libpath, mode=RTLD_GLOBAL))

n = 16
dtype=np.float64

b = np.arange(n*n, dtype=dtype).reshape((n,n))
dist_b = NPScal(gl_array=b, ctxt_tag="main", descr_tag="default", lib=sl)

b_matmul = b @ b
dist_b_matmul = dist_b @ dist_b
```