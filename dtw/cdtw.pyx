# This is a cython wrapper around core dtw module written in C.
#  
#   Author: Sankalp gulati
#   email: sankalp.gulati@gmai.com
#   Affiliation: Universitat Pompeu Fabra
#   
#   License: to be decided !!!   
#
import numpy as np
cimport numpy as np
from libc.stdlib cimport *
from cdtw cimport *

np.import_array()

def dtwNd(x, y, configuration):
    """Modified version of standard DTW as described in [Muller07] and [Keogh01],
    Modified code provided in mlpy.dtw
    DTW code is changed and added specific funtionalities to handle melodic similarity in addition
    to general time series. See additional functionalities below:
      
    :Parameters:
    x : Nxn d numpy array (length N) first sequence[for n dimensional features]
    y : Mxn d numpy array (length M) second sequence [for n dimensional features]
    configuration: dictionary specifying configuration params
    configuration = {
            'Output': n = {1-4} specify how many items you need from this ordered list
                'udist' (unnormalized warped distance)
                'plength' (path length)
                'path' (tuple of dtw path)              
                'cost' (cost matrix)
                
            'Ldistance': {
                  'type': 0 (Euclidean) or 1 (squared Euclidean)
                  'weight': [weight_mtx]
                  }
            'Constraint': {
                  'type':''
                  'CVal':
                  }   
              }
    :Returns: a list of same entities specified in the configuration parameter for 'Output'
    udist : (float) unnormalized minimum-distance of warp path between sequences
    plength : (float) path length 
    path : tuple of two 1d numpy array (path_x, path_y) warp path
    cost : 2d numpy array (N,M) containing accumulated cost matrix
    
      
    References
    .. [Muller07] M Muller. Information Retrieval for Music and Motion. Springer, 2007.
    .. [Keogh01] E J Keogh, M J Pazzani. Derivative Dynamic Time Warping. In FirsWt SIAM International Conference on Data Mining, 2001.
      
    Additional Functionalities:
    1) DTW path constraints
    2) Support for N dimensional input data in addition to just single dimension
    3) Many more options for computing local cost (using N dimensional data + modulus option useful for melodic similarity)   
      
      """
      #setting up system configuration according to input configuration
    cdef Config myconfig_t
    myconfig_t.DistMthd = configuration['Ldistance']['type']
    
    '''if not configuration['Ldistance'].has_key('mod'):
        configuration['Ldistance']['mod']=[False, -1 0]
        myconfig_t.mod_val=configuration['Ldistance']['mod'][1]
        myconfig_t.mod_dim=configuration['Ldistance']['mod'][2]'''
    
    
    if len(x.shape)==1:
        x = np.array([x])
        x = np.transpose(x)
    if len(y.shape)==1:
        y = np.array([y])
        y = np.transpose(y)   
    
    
    cdef np.ndarray[np.float_t, ndim=2] x_arr
    cdef np.ndarray[np.float_t, ndim=2] y_arr  
    cdef np.ndarray[np.float_t, ndim=2] cost_arr
    cdef np.ndarray[np.int_t, ndim=1] px_cord
    cdef np.ndarray[np.int_t, ndim=1] py_cord
    cdef np.ndarray[np.float_t, ndim=1] DistWghts
    cdef double udist
    cdef MatrixSize size_x_t,size_y_t
    cdef DTW_path path_t    
    cdef int NFeatDim
    
    # use the number of feature dimension which is lesser of two series. Ideally should have equal dimensions
    NFeatDim = min(x.shape[1], y.shape[1])
    
    size_x_t.Nrow = x.shape[0]
    size_x_t.Ncol = x.shape[1]
    size_y_t.Nrow = y.shape[0]
    size_y_t.Ncol = y.shape[1]  
    
    x_arr = np.ascontiguousarray(x, dtype=np.float)
    y_arr = np.ascontiguousarray(y, dtype=np.float)
    DistWghts = np.ascontiguousarray(configuration['Ldistance']['weight'], dtype=np.float)
    myconfig_t.DistWghts = <double *>DistWghts.data
    #print DistWghts
    
    cost_arr = np.empty((x_arr.shape[0], y_arr.shape[0]), dtype=np.float)
        
    udist = dtwNd_std(<double *>x_arr.data, <double*>y_arr.data,
                  &size_x_t,&size_y_t,NFeatDim,
                  <double*>cost_arr.data, &myconfig_t)
    
    if configuration['Output'] ==1:
        
        return udist
    
    else:
        print('start to generate path')
        path(<double*>cost_arr.data, cost_arr.shape[0], cost_arr.shape[1], -1, -1, &path_t)
        print('finish generate path')

        px_cord = np.empty(path_t.plen, dtype=np.int)
        py_cord = np.empty(path_t.plen, dtype=np.int)
        for i in range(path_t.plen):
            px_cord[i] = path_t.px[i]
            py_cord[i] = path_t.py[i] 
        free (path_t.px)
        free (path_t.py)
        print('done')

        if configuration['Output'] == 2:
            return udist, path_t.plen
        elif configuration['Output'] == 3:
            return udist, path_t.plen, (px_cord, py_cord)
        else:
            return udist, path_t.plen, (px_cord, py_cord), cost_arr
            
            
