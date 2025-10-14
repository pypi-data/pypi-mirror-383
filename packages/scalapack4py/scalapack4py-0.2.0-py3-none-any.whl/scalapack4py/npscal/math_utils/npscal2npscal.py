from ..npscal import NPScal
from ..blacs_ctxt_management import DESCR_Register, BLACSDESCRManager
import numpy as np

def matmul(self_mat, inp_mat):
    if inp_mat.transpose[0]:
        transB = "T"
        n = inp_mat.gl_m
    else:
        transB = "N"
        n = inp_mat.gl_n
    if self_mat.transpose[0]:
        transA = "T"
        m = self_mat.gl_n
        k = self_mat.gl_m
    else:
        transA = "N"
        m = self_mat.gl_m
        k = self_mat.gl_n

    alpha = 1.0
    beta = 1.0

    ctxt_tag = self_mat.ctxt.tag
    
    desc_a = self_mat.descr
    desc_b = inp_mat.descr

    desc_c_tag = f"matmul_{ctxt_tag}_{m}_{n}"
    newmat = NPScal(ctxt_tag=ctxt_tag, descr_tag=desc_c_tag, lib=inp_mat.sl,
                    gl_m=m, gl_n=n, dmb=desc_a.mb, dnb=desc_a.nb, drsrc=desc_a.rsrc,
                    dcsrc=desc_a.csrc, dlld=None)

    desc_c = newmat.descr
    self_mat.sl.pdgemm(transA, transB, m, n, k,
                   alpha, self_mat.loc_array, 1, 1, desc_a,
                   inp_mat.loc_array, 1, 1, desc_b,
                   beta, newmat.loc_array, 1, 1, desc_c)
    return newmat

def rmatmul(self_mat, inp_mat):
    if self_mat.transpose[0]:
        transB = "T"
        n = self_mat.gl_m
    else:
        transB = "N"
        n = self_mat.gl_n
    if inp_mat.transpose[0]:
        transA = "T"
        m = inp_mat.gl_n
        k = inp_mat.gl_m
    else:
        transA = "N"
        m = inp_mat.gl_m
        k = inp_mat.gl_n

    alpha = 1.0
    beta = 1.0

    ctxt_tag = inp_mat.ctxt.tag
    
    desc_a = inp_mat.descr
    desc_b = self_mat.descr

    if (m == n and n == k):
        # No need for new descriptor, just use the descriptor of A in A @ B
        desc_c_tag = inp_mat.descr_tag
    else:
        desc_c_tag = f"matmul_{ctxt_tag}_{m}_{n}"

    newmat = NPScal(ctxt_tag=ctxt_tag, descr_tag=desc_c_tag, lib=inp_mat.sl,
                gl_m=m, gl_n=n, dmb=desc_a.mb, dnb=desc_a.nb, drsrc=desc_a.rsrc,
                dcsrc=desc_a.csrc, dlld=None)

    desc_c = newmat.descr

    self_mat.sl.pdgemm(transA, transB, m, n, k,
                   alpha, inp_mat.loc_array, 1, 1, desc_a,
                   self_mat.loc_array, 1, 1, desc_b,
                   beta, newmat.loc_array, 1, 1, desc_c)

    return newmat

