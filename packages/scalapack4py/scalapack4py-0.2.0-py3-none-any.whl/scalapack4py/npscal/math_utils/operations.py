import numpy as np
from ..npscal import NPScal
from ..index_utils.npscal_select import diagonal

def diag(array, k=0, descr_tag=None, ctxt_tag=None, lib=None):

    if type(array) is NPScal:
        return diagonal(array)
        
    if type(array) is np.ndarray:
        if descr_tag is None:
            return np.diag(array, k=k)

        if len(np.shape(array)) == 1:
            m = np.size(array)
            n = np.size(array)

            new_diag_tag = f"newdiag_{m}_{n}"
            full_diag_dist = NPScal(ctxt_tag=ctxt_tag, descr_tag=new_diag_tag, lib=lib,
                                    gl_m=m, gl_n=n)

            for idx, i in enumerate(array):
                full_diag_dist[idx,idx] = i

            return full_diag_dist

def trace(array, **kwargs):

    if type(array) is NPScal:
        result = diag(array)
        result = np.sum(result)
        
    if type(array) is np.ndarray:
        result = np.trace(array, **kwargs)

    return result
        
def eig(array, vl, vu, b=None, left=False, right=True, overwrite_a=False, overwrite_b=False,
        check_finite=True, homogeneous_eigvals=False):

    if type(array) is NPScal:

        print("NOT IMPLEMENTED")
        
    if type(array) is np.ndarray:
        result = np.linalg.eig(array, b, left, right, overwrite_a, overwrite_b, check_finite,
                               homogeneous_eigvals)

        if left or right:
            return result[0], result[1]
        else:
            return result
    
