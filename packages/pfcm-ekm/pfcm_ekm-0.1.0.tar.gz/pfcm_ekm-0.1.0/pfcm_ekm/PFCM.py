# this source code is a modified version of the original code from https://github.com/IbraDje/PFCM
import numpy as np

def kmeans_plusplus_init(data, c):
    """
    Initialize cluster centers using K-Means++ algorithm
    
    Parameters:
    -----------
    data : array-like, shape (n_samples, n_features)
        Dataset to initialize centers from
    c : int
        Number of clusters
        
    Returns:
    --------
    centers : array, shape (c, n_features)
        Initial cluster centers
    """
    n_samples, n_features = data.shape
    centers = np.zeros((c, n_features))
    
    # Step 1: Choose first center randomly
    centers[0] = data[np.random.randint(n_samples)]
    
    # Step 2: Choose remaining centers
    for i in range(1, c):
        # Calculate distance from each point to nearest center
        distances = np.zeros(n_samples)
        for j in range(n_samples):
            min_dist = float('inf')
            for k in range(i):
                dist = np.sum((data[j] - centers[k]) ** 2)
                if dist < min_dist:
                    min_dist = dist
            distances[j] = min_dist
        
        # Choose next center with probability proportional to distance squared
        probabilities = distances / np.sum(distances)
        cumulative_probs = np.cumsum(probabilities)
        r = np.random.rand()
        for j in range(n_samples):
            if r < cumulative_probs[j]:
                centers[i] = data[j]
                break
    
    return centers


def pfcm(data, c, expo=2, max_iter=1000, min_impro=0.005, a=1, b=4, nc=3, 
         init_method='random', init_centers=None):
    """
    Possiblistic Fuzzy C-Means Clustering Algorithm
    
    Parameters :
    ------------
    `data`: Dataset to be clustered, with size M-by-N,
    where M is the number of data points
    and N is the number of coordinates for each data point.
    `c` : Number of clusters
    `expo` : exponent for the U matrix (default = 2)
    `max_iter` : Maximum number of iterations (default = 1000)
    `min_impro` : Minimum amount of improvement (default = 0.005)
    `a` : User-defined constant a (default = 1)
    `b` : User-defined constant b that should be greater than a (default = 4)
    `nc` : User-defined constant nc (default = 3)
    `init_method` : Initialization method - 'random', 'kmeans++', or 'manual' (default = 'random')
    `init_centers` : Initial cluster centers for manual initialization, shape (c, n_features)
                     Required when init_method='manual', ignored otherwise
    
    The clustering process stops when the maximum number of iterations is
    reached, or when objective function improvement or the maximum centers
    improvement between two consecutive iterations is less
    than the minimum amount specified.
    
    Returns:
    --------
    `cntr` : The clusters centers
    `U` : The C-Partitioned Matrix (used in FCM)
    `T` : The Typicality Matrix (used in PCM)
    `obj_fcn` : The objective function for U and T
    """
    
    obj_fcn = np.zeros(shape=(max_iter, 1))
    ni = np.zeros(shape=(c, data.shape[0]))
    U = initf(c, data.shape[0])
    T = initf(c, data.shape[0])
    
    # Choose initialization method
    if init_method == 'manual':
        if init_centers is None:
            raise ValueError("init_centers must be provided when init_method='manual'")
        if init_centers.shape != (c, data.shape[1]):
            raise ValueError(f"init_centers must have shape ({c}, {data.shape[1]}), got {init_centers.shape}")
        cntr = np.array(init_centers, dtype=float)
    elif init_method == 'kmeans++':
        cntr = kmeans_plusplus_init(data, c)
    elif init_method == 'random':
        cntr = np.random.uniform(low=np.min(data), high=np.max(data), size=(c, data.shape[1]))
    else:
        raise ValueError("init_method must be either 'random', 'kmeans++', or 'manual'")
    
    for i in range(max_iter):
        current_cntr = cntr
        U, T, cntr, obj_fcn[i], ni = pstepfcm(data, cntr, U, T, expo, a, b, nc, ni)
        if i > 1:
            if abs(obj_fcn[i] - obj_fcn[i-1]) < min_impro:
                break
            elif np.max(abs(cntr - current_cntr)) < min_impro:
                break
    return cntr, U, T, obj_fcn


def pstepfcm(data, cntr, U, T, expo, a, b, nc, ni):
    mf = np.power(U, expo)
    tf = np.power(T, nc)
    tfo = np.power((1 - T), nc)
    cntr = (np.dot(a * mf + b * tf, data).T / np.sum(a * mf + b * tf, axis=1).T).T
    dist = pdistfcm(cntr, data)
    obj_fcn = np.sum(np.sum(np.power(dist, 2) * (a * mf + b * tf), axis=0)) + np.sum(ni * np.sum(tfo, axis=0))
    ni = mf * np.power(dist, 2) / (np.sum(mf, axis=0))
    tmp = np.power(dist, (-2/(expo - 1)))
    U = tmp/(np.sum(tmp, axis=0))
    tmpt = np.power((b / ni) * np.power(dist, 2), (1 / (nc - 1)))
    T = 1 / (1 + tmpt)
    return U, T, cntr, obj_fcn, ni


def initf(c, data_n):
    A = np.random.random(size=(c, data_n))
    col_sum = np.sum(A, axis=0)
    return A/col_sum


def pdistfcm(cntr, data):
    out = np.zeros(shape=(cntr.shape[0], data.shape[0]))
    for k in range(cntr.shape[0]):
        out[k] = np.sqrt(np.sum((np.power(data-cntr[k], 2)).T, axis=0)) + 1e-10
    return out


def pfcm_predict(data, cntr, expo=2, a=1, b=4, nc=3):
    """
    Possiblistic Fuzzy C-Means Clustering Prediction Algorithm
    
    Parameters :
    ------------
    `data`: Dataset to be clustered, with size M-by-N, where M is the number of data points 
    and N is the number of coordinates for each data point.
    `cntr` : centers of the dataset previously calculated
    `expo` : exponent for the U matrix (default = 2)
    `a` : User-defined constant a (default = 1)
    `b` : User-defined constant b that should be greater than a (default = 4)
    `nc` : User-defined constant nc (default = 3)
    
    The algorithm predicts which clusters the new dataset belongs to
    
    Returns:
    --------
    `new_cntr` : The new clusters centers
    `U` : The C-Partitioned Matrix (used in FCM)
    `T` : The Typicality Matrix (used in PCM)
    `obj_fcn` : The objective function for U and T
    """

    dist = pdistfcm(cntr, data)
    tmp = np.power(dist, (-2 / (expo - 1)))
    U = tmp / (np.sum(tmp, axis=0))
    mf = np.power(U, expo)
    ni = mf*np.power(dist, 2) / (np.sum(mf, axis=0))
    tmpt = np.power((b / ni) * np.power(dist, 2), (1 / (nc - 1)))
    T = 1 / (1 + tmpt)
    tf = np.power(T, nc)
    tfo = np.power((1 - T), nc)
    new_cntr = (np.dot(a * mf + b * tf, data).T / np.sum(a * mf + b * tf, axis=1).T).T
    obj_fcn = np.sum(np.sum(np.power(dist, 2) * (a * mf + b * tf), axis=0)) + np.sum(ni * np.sum(tfo, axis=0))
    
    return new_cntr, U, T, obj_fcn