##############################################################################################################################
            
def dtw1d(x, y, configuration):
    """Modified version of standard DTW as described in [Muller07] and [Keogh01],
    Modified code provided in mlpy.dtw
    DTW code is changed and added specific funtionalities to handle melodic similarity in addition
    to general time series. See additional functionalities below:
      
    :Parameters:
    x : 1d numpy array (length N) first sequence
    y : 1d numpy array (length M) second sequence 
    configuration: dictionary specifying configuration params
    configuration = {
            'Output': n = {1-4} specify how many items you need from this ordered list
                'udist' (unnormalized warped distance)
                'plength' (path length)
                'path' (tuple of dtw path)              
                'cost' (cost matrix)
                
            'Ldistance': {
                  'type': 0 (Euclidean) or 1 (squared Euclidean) or 2 (octBy2WrappedCitiblock - used in makam music score alignment)
                   }
            'Constraint': {
                  'type':''
                  'CVal':
                  }   
              }
    :Returns: a list of same entities specified in the configuration parameter for 'Output'
    udist : (float) unnormalized minimum-distance of warp path between sequences
    plength : (float) path length 
    path : tuple of two 1d numpy array (path_x, path_y) warp path
    cost : 2d numpy array (N,M) containing accumulated cost matrix
    
      
    References
    .. [Muller07] M Muller. Information Retrieval for Music and Motion. Springer, 2007.
    .. [Keogh01] E J Keogh, M J Pazzani. Derivative Dynamic Time Warping. In FirsWt SIAM International Conference on Data Mining, 2001.
      
    Additional Functionalities:
    1) DTW path constraints
    2) Support for N dimensional input data in addition to just single dimension
    3) Many more options for computing local cost (using N dimensional data + modulus option useful for melodic similarity)   
      
      """
    cdef np.ndarray[np.float_t, ndim=1] x_arr
    cdef np.ndarray[np.float_t, ndim=1] y_arr  
    cdef np.ndarray[np.float_t, ndim=2] cost_arr
    cdef np.ndarray[np.int_t, ndim=1] px_cord
    cdef np.ndarray[np.int_t, ndim=1] py_cord
    
    cdef double udist
    cdef DTW_path path_t    
    
    x_arr = np.ascontiguousarray(x, dtype=np.float)
    y_arr = np.ascontiguousarray(y, dtype=np.float)
    
    cost_arr = np.empty((x_arr.shape[0], y_arr.shape[0]), dtype=np.float)
    print('start dtw')
    udist = dtw1d_std(<double *>x_arr.data, <double*>y_arr.data,
                  x_arr.shape[0],y_arr.shape[0],
                  <double*>cost_arr.data,configuration['Ldistance']['type'])
    print('dtw done')
    if configuration['Output'] ==1:
        
        return udist
    
    else:
        print('start path')
        path(<double*>cost_arr.data, cost_arr.shape[0], cost_arr.shape[1], -1, -1, &path_t)
        print('path done')
        px_cord = np.empty(path_t.plen, dtype=np.int)
        py_cord = np.empty(path_t.plen, dtype=np.int)
        for i in range(path_t.plen):
            px_cord[i] = path_t.px[i]
            py_cord[i] = path_t.py[i]
        free (path_t.px)
        free (path_t.py)
        print('processing done')
        
        if configuration['Output'] == 2:
            return udist, path_t.plen
        elif configuration['Output'] == 3:
            return udist, path_t.plen, (px_cord, py_cord)
        else:
            return udist, path_t.plen, (px_cord, py_cord), cost_arr         

            
