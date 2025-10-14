import math as m
from PIL import Image
import numpy as np

def a_reduce_dim(input):
    output = [0] *( len(input) * len(input[0]) )
    k = 0
    for i in range(0, len(input)):
        for j in range(0, len(input[0])):
            output[k] = input[i][j]
            k += 1
    return output

def normalize(ch_input):
    """
    normalizes an input array according to the rgb linearlization algorithm
    Args:
        ch_input: a 2d array containing pixel values of one rgb channel

    Returns: 
        void

    Dependencies: 
        requires 'pow' module from library 'math' to linearlize bright pixels
    """
    for i in range(0, len(ch_input)):
        for j in range(0, len(ch_input[0])):
            if(ch_input[i][j] <= 0.0405):
                ch_input[i][j] = ch_input[i][j] / 12.92
            else:
                ch_input[i][j] = m.pow( ((ch_input[i][j] + 0.055)/1.055), 2.4 )  

CHANNEL_WEIGHTS = [0.2126, 0.7152, 0.0722]
def rgb_to_grayscale (img_array):  
    """
    converts an array of rgb pixel values into grayscale using the grayscale conversion algorithm
    Args:
        img_array: a 3 dimensional array containing data on the image
                   more specifically, it is a numpy array obtained from calling
                   numpy.asarray on PIL.Image.open, and NOT an appended list of
                   rgb pixel values
    Returns: 
        gray_values: a 2 dimensional array containing grayscale converted pixel values for the image

    Dependencies: 
        reqires module 'Image' from library 'PIL' for valid input data
        requires library 'numpy' for valid input type
    """
    ch_data = [0] * 3
    for i in range(0, len(ch_data)):
        ch_data[i] = img_array[:,:,i] / 255
        normalize(ch_data[i])
        ch_data[i] = ch_data[i] * CHANNEL_WEIGHTS[i]

    gray_values = np.zeros((len(ch_data[0]), len(ch_data[0][0])))

    for i in range(0, len(gray_values)):
        for j in range(0, len(gray_values[0])):
            for k in range(0, len(ch_data)):
                gray_values[i][j] += ch_data[k][i][j] * 255 

    return gray_values

def a_sum(input):
    """
    calculates the sum of an array
    Args:
        input: a one-dimensional array
    Returns: 
        sum: the sum of all values in the array

    Dependencies: 
        None
    """
    sum = 0
    for i in range (0, len(input)):
            sum += input[i]

    return sum

def a_mean(input):
    """
    calculates the mean of an array
    Args:
        input: a one-dimensional array
    Returns: 
        the mean of the one-dimensional array

    Dependencies: 
        None
    """
    return ( a_sum(input) / len(input) )