def eig(self_mat, vl=None, vu=None):

    from scalapack4py import ScaLAPACK4py
    from ctypes import CDLL, POINTER, c_int
    from mpi4py import MPI

    # Ideally, we don't want to be doing copy operations, but
    # PDSYEVX destroys the diagonal and the lower/upper matrix
    # segment - users tend to like their input data being unaltered.
    input_mat = self_mat.copy()
    
    ctxt_tag = input_mat.ctxt_tag
    descr_tag = input_mat.descr_tag

    ctxt = input_mat.ctxt

    n = input_mat.gl_m
    dtype = np.float64
    descr = input_mat.descr

    # Execution of PDSYEVX
    w = np.asfortranarray(np.zeros(n))
    z = NPScal(ctxt_tag=ctxt_tag, descr_tag=descr_tag, lib=input_mat.sl,
               gl_m=n, gl_n=n, dmb=descr.mb, dnb=descr.nb, drsrc=descr.rsrc, dcsrc=descr.csrc,
               dlld=None)

    # Parameters for PDSYEVX
    jobz = "V"  
    uplo = "U"  
    ia = 1
    ja = 1 
    iz = 1
    jz = 1
    if vl is None:
        vl = 0.
        vu = 0.
        range_type = "A"
    else:
        vl = vl
        vu = vu
        range_type = "V"
    il = 1  
    iu = n  
    abstol = 2.0 * 1e-15
    orfac = -1.0

    # Output parameters
    m = 0  
    nz = 0

    # Workspace query for PDSYEVX
    lwork = -1
    liwork = -1
    work = np.zeros(1, dtype=np.float64, order='F')
    iwork = np.zeros(1, dtype=np.int32, order='F')
    info = 0

    ifail = np.asfortranarray(np.zeros(n, dtype=np.int32))
    iclustr = np.zeros(1, dtype=np.int32, order='F')
    gap = np.zeros(1, dtype=np.float64, order='F')
    input_mat.sl.pdsyevx("V", range_type, "U", n, input_mat.loc_array, ia, ja, descr,
               vl, vu, il, iu, abstol, m, nz, w, orfac, z.loc_array, iz, jz, descr,
               work, lwork, iwork, liwork, ifail, iclustr, gap, info)

    # Execute PDSYEVX with optimal workspace
    lwork = int(work[0])
    liwork = int(iwork[0])
    work = np.zeros(lwork, dtype=np.float64, order='F')
    iwork = np.zeros(liwork, dtype=np.int32, order='F')

    # Find nlocal rows and columns 
    nprow, npcol, myrow, mycol = descr.nprow, descr.npcol, descr.myrow, descr.mycol
    ifail = np.zeros(n, dtype=np.int32, order='F')
    iclustr = np.zeros(2 * nprow * npcol, dtype=np.int32, order='F')
    gap = np.zeros(nprow * npcol, dtype=np.float64, order='F')

    # Call PDSYEVX with optimal workspace
    input_mat.sl.pdsyevx("V", range_type, "U", n, input_mat.loc_array, ia, ja, descr, 
               vl, vu, il, iu, abstol, m, nz, w, orfac, z.loc_array, iz, jz, descr, 
               work, lwork, iwork, liwork, ifail, iclustr, gap, info)

    eigvals = w
    eigvecs = z

    return eigvals, eigvecs

def svd(inp_mat):

    from ..blacs_ctxt_management import BLACSDESCRManager, DESCR_Register

    # Ideally, we don't want to be doing copy operations, but
    # PDSYEVX destroys the diagonal and the lower/upper matrix
    # segment - users tend to like their input data being unaltered.
    self_mat = inp_mat.copy()


    ctxt_tag = self_mat.ctxt_tag
    descr_tag = self_mat.descr_tag
    ctxt = self_mat.ctxt
    descr = self_mat.descr

    m, n = self_mat.gl_m, self_mat.gl_n
    dtype = np.float64

    size = min(m, n)

    s = np.zeros(size, dtype=dtype, order='F')

    u = NPScal(ctxt_tag=ctxt_tag, descr_tag=f"svdu_{ctxt}_{m}_{size}", lib=self_mat.sl,
               gl_m=m, gl_n=size, dmb=descr.mb, dnb=descr.nb, drsrc=descr.rsrc, dcsrc=descr.csrc,
               dlld=None)

    vt = NPScal(ctxt_tag=ctxt_tag, descr_tag=f"svdvt_{ctxt}_{size}_{n}", lib=self_mat.sl,
               gl_m=size, gl_n=n, dmb=descr.mb, dnb=descr.nb, drsrc=descr.rsrc, dcsrc=descr.csrc,
               dlld=None)

    work = np.zeros(1, dtype=np.float64, order='F')

    # Workspace query for PDGESVD
    lwork = -1
    rwork = -1
    info = -1
    self_mat.sl.pdgesvd("V", "V", m, n, self_mat.loc_array, 1, 1, descr,
               s, u.loc_array, 1, 1, u.descr, vt.loc_array, 1, 1, vt.descr,
               work, lwork, info) 

    # Execute PDGESVD with optimal workspace
    lwork = int(work[0])
    work = np.zeros((lwork), dtype=dtype, order='F')
    self_mat.sl.pdgesvd("V", "V", m, n, self_mat.loc_array, 1, 1, descr,
               s, u.loc_array, 1, 1, u.descr, vt.loc_array, 1, 1, vt.descr,
               work, lwork, info)

    u_gather = u
    s_vals = s
    vt_gather = vt

    return u_gather, s_vals, vt_gather
