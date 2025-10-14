from scalapack4py import ScaLAPACK4py
from scalapack4py.array_types import nullable_ndpointer, ctypes2ndarray
from ctypes import CDLL, POINTER, c_int, c_double, RTLD_GLOBAL
import ctypes
from mpi4py import MPI
from .comms import mpi_bcast_float, root_print
from .blacs_ctxt_management import CTXT_Register, DESCR_Register, BLACSContextManager, BLACSDESCRManager
from .utils import find_squarest_grid
from typing import overload
import numpy as np

class NPScal():

    def __init__(self, gl_array=None, loc_array=None, lib=None, ctxt_tag=None, descr_tag=None,
                 gl_m=None, gl_n=None, ctxt_mp=-1, ctxt_np=-1, dmb=1, dnb=1, drsrc=0, dcsrc=0,
                 dlld=None):

        """Wrapper for distributed numpy arrays with BLACS contexts and descriptors tracked by registry

        Provides a pythonic wrapper for numpy arrays distributed as BLACS arrays. Replicates common
        syntax features of numpy (i.e., slice index setting/getting with global indices and common
        matrix operations with operator symbols) and interfaces with parallel linear algebra routines
        provided by scalapack4py. 

        BLACS contexts and array descriptors are tracked by registry, maintaining a global record of
        each in CTXT_Register and DESCR_Register, respectively. Each context is assigned a tag, which
        may be transferred to other NPScal arrays with identical distributions.

        An NPScal array may be created in three ways:
        a) A global numpy array, which is scattered to each MPI task
        b) A pre-distributed set of numpy arrays that match a given BLACS context and descriptor.
        c) A C-type pointer to a c_double distributed type

        Parameters
        ----------
        gl_array : ndarray
            Global numpy array to be scattered to each MPI process
        loc_array : ctypes.POINTER or ndarray
            A distributed array input as either a numpy array or a
            ctypes C double pointer
        lib : CDLL or str
            Location of ScaLAPACK library or an already loaded CDLL
        ctxt_tag : str
            Human-readable label for the BLACS context assigned to
            NPScal instance
        descr_tag : str
            Human-readable label for the BLACS descriptor assigned to
            NPScal instance

        Examples
        --------
        FIXME: Add docs.

        """

        from scalapack4py import ScaLAPACK4py
        from ctypes import RTLD_GLOBAL, POINTER, c_int, c_double
        from mpi4py import MPI
        import os

        # Specify library containing symbols for ScaLAPACK and MPI
        if isinstance(lib, str):
            self.sl = ScaLAPACK4py(CDLL(lib, mode=RTLD_GLOBAL))
        else:
            self.sl = lib

        # Create an internal copy for the number of requested MPI tasks
        self.comm = MPI.COMM_WORLD
        self.ntasks = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

        # TODO: Print warning if both gl_array and loc_array are None that loc_array
        # will be set to zeros in a globally distributed fashion
        init_zero, init_gl, init_loc = False, False, False
        self.dim_2d = False

        # Assumed zero array is requested with the dimensions of the
        # specified descriptor either inferred from the descriptor
        # tag or the input parameters
        if ((gl_array is not None) and (loc_array is not None)):
            raise Exception("Only specify either a global or a local array.")

        if ((gl_array is None) and (loc_array is None)):
            init_zero = True
        elif (gl_array is not None):
            init_gl = True
        elif (loc_array is not None):
            init_loc = True

        if (init_zero or init_loc):
            if DESCR_Register.check_register(descr_tag):
                gl_m = DESCR_Register.get_register(descr_tag).m
                gl_n = DESCR_Register.get_register(descr_tag).n
            elif ((gl_m is None) or (gl_n is None)):
                raise Exception("Global dimensions (gl_m and gl_n) needed for local array initialisation")

            if (gl_m == 1 or gl_n == 1):
                self.dim_2d = False
            else:
                self.dim_2d = True
        else:
            if len(np.shape(gl_array)) == 1:
                gl_array = gl_array.reshape(-1, 1)
                
            gl_m = np.shape(gl_array)[0]
            gl_n = np.shape(gl_array)[1]


        # Implicitly skip user inputs for context and descriptor set-up if
        # the descriptor and context tags already exist.
        self.ctxt_tag = ctxt_tag
        self.descr_tag = descr_tag

        if not(CTXT_Register.check_register(ctxt_tag)):
            # TODO: ERROR CHECK TO ENSURE TOTAL NPROC MATCHES GRID OF CTXT_M X CTXT_N
            if ((ctxt_mp == -1) or (ctxt_np == -1)):
                MP, NP = find_squarest_grid(self.ntasks)
            else:
                MP, NP = ctxt_mp, ctxt_np

            ctxt = BLACSContextManager(self.ctxt_tag, MP, NP, self.sl)

        if not(DESCR_Register.check_register(descr_tag)):
            # TODO: ERROR CHECK TO ENSURE THAT CONTEXT MATCHES DESCRIPT
            descr = BLACSDESCRManager(self.ctxt_tag, self.descr_tag, self.sl, gl_m, gl_n,
                                      dmb, dnb, drsrc, dcsrc, dlld)

        # If an already distributed array is given, either cast the pointers to
        # local numpy arrays or directly transfer the array with proper ordering
        if init_loc:
            self.gl_array=None
            if isinstance(loc_array, ctypes._Pointer):
                #self.loc_array = ctypes2ndarray(loc_array, shape=(self.descr.locrow*self.descr.loccol)).T
                self.loc_array = np.ctypeslib.as_array(loc_array, shape=(self.descr.locrow*self.descr.loccol,)).copy()
                self.loc_array = self.loc_array.reshape((self.descr.locrow,self.descr.loccol), order='F')
            else:
                self.loc_array = loc_array.reshape((self.descr.locrow,self.descr.loccol), order='F')
                #self.loc_array = loc_array.reshape((self.descr.locrow,self.descr.loccol)).T

        if init_zero:
            self.gl_array=None
            self.loc_array = self.descr.alloc_zeros(dtype=np.float64) 

        # If a global array is given, scatter the array with the proper Fortran
        # ordering
        if init_gl:
            self.gl_array = np.asfortranarray(gl_array)
            self.loc_array = self.scatter_to_local()

        # Establish the global to local index mapping arrays for later use
        self.set_mapping_array()

        # We don't actually do any transpose operations here - the transpose tag is
        # passed to the relevant scalapack function
        self.transpose = [False]

    @property
    def gl_array(self):
        return self._gl_array

    @gl_array.setter
    def gl_array(self, val):
        self._gl_array = val

    @property
    def gl_m(self):
        return self.descr.m

    @property
    def gl_n(self):
        return self.descr.n

    def set_mapping_array(self):
        lr2gr = self.gl_m * [-1]
        lc2gc = self.gl_n * [-1]

        mb = self.descr.mb
        nb = self.descr.nb
        nprow = self.descr.nprow
        npcol = self.descr.npcol
        myrow = self.descr.myrow
        mycol = self.descr.mycol

        self.lr2gr_map = self.gl_m * [-1]
        idx = 0
        for i in range(self.gl_m):
            if ( int(i/mb % nprow) == myrow ):
                self.lr2gr_map[i] = nb * int(i / (mb * nprow)) + int(i % mb)

        self.lc2gc_map = self.gl_n * [-1]
        idx = 0
        for i in range(self.gl_n):
            if ( int(i/nb % npcol) == mycol ):
                self.lc2gc_map[i] = nb * int(i / (nb * npcol)) + int(i % nb)
        
    @property
    def loc_array(self):
        return self._loc_array

    @loc_array.setter
    def loc_array(self, val):
        self._loc_array = val

    @property
    def loc_array_ptr(self):
        return self.loc_array.ctypes.data_as(POINTER(c_double))

    @property
    def ctxt(self):
        # Important to avoid cyclic references - do not add the DESCR objects
        # as an attribute of NPScal to let the garbage collector do it's
        # work.
        return CTXT_Register.get_register(self.ctxt_tag)

    @property
    def descr(self):
        # Important to avoid cyclic references - do not add the DESCR objects
        # as an attribute of NPScal to let the garbage collector do it's
        # work.
        return DESCR_Register.get_register(self.descr_tag)

    def rank_from_rc(self, row, col):
        return row * self.descr.npcol + col

    def prow_from_idx(self, idx):
        return int(idx/self.descr.mb % self.descr.nprow)

    def pcol_from_idx(self, idx):
        return int(idx/self.descr.nb % self.descr.npcol)

    #TODO: SENSIBLE OVERLOADING OF THIS INTERFACE
    def __getitem__(self, idx):
        from .index_utils.npscal_select import select_single_val 
        from .index_utils.npscal_select import select_slice

        if len(idx) != 2:
            raise Exception("Please use two indices.")

        idx1 = idx[0]
        idx2 = idx[1]
        
        # Convert mask to slice
        if (type(idx1) is list) or (type(idx1) is np.ndarray):
            isbool = all([((type(x) is bool) or (type(x) is np.bool_)) for x in idx1])
            # Convert mask to integer list
            if isbool:
                idx1 = [i for (i, x) in enumerate(idx1) if x]

            idx1.sort()
            isconseq = np.all(np.ediff1d(idx1) == 1)

            if not(isconseq):
                raise Exception("Only continuous values with continuous indices may be set")
            else:
                idx1 = slice(np.array(idx1).min(), np.array(idx1).max()+1, None)

        if (type(idx2) is list) or (type(idx2) is np.ndarray):
            isbool = all([((type(x) is bool) or (type(x) is np.bool_)) for x in idx2])
            # Convert mask to integer list
            if isbool:
                idx2 = [i for i, x in enumerate(idx2) if x]
            idx2.sort()
            isconseq = np.all(np.ediff1d(idx2) == 1)

            if not(isconseq):
                raise Exception("Only continuous values with continuous indices may be set")
            else:
                idx2 = slice(np.min(idx2), np.max(idx2)+1, None)

        if (isinstance(idx1, int) and isinstance(idx2, int)):
            return select_single_val(self, [idx1, idx2])

        if (isinstance(idx1, slice) or isinstance(idx2, slice)):
            return select_slice(self, [idx1, idx2])

    #TODO: SENSIBLE OVERLOADING OF THIS INTERFACE
    def __setitem__(self, idx, val_set):
        from .index_utils.npscal_select import set_slice
        
        if len(idx) != 2:
            raise Exception("Please use two indices.")

        idx1 = idx[0]
        idx2 = idx[1]

        # If a list is provided, check whether the list is continuous
        # and convert to slice

        # Convert mask to slice
        if idx1 is list:
            isint = all([type(x) is int for x in idx1])
            isbool = all([type(x) is bool for x in idx1])

            # Convert mask to integer list
            if isbool:
                idx1 = [i for i, x in emumerate(idx1) if x]

            idx1.sort()
            isconseq = np.all(np.ediff1d(idx1) == 1)

            if not(isconseq):
                raise Exception("Only continuous values with continuous indices may be set")
            else:
                idx1 = slice(np.min(idx1), np.max(idx1), None)

        if idx2 is list:
            isint = all([type(x) is int for x in idx2])
            isbool = all([type(x) is bool for x in idx2])

            # Convert mask to integer list
            if isbool:
                idx2 = [i for i, x in emumerate(idx2) if x]

            idx2.sort()
            isconseq = np.all(np.ediff1d(idx2) == 1)

            if not(isconseq):
                raise Exception("Only continuous values with continuous indices may be set")
            else:
                idx2 = slice(np.min(idx2), np.max(idx2), None)

        # Actual setting done here
        if (isinstance(idx1, int) and isinstance(idx2, int)):
            
            lidx1 = self.lr2gr_map[idx1]
            lidx2 = self.lc2gc_map[idx2]

            if (lidx1 != -1 and lidx2 != -1):
                self.loc_array[lidx1, lidx2] = val_set

            return None

        # Let's just do a stupid and slow implementation for now
        # We can worry about doing something faster later

        # 1D (columns) Array Setting
        if (isinstance(idx1, slice) and (not isinstance(idx2, slice))):
            start = idx1.start
            stop = idx1.stop

            if start is None:
                start = 0
            if stop is None:
                stop = self.gl_n - 1

            lidx2 = self.lc2gc_map[idx2]
            for i in range(start, stop):
                lidx1 = self.lr2gr_map[i]
                if (lidx1 != -1 and lidx2 != -1):
                    self.loc_array[lidx1, lidx2] = val_set[i]

            return None
        
        # 1D (rows) Array Setting
        if (not isinstance(idx1, slice) and (isinstance(idx2, slice))):
            start = idx2.start
            stop = idx2.stop

            if start is None:
                start = 0
            if stop is None:
                stop = self.gl_m - 1

            lidx2 = self.lr2gr_map[idx1]
            for i in range(start, stop):
                lidx1 = self.lc2gc_map[i]
                if (lidx1 != -1 and lidx2 != -1):
                    self.loc_array[lidx1, lidx2] = val_set[i]

            return None

        # 2D (subarray) Array Setting
        if (isinstance(idx1, slice) and (isinstance(idx2, slice))):

            if type(val_set) is np.ndarray:
            
                start_r = idx1.start
                stop_r = idx1.stop

                start_c = idx2.start
                stop_c = idx2.stop

                if start_r is None:
                    start_r = 0
                if start_c is None:
                    start_c = 0
                if stop_r is None:
                    stop_r = self.gl_m - 1
                if stop_c is None:
                    stop_c = self.gl_n - 1

                lidx2 = self.lr2gr_map[idx2]
                for i in range(start_r, stop_r):
                    for j in range(start_c, stop_c):
                        lidx1 = self.lr2gr_map[i]
                        lidx2 = self.lc2gc_map[j]

                        if (lidx1 != -1 and lidx2 != -1):
                            self.loc_array[lidx1, lidx2] = val_set[i, j]

                return None

            if type(val_set) is type(self):
                self = set_slice(val_set, self, idx)
                return None
        
    def __add__(self, val):
        new_loc_array = self.loc_array + val.loc_array

        add_result = NPScal(loc_array=new_loc_array, ctxt_tag=self.ctxt_tag, descr_tag=self.descr_tag, lib=self.sl)

        return add_result

    def __radd__(self, val):
        new_loc_array = val.loc_array + self.loc_array

        add_result = NPScal(loc_array=new_loc_array, ctxt_tag=self.ctxt_tag, descr_tag=self.descr_tag, lib=self.sl)

        return add_result

    def __sub__(self, val):
        new_loc_array = self.loc_array - val.loc_array

        add_result = NPScal(loc_array=new_loc_array, ctxt_tag=self.ctxt_tag, descr_tag=self.descr_tag, lib=self.sl)
        
        return add_result

    def __rsub__(self, val):
        new_loc_array = val.loc_array - self.loc_array

        sub_result = NPScal(loc_array=new_loc_array, ctxt_tag=self.ctxt_tag, descr_tag=self.descr_tag, lib=self.sl)
        
        return sub_result

    def __matmul__(self, inp_mat):
        from .math_utils.npscal2npscal import matmul

        if type(inp_mat) is np.ndarray:
            # Convert the input numpy array to an NPScal array
            ctxt_tag = self.ctxt_tag

            dims = np.shape(inp_mat)

            if len(dims) == 1:
                gl_m = dims[0]
                gl_n = 1
            elif len(dims) == 2:
                gl_m = dims[0]
                gl_n = dims[1]
            else:
                raise Exception("Invalid number of array dimensions in __matmul__")
                        
            np_descr_tag = f"matmul_{gl_m}_{gl_n}"

            inp_mat = NPScal(gl_array=inp_mat, ctxt_tag=ctxt_tag, descr_tag=np_descr_tag, lib=self.sl,
                             gl_m=gl_m, gl_n=gl_n, dmb=self.descr.mb, dnb=self.descr.nb,
                             drsrc=self.descr.rsrc,dcsrc=self.descr.csrc, dlld=None)

        newmat = matmul(self, inp_mat)

        self = self.N
        inp_mat = inp_mat.N
        newmat = newmat.N

        return newmat

    def __rmatmul__(self, inp_mat):
        from .math_utils.npscal2npscal import matmul

        if type(inp_mat) is np.ndarray:
            # Convert the input numpy array to an NPScal array
            ctxt_tag = self.ctxt_tag

            dims = np.shape(inp_mat)

            if len(dims) == 1:
                gl_m = dims[0]
                gl_n = 1
            elif len(dims) == 2:
                gl_m = dims[0]
                gl_n = dims[1]
            else:
                raise Exception("Invalid number of array dimensions in __matmul__")
                        
            np_descr_tag = f"matmul_{gl_m}_{gl_n}"

            inp_mat = NPScal(gl_array=inp_mat, ctxt_tag=ctxt_tag, descr_tag=np_descr_tag, lib=self.sl,
                             gl_m=gl_m, gl_n=gl_n)

        newmat = matmul(inp_mat, self)
        self = self.N
        inp_mat = inp_mat.N
        newmat = newmat.N

        return newmat

    def __mul__(self, val):
        self.loc_array = self.loc_array * val
        return self

    def __rmul__(self, val):
        self.loc_array = val * self.loc_array
        return self

    def __div__(self, val):
        self.loc_array = self.loc_array / val
        return self

    def __del__(self):
        return None

    def __str__(self):
        return str(self.loc_array)

    def gather_to_global(self):
        self.gl_array = self.sl.gather_numpy(POINTER(c_int)(self.descr), self.loc_array.ctypes.data_as(POINTER(c_double)), (self.gl_n, self.gl_m))

        self.gl_array = self.comm.bcast([self.gl_array, np.float64], root=0)[0]

        return self.gl_array

    def scatter_to_local(self):
        gl_array = self.gl_array if self.rank == 0 else None

        self.loc_array = self.descr.alloc_zeros(dtype=np.float64).reshape((self.descr.locrow, self.descr.loccol), order='F')

        self.sl.scatter_numpy(gl_array, POINTER(c_int)(self.descr), self.loc_array.ctypes.data_as(POINTER(c_double)), self.loc_array.dtype)

        return self.loc_array

    @property
    def T(self):
        # Unliked numpy, where matrix transposition is pretty simple,
        # it represents a large communication bottleneck for ScaLAPACK
        # As we should only ever really use transposed matrices to perform
        # some kind of operation, we will use it to set a transposition
        # flag, which is passed to the routine and unset it once we're done.

        self.transpose = [True]
        return self

    @property
    def N(self):
        # Unliked numpy, where matrix transposition is pretty simple,
        # it represents a large communication bottleneck for ScaLAPACK
        # As we should only ever really use transposed matrices to perform
        # some kind of operation, we will use it to set a transposition
        # flag, which is passed to the routine and unset it once we're done.

        self.transpose = [False]
        return self
    
    def copy(self):
        import copy

        new_self = copy.copy(self)
        new_self.loc_array = copy.deepcopy(self.loc_array)
        return new_self
