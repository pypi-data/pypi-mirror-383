import secrets
import numpy as np

def uniform(a: float = 0.0, b: float = 1.0) -> float:
    """
    Cryptographically secure uniform sample.
    """
    # 53 random bits gives 53-bit precision double
    u = secrets.randbits(53) / (1 << 53) # in [0, 1)
    return a + (b - a) * u



def exponentialdist(lmda, n):
    '''
    Take lambda as a inpute, and return a random sample that is exponentially distributed.

    Input: -> lambda. // coefficient
           -> n. // number of samples
    Output: -> expinetial distirbution samples
    '''

    u = [] # list for uniform returns

    # first check the lambda, make sure lambda is greater than 0
    if lmda <= 0:
        return ValueError("Lambda must greater than 0")
    
    # uniform distribution simulation
    for i in range(n):
        u.append(uniform())

    # calculate the inverse sampling
    x = (- 1 / lmda) * np.log(np.array(u))

    return x


def poissiondist(lmda, n):
    '''
    Take lambda and n as input, and return a random sample that is poission distributed

    Input: -> lambda. // coefficenet
           -> n. // number of samples
    Output: -> poission distribution samples
    '''
    x = []

    # first check the lambda, make sure lambda is greater than 0
    if lmda <= 0:
        return ValueError("Lambda must greater than 0")
    
    # for poission distribution, due to the descrete, we have to use this formula: 
    # F^{-1}(u) = min{x; F(x) >= u}, u \in [0, 1]

    for i in range(n):
        # get the unifrom returns
        u = uniform()
        F0 = np.exp(-lmda) # if k = 0, the CDF is e^{-lambda}
        p = np.exp(-lmda) # lambda^{k}e^{-lambda} / lambda!
        k = 0

        # get the samples
        while u > F0:
            k += 1
            p *= lmda / k
            F0 += p
        x.append(k)
    
    return np.array(x)