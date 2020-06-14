import pandas as pd
import numpy as np


def strided_app(a, L, S): # Window len = L, Stride len/stepsize = S

    nrows = ((a.size - L) // S) + 1

    n = a.strides[0]

    return np.lib.stride_tricks.as_strided(a, shape=(nrows, L), strides=(S * n, n))



def EWMA(array_, windowSize):

    array_ = np.array(array_)
    weights = np.exp(np.linspace(-1., 0., windowSize))

    weights /= weights.sum()

    a2D = strided_app(array_, windowSize, 1)

    returnArray = np.empty((array_.shape[0]))

    returnArray.fill(np.nan)

    for index in (range(a2D.shape[0])):

        returnArray[index + windowSize-1] = np.convolve(weights, a2D[index])[windowSize - 1:-windowSize + 1]

    return np.reshape(returnArray, (-1, 1))[-1][0]