def dtw1dLocalBand(x, y, configuration):
    """Modified version of standard DTW as described in [Muller07] and [Keogh01],
    Modified code provided in mlpy.dtw
    This version is a subsequence version of the code with local constraints and global band constraint:
      
    :Parameters:
    x : 1d numpy array (length N) first sequence
    y : 1d numpy array (length M) second sequence 
    configuration: dictionary specifying configuration params
    configuration = {
            'Output': n = {1-4} specify how many items you need from this ordered list
                'udist' (unnormalized warped distance)
                'plength' (path length)
                'path' (tuple of dtw path)              
                'cost' (cost matrix)
                
            'Ldistance': {
                  'type': 0 (Euclidean) or 1 (squared Euclidean) or 2 (octBy2WrappedCitiblock - used in makam music score alignment)
                   }
            'Constraint': {
                  'type':'Band' or 'Local' or 'BandLocal'
                  'CVal': bandwidth for band
                  }   
              }
    :Returns: a list of same entities specified in the configuration parameter for 'Output'
    udist : (float) unnormalized minimum-distance of warp path between sequences
    plength : (float) path length 
    path : tuple of two 1d numpy array (path_x, path_y) warp path
    cost : 2d numpy array (N,M) containing accumulated cost matrix
    
      
    References
    .. [Muller07] M Muller. Information Retrieval for Music and Motion. Springer, 2007.
    .. [Keogh01] E J Keogh, M J Pazzani. Derivative Dynamic Time Warping. In FirsWt SIAM International Conference on Data Mining, 2001.
      
    Additional Functionalities:
    1) DTW path constraints
    2) Support for N dimensional input data in addition to just single dimension
    3) Many more options for computing local cost (using N dimensional data + modulus option useful for melodic similarity)   
      
      """
    cdef np.ndarray[np.float_t, ndim=1] x_arr
    cdef np.ndarray[np.float_t, ndim=1] y_arr  
    cdef np.ndarray[np.float_t, ndim=2] cost_arr
    cdef np.ndarray[np.int_t, ndim=1] px_cord
    cdef np.ndarray[np.int_t, ndim=1] py_cord
    
    cdef double udist
    cdef DTW_path path_t    
    
    x_arr = np.ascontiguousarray(x, dtype=np.float)
    y_arr = np.ascontiguousarray(y, dtype=np.float)
    
    cost_arr = np.empty((x_arr.shape[0], y_arr.shape[0]), dtype=np.float)
        
    udist = dtw1d_BandConst_LocalConst(<double *>x_arr.data, <double*>y_arr.data, x_arr.shape[0],y_arr.shape[0], <double*>cost_arr.data,configuration['Ldistance']['type'], configuration['Constraint']['CVal'])

    if configuration['Output'] ==1:
        
        return udist
    
    else:
        
        path(<double*>cost_arr.data, cost_arr.shape[0], cost_arr.shape[1], -1, -1, &path_t)
        
        px_cord = np.empty(path_t.plen, dtype=np.int)
        py_cord = np.empty(path_t.plen, dtype=np.int)
        for i in range(path_t.plen):
            px_cord[i] = path_t.px[i]
            py_cord[i] = path_t.py[i] 
        free (path_t.px)
        free (path_t.py)
        
        if configuration['Output'] == 2:
            return udist, path_t.plen
        elif configuration['Output'] == 3:
            return udist, path_t.plen, (px_cord, py_cord)
        else:
            return udist, path_t.plen, (px_cord, py_cord), cost_arr 
            
