from scalapack4py.array_types import nullable_ndpointer, ctypes2ndarray
from ..npscal import NPScal
from ..comms import mpi_bcast_float, mpi_bcast_integer
from ..blacs_ctxt_management import BLACSDESCRManager, CTXT_Register
import numpy as np

def select_single_val(npscal, val, bcast=True):

        # Only want one value wanted - give it back
        # And broadcast to all tasks
        idx1 = val[0]
        idx2 = val[1]
    
        lidx1 = npscal.lr2gr_map[idx1]
        lidx2 = npscal.lc2gc_map[idx2]

        if (lidx1 != -1 and lidx2 != -1):
            out = npscal.loc_array[lidx1, lidx2]
        else:
            out = 0

        root_r = npscal.prow_from_idx(idx1)
        root_c = npscal.pcol_from_idx(idx2)
        root = npscal.rank_from_rc(root_r, root_c)

        if bcast:
            out_val = mpi_bcast_float(out, root)
            return out_val
        else:
            return out

def select_slice(npscal, val):

    # Generates a new instance of NPScal with the
    # desired shape and a new distribution
    val = list(val)
        
    if isinstance(val[0], int):
        newstart, newend = val[0], val[0] + 1
        val[0] = slice(newstart, newend, None)
    if isinstance(val[1], int):
        newstart, newend = val[1], val[1] + 1
        val[1] = slice(newstart, newend, None)

    if val[0].start is None:
        gl_row_start = 1
    else:
        gl_row_start = val[0].start + 1
    if val[1].start is None:
        gl_col_start = 1
    else:
        gl_col_start = val[1].start + 1

    if val[0].stop is None:
        gl_row_end = npscal.gl_m
    else:
        gl_row_end = val[0].stop
    if val[1].stop is None:
        gl_col_end = npscal.gl_n
    else:
        gl_col_end = val[1].stop

    new_m = gl_row_end - gl_row_start + 1
    new_n = gl_col_end - gl_col_start + 1

    if new_m == 1 or new_n == 1:
        # We are just using a column or row here - in that case, just return an ndarray
        # Given that the contexts created here are temporary, we do not bother logging
        # them into the context manager
        new_ctx = npscal.sl.make_blacs_context(npscal.sl.get_system_context(npscal.ctxt.ctxt), 1, 1)
        descr_new = npscal.sl.make_blacs_desc(new_ctx, new_m, new_n)
        submatrix = np.zeros((new_m, new_n), dtype=np.float64).T if (descr_new.myrow==0 and descr_new.mycol==0) else None

        npscal.sl.pdgemr2d(new_m, new_n, npscal.loc_array, gl_row_start, gl_col_start, npscal.descr,
                           submatrix, 1, 1, descr_new, npscal.ctxt.ctxt)

        submatrix = npscal.comm.bcast([submatrix, np.float64], root=0)[0]

        if new_m == 1:
            submatrix = submatrix.reshape(new_n)
        if new_n == 1:
            submatrix = submatrix.reshape(new_m)

    else:
        # Return a new NPScal object with a new distribution
        descr_tag = f"getitem_{new_m}_{new_n}"
        submatrix = NPScal(ctxt_tag=npscal.ctxt_tag, descr_tag=descr_tag, lib=npscal.sl,
                           gl_m=new_m, gl_n=new_n)
        
        npscal.sl.pdgemr2d(new_m, new_n, npscal.loc_array, gl_row_start, gl_col_start, npscal.descr,
                           submatrix.loc_array, 1, 1, submatrix.descr, npscal.ctxt.ctxt)

    return submatrix


def set_slice(src_npscal, dest_npscal, val):

    # Generates a new instance of NPScal with the
    # desired shape and a new distribution
    #print(val)

    val = list(val)
        
    if isinstance(val[0], int):
        newstart, newend = val[0], val[0] + 1
        val[0] = slice(newstart, newend, None)
    if isinstance(val[1], int):
        newstart, newend = val[1], val[1] + 1
        val[1] = slice(newstart, newend, None)

    if val[0].start is None:
        gl_row_start = 1
    else:
        gl_row_start = val[0].start + 1
    if val[1].start is None:
        gl_col_start = 1
    else:
        gl_col_start = val[1].start + 1

    if val[0].stop is None:
        gl_row_end = npscal.gl_m
    else:
        gl_row_end = val[0].stop
    if val[1].stop is None:
        gl_col_end = npscal.gl_n
    else:
        gl_col_end = val[1].stop

    new_m = gl_row_end - gl_row_start + 1
    new_n = gl_col_end - gl_col_start + 1

    src_npscal.sl.pdgemr2d(new_m, new_n, src_npscal.loc_array, 1, 1, src_npscal.descr,
                       dest_npscal.loc_array, gl_row_start, gl_col_start, dest_npscal.descr, src_npscal.ctxt.ctxt)

    return dest_npscal

def diagonal(npscal):
    # Already, the global selection syntax bears some fruit - we
    # no longer have to wrangle with local row/local column
    # indexing.

    #print(npscal.lc2gc_map[idx2])
    #print(npscal.lc2gc_map)
    diag = np.zeros(npscal.gl_n)
    for i in range(npscal.gl_n):
        diag[i] = npscal[i,i]

    return diag
                
                
