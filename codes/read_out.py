'''
These functions are taken from RADMC3D in order to read the .out files.

All the credits for this work goes to Dullemond+2018
'''

from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
import glob


class simplereaddataobject(object):
    '''
    Original from RADMC3D.
    Generic data object for the RADMC-3D simpleread.py functions.
    '''
    def __init__(self,datatype):
        self.datatype = datatype


def read_out_image(imagename, indexorder='fortran'):
    '''
    Original from RADMC3D, to read the image.out file.

    Args:
      indexorder: If 'fortran' then converting array to fortran 
                  index order (default). Else use Python/C order.

    Returns:
        Data object containing:
        - freq: Frequency at which the image is taken
        - image: An array with the image intensity in erg/(s.cm^2.Hz.ster)
    '''
    pc        = 3.08572e18     # Parsec                  [cm]
    cc        = 2.99792458e10  # Light speed             [cm/s]
    image     = simplereaddataobject('image')
    fname     = imagename
    print('Reading '+ fname)
    with open(fname, 'r') as rfile:
        dum = ''

        # Format number
        iformat = int(rfile.readline())

        # Nr of pixels
        dum = rfile.readline()
        dum = dum.split()
        image.nx = int(dum[0])
        image.ny = int(dum[1])

        # Nr of frequencies
        image.nfreq = int(rfile.readline())
        image.nwav = image.nfreq

        # Pixel sizes
        dum = rfile.readline()
        dum = dum.split()
        image.sizepix_x = float(dum[0])
        image.sizepix_y = float(dum[1])

        # Wavelength of the image
        image.wav = np.zeros(image.nwav, dtype=np.float64)
        for iwav in range(image.nwav):
            image.wav[iwav] = float(rfile.readline())
        image.freq = cc / image.wav * 1e4

        # Read the rest of the data
        data = np.fromfile(rfile, count=-1, sep=" ", dtype=np.float64)
        
    # Convert the rest of the data to the proper shape
    if iformat == 1:
        # We have a normal total intensity image
        image.stokes = False
        data = np.reshape(data, [image.nfreq, image.ny, image.nx])
        if indexorder=='fortran':
            data = np.swapaxes(data, 0, 2)

    elif iformat == 3:
        # We have the full stokes image
        image.stokes = True
#        data = np.reshape(data, [image.nfreq, 4, image.ny, image.nx])
        data = np.reshape(data, [image.nfreq, image.ny, image.nx, 4])
        if indexorder=='fortran':
            data = np.swapaxes(data, 0, 3)
            data = np.swapaxes(data, 1, 2)
        # Experimental step
        data = np.squeeze(data[0])

    else:
        msg = 'Unknown format number in image.out'
        raise ValueError(msg)

    # Add this to the object
    image.image = data
    
    # Conversion from erg/s/cm/cm/Hz/ster to Jy/pixel
    conv = image.sizepix_x * image.sizepix_y / pc**2. * 1e23
    image.imageJyppix = image.image * conv
    
    # Create the x and y axes in units of cm
    image.x = ((np.arange(image.nx, dtype=np.float64) + 0.5) - image.nx / 2) * image.sizepix_x
    image.y = ((np.arange(image.ny, dtype=np.float64) + 0.5) - image.ny / 2) * image.sizepix_y
    
    # Return object
    return image