def dtw1d_GLS(x, y, configuration):
    """Modified version of standard DTW as described in [Muller07] and [Keogh01],
    Modified code provided in mlpy.dtw
    This version is a subsequence version of the code with local constraints and global band constraint:
      
    :Parameters:
    x : 1d numpy array (length N) first sequence
    y : 1d numpy array (length M) second sequence 
    
    :Returns: a list of same entities specified in the configuration parameter for 'Output'
    udist : (float) unnormalized minimum-distance of warp path between sequences
    plength : (float) path length 
    path : tuple of two 1d numpy array (path_x, path_y) warp path
    cost : 2d numpy array (N,M) containing accumulated cost matrix
    
      
    References
    .. [Muller07] M Muller. Information Retrieval for Music and Motion. Springer, 2007.
    .. [Keogh01] E J Keogh, M J Pazzani. Derivative Dynamic Time Warping. In FirsWt SIAM International Conference on Data Mining, 2001.
    """
      
    cdef np.ndarray[np.float_t, ndim=1] x_arr
    cdef np.ndarray[np.float_t, ndim=1] y_arr  
    cdef np.ndarray[np.float_t, ndim=2] cost_arr
    cdef np.ndarray[np.int_t, ndim=1] px_cord
    cdef np.ndarray[np.int_t, ndim=1] py_cord
    
    cdef double udist
    cdef DTW_path path_t    
    cdef dtwParams_t myDtwParama
    

    x_arr = np.ascontiguousarray(x, dtype=np.float)
    y_arr = np.ascontiguousarray(y, dtype=np.float)
    
    cost_arr = np.ones((x_arr.shape[0], y_arr.shape[0]), dtype=np.float)
    
    myDtwParama.distType = configuration['distType'];
    myDtwParama.hasGlobalConst = configuration['hasGlobalConst'];
    myDtwParama.globalType = configuration['globalType'];
    myDtwParama.bandwidth = np.round(x_arr.shape[0]*configuration['bandwidth']).astype(np.int);
    myDtwParama.initCostMtx = configuration['initCostMtx'];
    myDtwParama.reuseCostMtx = configuration['reuseCostMtx'];
    myDtwParama.delStep = configuration['delStep'];
    myDtwParama.moveStep = configuration['moveStep'];
    myDtwParama.diagStep = configuration['diagStep'];
    myDtwParama.initFirstCol = configuration['initFirstCol'];
    myDtwParama.isSubsequence = configuration['isSubsequence'];
    
    print('start dtw_GLS')
    udist = dtw_GLS(<double *>x_arr.data, <double*>y_arr.data, x_arr.shape[0],y_arr.shape[0], <double*>cost_arr.data, myDtwParama)
    print('dtw_GLS done')

    y_cord = np.argmin(cost_arr[x_arr.shape[0]-1, :])
    x_cord = x_arr.shape[0]-1
    min_val = np.min(cost_arr[x_arr.shape[0]-1, :])
    if np.min(cost_arr[:,y_arr.shape[0]-1]) < min_val:
        x_cord = np.argmin(cost_arr[:,y_arr.shape[0]-1])
        y_cord = y_arr.shape[0]-1
    
    print('start pathLocal')
    pathLocal(<double*>cost_arr.data, cost_arr.shape[0], cost_arr.shape[1], x_cord, y_cord, &path_t, myDtwParama)
    print('pathLocal done')

    px_cord = np.empty(path_t.plen, dtype=np.int)
    py_cord = np.empty(path_t.plen, dtype=np.int)
    for i in range(path_t.plen):
        px_cord[i] = path_t.px[i]
        py_cord[i] = path_t.py[i] 
    free (path_t.px)
    free (path_t.py)
    print('algo done')
    return udist, path_t.plen, (px_cord, py_cord), cost_arr
    
    return udist     
            
def dtw1dSubLocalBand(x, y, configuration):
    """Modified version of standard DTW as described in [Muller07] and [Keogh01],
    Modified code provided in mlpy.dtw
    This version is a subsequence version of the code with local constraints and global band constraint:
      
    :Parameters:
    x : 1d numpy array (length N) first sequence
    y : 1d numpy array (length M) second sequence 
    configuration: dictionary specifying configuration params
    configuration = {
            'Output': n = {1-4} specify how many items you need from this ordered list
                'udist' (unnormalized warped distance)
                'plength' (path length)
                'path' (tuple of dtw path)              
                'cost' (cost matrix)
                
            'Ldistance': {
                  'type': 0 (Euclidean) or 1 (SqEuclidean) or 2 (CityBlock) or 3 (ShiftCityBlock) or 4 (TMM_CityBlock)- used in makam music score alignment) or 5 (ShiftLinExp)
                   }
            'Constraint': {
                  'type':'Band' or 'Local' or 'BandLocal'
                  'CVal': bandwidth for band
                  }   
              }
    :Returns: a list of same entities specified in the configuration parameter for 'Output'
    udist : (float) unnormalized minimum-distance of warp path between sequences
    plength : (float) path length 
    path : tuple of two 1d numpy array (path_x, path_y) warp path
    cost : 2d numpy array (N,M) containing accumulated cost matrix
    
      
    References
    .. [Muller07] M Muller. Information Retrieval for Music and Motion. Springer, 2007.
    .. [Keogh01] E J Keogh, M J Pazzani. Derivative Dynamic Time Warping. In FirsWt SIAM International Conference on Data Mining, 2001.
      
    Additional Functionalities:
    1) DTW path constraints
    2) Support for N dimensional input data in addition to just single dimension
    3) Many more options for computing local cost (using N dimensional data + modulus option useful for melodic similarity)   
      
      """
    cdef np.ndarray[np.float_t, ndim=1] x_arr
    cdef np.ndarray[np.float_t, ndim=1] y_arr  
    cdef np.ndarray[np.float_t, ndim=2] cost_arr
    cdef np.ndarray[np.int_t, ndim=1] px_cord
    cdef np.ndarray[np.int_t, ndim=1] py_cord
    
    cdef double udist
    cdef DTW_path path_t    
    
    x_arr = np.ascontiguousarray(x, dtype=np.float)
    y_arr = np.ascontiguousarray(y, dtype=np.float)
    
    cost_arr = np.empty((x_arr.shape[0], y_arr.shape[0]), dtype=np.float)
        
    udist = dtw1d_BandConst_LocalConst_Subsequence(<double *>x_arr.data, <double*>y_arr.data, x_arr.shape[0],y_arr.shape[0], <double*>cost_arr.data,configuration['Ldistance']['type'], configuration['Constraint']['CVal'])
    
    y_cord = np.argmin(cost_arr[x_arr.shape[0]-1, :])
    x_cord = x_arr.shape[0]-1
    min_val = np.min(cost_arr[x_arr.shape[0]-1, :])
    if np.min(cost_arr[:,y_arr.shape[0]-1]) < min_val:
        x_cord = np.argmin(cost_arr[:,y_arr.shape[0]-1])
        y_cord = y_arr.shape[0]-1
    
    if configuration['Output'] ==1:
        
        return udist
    
    else:
        
        path(<double*>cost_arr.data, cost_arr.shape[0], cost_arr.shape[1], x_cord, y_cord, &path_t)
        
        px_cord = np.empty(path_t.plen, dtype=np.int)
        py_cord = np.empty(path_t.plen, dtype=np.int)
        for i in range(path_t.plen):
            px_cord[i] = path_t.px[i]
            py_cord[i] = path_t.py[i] 
        free (path_t.px)
        free (path_t.py)
        
        if configuration['Output'] == 2:
            return udist, path_t.plen
        elif configuration['Output'] == 3:
            return udist, path_t.plen, (px_cord, py_cord)
        else:
            return udist, path_t.plen, (px_cord, py_cord), cost_arr 

def DistAlongPath(x, y, path, configuration):
    """This function computes the distance between two time series x and y along the provided "path"
      
    :Parameters:
    x : Nxn d numpy array (length N) first sequence[for n dimensional features]
    y : Mxn d numpy array (length M) second sequence [for n dimensional features]
    path: path along with distance has to be computed. Tuple with x and y coordinates
    configuration: dictionary specifying configuration params
    configuration = {
            'Ldistance': {
                  'type': 1 (Euclidean) or 2 (squared Euclidean)
                  'weight': [weight_mtx]
                    }   
            }
    :Returns: 
    udist : (float) unnormalized distance between two sequences according to given path
    """
      
      #setting up system configuration according to input configuration
    
    cdef Config myconfig_t
    myconfig_t.DistMthd = configuration['Ldistance']['type']
    
    if len(x.shape)==1:
        x = np.array([x])
        x = np.transpose(x)
    if len(y.shape)==1:
        y = np.array([y])
        y = np.transpose(y)   
    
    
    cdef np.ndarray[np.float_t, ndim=2] x_arr
    cdef np.ndarray[np.float_t, ndim=2] y_arr  
    cdef np.ndarray[np.int32_t, ndim=1] px_cord
    cdef np.ndarray[np.int32_t, ndim=1] py_cord
    cdef np.ndarray[np.float_t, ndim=1] DistWghts
    cdef double udist
    cdef MatrixSize size_x_t,size_y_t
    cdef DTW_path path_t    
    cdef int NFeatDim
    
    # use the number of feature dimension which is lesser of two series. Ideally should have equal dimensions
    NFeatDim = min(x.shape[1], y.shape[1])
    
    size_x_t.Nrow = x.shape[0]
    size_x_t.Ncol = x.shape[1]
    size_y_t.Nrow = y.shape[0]
    size_y_t.Ncol = y.shape[1]  
    
    x_arr = np.ascontiguousarray(x, dtype=np.float)
    y_arr = np.ascontiguousarray(y, dtype=np.float)
    
    DistWghts = np.ascontiguousarray(configuration['Ldistance']['weight'], dtype=np.float)
    px_cord = np.empty(len(path[0]), dtype=np.int32)
    py_cord = np.empty(len(path[0]), dtype=np.int32)
    
    for ind in range(0,len(path[0])):
        px_cord[ind]=path[0][ind]
        py_cord[ind]=path[1][ind]
        #print  px_cord[ind], py_cord[ind]
        
    path_t.px = <int*>px_cord.data
    path_t.py = <int*>py_cord.data
    
    #print path_t.px[1], path_t.px[1]
    
    myconfig_t.DistWghts = <double *>DistWghts.data
    udist = dist4Path(<double *>x_arr.data, <double*>y_arr.data,
                  &size_x_t,&size_y_t,NFeatDim, &path_t, len(path[0]), &myconfig_t)
    
    return udist