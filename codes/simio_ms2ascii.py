# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
##############################################################################

'''
Max Planck Institute for Astronomy
Planet Genesis Group

Nicolas Kurtovic
Contact: kurtovic at mpia.de
'''

import sys
import os
import numpy as np

# Directories
current_dir = os.getcwd()+'/'
# Check if working at simio or template
if current_dir[-6:] != 'simio/':
    # Modify to get correct simio location
    current_dir += '../../'
# Read the codes directory
sys.path.append(current_dir+'codes/')

# Append ms to ascii functions
execfile(current_dir+'codes/simio_support.py')
# Append cleaning functions
execfile(current_dir+'codes/simio_clean.py')


################################################################################
#                                    FUNCTIONS                                 #
################################################################################


def ms_to_ascii(ms_cont, ascii_file, with_flags):
    '''
    Takes ms_cont, and writes the visibilities in a file named ``ascii_file``.
    The visibility table will have the structure of (u, v, Real, Imag, weights).
    If you do not want to include flagged data in your visibility table, then
    set ``with_flags`` to ``False``.
    This functions averages the two linear polarizations.
    
    Args:
        - ms_cont: (str) Name of the measurement set file from where to
                    extract the visibility table.
        - ascii_file: (str) Name of the ``ascii_file`` where you want to write
                    the visibilities. Must end in ``.txt`` or ``.dat``.
        - with_flags: (bool) ``True`` to extract the visibilities flagged, 
                    ``False`` to exclude them.
    Returns:
        Writes a visibility table with the name of ``ascii_file``.
    '''
    # Use CASA table tools to get columns of UVW, DATA, WEIGHT, etc.
    tb.open(ms_cont)
    data      = tb.getcol("DATA")
    uvw       = tb.getcol("UVW")
    weights   = tb.getcol("WEIGHT")
    wspectrum = tb.getcol("WEIGHT_SPECTRUM")
    ant1      = tb.getcol("ANTENNA1")
    ant2      = tb.getcol("ANTENNA2")
    flags     = tb.getcol("FLAG")
    tb.close()    
    # Use CASA ms tools to get the channel/spw info
    ms.open(ms_cont)
    spw_info = ms.getspectralwindowinfo()
    nchan = spw_info["0"]["NumChan"]
    npol = spw_info["0"]["NumCorr"]
    ms.close()
    # Use CASA table tools to get frequencies
    tb.open(ms_cont+"/SPECTRAL_WINDOW")
    freqs = tb.getcol("CHAN_FREQ")
    tb.close()
    # convert spatial frequencies from m to lambda 
    uu = uvw[0,:]*freqs/qa.constants('c')['value']
    vv = uvw[1,:]*freqs/qa.constants('c')['value']
    Ruv = np.sqrt(uu[0]**2 + vv[0]**2)
    # check to see whether the polarizations are already averaged
    data = np.squeeze(data)
    wspectrum = np.squeeze(wspectrum)
    flags = np.squeeze(flags)
    # 
    if npol==1:
        Re = data.real
        Im = data.imag
        wspec = wspectrum
    # 
    if npol==2:
        # polarization averaging
        Re_xx = data[0,:].real
        Re_yy = data[1,:].real
        Im_xx = data[0,:].imag
        Im_yy = data[1,:].imag
        if nchan==1:
            wspectrum_xx = weights[0,:]
            wspectrum_yy = weights[1,:]
        else:
            wspectrum_xx = wspectrum[0,:,:]
            wspectrum_yy = wspectrum[1,:,:]            
            flags = flags[0,:]*flags[1,:]
            # - weighted averages
        with np.errstate(divide='ignore', invalid='ignore'):
            Re = np.where((wspectrum_xx + wspectrum_yy) != 0, (Re_xx*wspectrum_xx + Re_yy*wspectrum_yy) / (wspectrum_xx + wspectrum_yy), 0.)
            Im = np.where((wspectrum_xx + wspectrum_yy) != 0, (Im_xx*wspectrum_xx + Im_yy*wspectrum_yy) / (wspectrum_xx + wspectrum_yy), 0.)
            wspec = (wspectrum_xx + wspectrum_yy)
    # toss out the autocorrelation placeholders
    xc = np.where(ant1 != ant2)[0]
    # check if there's only a single channel
    # else, make 1-d arrays since channel info is not important now:
    if nchan==1:
        data_real = Re[xc]
        data_imag = Im[xc]
        data_flags = flags[:,xc]
        data_wspec = wspec[xc]
        data_uu = uu[:,xc].flatten()
        data_vv = vv[:,xc].flatten()
    else:
        data_real = Re[:,xc].flatten()
        data_imag = Im[:,xc].flatten()
        data_flags = flags[:,xc].flatten()
        data_wspec = wspec[:,xc].flatten()
        data_uu = uu[:,xc].flatten()
        data_vv = vv[:,xc].flatten()
    # remove flagged data if user wants to:
    if with_flags == False:
        if np.any(data_flags): 
            #print ('flagged data not included!')
            data_uu = data_uu[np.logical_not(data_flags)]
            data_vv = data_vv[np.logical_not(data_flags)]
            data_real = data_real[np.logical_not(data_flags)]
            data_imag = data_imag[np.logical_not(data_flags)]
            data_wspec =data_wspec[np.logical_not(data_flags)]            
    # Write the ascii file (Format will be: u, v, Re, Im, We)
    out_file = ascii_file
    np.savetxt(out_file , np.transpose([data_uu, data_vv, data_real, data_imag, data_wspec]), fmt="%+.15e")


def ascii_to_ms(ascii_file, ms_file, new_ms_file):
    '''
    Inverse function of ms_to_ascii. It takes a visibility table in a ``.txt``
    or ``.dat`` format, and replaces those visibilities in a ms_file. The
    ``ms_file`` must match exactly the visibility table in number of spw and
    channels.
    
    Args:
        - ascii_file: (str) Name of the ascii_file where you want to write the
                    visibilities. Must end in ``.txt`` or ``.dat``
        - ms_file: (str) Path to the original measurement set, from where the
                    ``new_ms_file`` will be copied. This file will not be
                    modified. Both ``ascii file`` and ``ms_file`` must have the
                    same number of visibility measurements.
        - new_ms_file: (str) Name of the new measurement set. It will have the
                    same structure as ``ms_file``, but the visibilities will be
                    written from the ``ascii_file``.
    Returns
        Returns a measurement set with the name of ``new_ms_file``, that
        contains the visibilities of ``ascii_file``.
    '''
    # Read ascii file
    model_uu, model_vv, model_real, model_imag, model_wspec = np.loadtxt(ascii_file,unpack=True)
    # Use CASA table tools to get columns of UVW, DATA, WEIGHT, etc.
    tb.open(ms_file)
    data      = tb.getcol('DATA')
    ant1      = tb.getcol('ANTENNA1')
    ant2      = tb.getcol('ANTENNA2')
    tb.close()
    # Use CASA ms tools to get the channel/spw info
    ms.open(ms_file)
    spw_info = ms.getspectralwindowinfo()
    nchan = spw_info['0']['NumChan']
    npol = spw_info['0']['NumCorr']
    ms.close()
    # Figure out if there is autocorrelation data
    ac = np.where(ant1 == ant2)[0] # autocorrelation
    xc = np.where(ant1 != ant2)[0] # correlation
    # Check that ascii_file data has the same shape as the ms_file data
    if len(model_real) != nchan*len(xc): 
        print ('Problem found, array dimensions do not match!')
        return
    # New data has to have the same shape as original data
    data_array = np.zeros((npol, nchan, ant1.shape[0])).astype(complex)
    # Put the model data on both polarizations
    data_array[0, :, xc] = model_real.reshape(nchan,len(xc)).transpose() + 1j * model_imag.reshape(nchan,len(xc)).transpose()
    data_array[1, :, xc] = model_real.reshape(nchan,len(xc)).transpose() + 1j * model_imag.reshape(nchan,len(xc)).transpose()
    # There is no model for the autocorrelation data
    data_array[0, :, ac] = 0 + 0j
    data_array[1, :, ac] = 0 + 0j
    # Duplicate ms_file and remove any extra columns
    split(vis=ms_file, outputvis=new_ms_file, datacolumn='data')
    tb.open(new_ms_file, nomodify=False)
    tb.putcol('DATA', data_array)
    tb.flush()
    tb.close()
    # Print
    print ('New ms file is: ' + new_ms_file)


def _write_temp_uvtables(simobj):
    '''
    Write the template uvtable. This is wrapper to write the uvtable of the
    ``simio_object`` template, to be used when executing *SIMIO* with
    ``galario``.
    
    Args:
        - simobj: (simio_object) *SIMIO* object containing the synthetic
                    observation that will be extracted.
    Returns:
        Writes the visibility table of each spectral window.
    '''
    # Remove previous existent uvtables
    os.system('rm ' + simobj._source_dir + 'msfiles/'  + simobj._prefix + '_cont_spw*.txt')
    os.system('rm ' + simobj._source_dir + 'uvtables/' + simobj._prefix + '_cont_spw*.txt')
    # Write individual uvtables for each spw
    for i in simobj._spw_temp:
        # Names
        ms_file    = simobj._source_dir + 'msfiles/'  + simobj._prefix + '_cont_spw' + str(i) + '.ms'
        ascii_file = simobj._source_dir + 'uvtables/' + simobj._prefix + '_cont_spw' + str(i) + '.txt'
        # Delete any previous spw file
        os.system('rm -rf ' + ms_file)
        os.system('rm -rf ' + ascii_file)
        # Split
        split(vis=simobj._ms_temp, outputvis=ms_file, \
              keepflags=False, datacolumn='data', spw=i)
        ms_to_ascii(ms_file, ascii_file, with_flags=True)
        # Delete temporal msfile
        os.system('rm -rf ' + ms_file)
    # Check weight
    os.system('du -h ' + simobj._source_dir + 'uvtables')


def _write_mod_uvtables(simobj):
    '''
    Writes the uvtables of the model in ``simio_object``. This function is
    written to work with the ``galario`` mode of ``simio_object``.
    
    Args:
        - simobj: (simio_object) *SIMIO* object containing the synthetic
                    observation that will be written.
    Returns:
        Writes the visibility table of each spectral window, with the
        visibilities from the model.
    '''
    # Iterate over all spws
    for i in simobj._spw_temp.astype(str):
        print (i)
        # Read uvtable from individual spw
        ascii_file = simobj._source_dir + 'uvtables/' + simobj._prefix + '_cont_spw'+str(i)+'.txt'
        uu, vv, RReal, IImag, WWei = np.loadtxt(ascii_file, unpack=True)
        # C-contiguous
        uu = np.ascontiguousarray(uu)
        vv = np.ascontiguousarray(vv)
        RReal = np.ascontiguousarray(RReal)
        IImag = np.ascontiguousarray(IImag)
        WWei = np.ascontiguousarray(WWei)
        # Get model visibilities            
        model_vis = uvmodel_from_image(model_image = simobj.sim_im.scaled_model_im, \
                                       u=uu, v=vv, \
                                       real_part=RReal, imag_part=IImag, \
                                       params = simobj._geom_params, \
                                       px = simobj.sim_im.pxsize_arcsec)
        # Save model and residuals
        model_file = simobj._source_dir + 'uvtables/' + simobj._prefix + '_model_spw' + str(i) + '.txt'
        # Write model
        np.savetxt(model_file, np.array([uu, vv, \
                                         model_vis.real, \
                                         model_vis.imag, \
                                         WWei]).T)


def _write_mod_ms(simobj):
    '''
    After writing the uvtables of the model using the ``_write_mod_uvtables``
    function, this function takes them and converts them in msfiles, to generate
    the msfile of the simio_object model. This function is used then *SIMIO* is
    calculating the fourier transform with galario.
    '''
    # List for storing the names of auxiliary ms files
    list_model = []
    # Generate ms files from ascii tables
    for i in simobj._spw_temp:
        # Names
        ms_file     = simobj._source_dir + 'msfiles/'  + simobj._prefix + '_cont_spw'  + str(i) + '.ms'
        ms_file_new = simobj._source_dir + 'msfiles/'  + simobj._prefix + '_model_spw' + str(i) + '.ms'
        ascii_file  = simobj._source_dir + 'uvtables/' + simobj._prefix + '_model_spw' + str(i) + '.txt'
        list_model.append(ms_file_new)
        os.system('rm -rf '+ms_file)
        os.system('rm -rf '+ms_file_new)
        # Split
        split(vis=simobj._ms_temp, outputvis=ms_file, \
              keepflags=False, datacolumn='data', spw=i)
        ascii_to_ms(ascii_file, ms_file, ms_file_new)
        os.system('rm -rf '+ms_file)
        os.system('rm -rf '+ascii_file)
    # Rejoin best uvmodel
    ms_model = simobj._prefix + '_model'
    os.system('rm -rf '+ simobj._source_dir + 'msfiles/' + ms_model + '.ms')
    concat(vis = list_model, \
           concatvis=simobj._source_dir + 'msfiles/' + ms_model + '.ms', \
           dirtol = '0.1arcsec', copypointing = False)
    # Remove indermediate files
    for i in list_model:
        os.system('rm -rf ' + i)


def get_mod_ms(simobj, generate_ms=True):
    '''    
    Generates the model measurement set file for the ``simobj``. If the
    parameter ``generate_ms`` is set to ``False``, then the function will only
    return the string of the ms file path, but not generate the ms file itself.

    ..warning:: Use it if you want to calculate the visibilities with galario.

    Args:
        - simobj: (simio_object) **SIMIO** object containing the information of
                    the synthetic observation that will be generated.
        - generate_ms: (bool) Set to ``True`` if the measurement set is to be 
                    generated. Set to ``False`` if only the string with the name
                    of the measurement set is needed.
                    Default: ``True``.
    Returns:
        - mod_ms: Name of the measurement set with the synthetic observation.
    '''
    # Check if ms has to be generated
    simobj.mod_ms = simobj._source_dir + 'msfiles/' + simobj._prefix + '_model.ms'
    if not generate_ms:
        return simobj.mod_ms
    # If ms has to be generated:
    # Write template uvtables
    print (' ')
    print ('Getting visibilities from template')
    print (' ')
    _write_temp_uvtables(simobj)
    # Write source uvtables
    print (' ')
    print ('Writing uv-model for: ', simobj._prefix, ' based on ', simobj.template)
    print (' ')
    _write_mod_uvtables(simobj)
    # From source uvtables, write and concatenate the ms files
    print (' ')
    print ('Writing the ms file of the model')
    print (' ')
    _write_mod_ms(simobj)
    # Create a single uvtable for the model
    aux_str1 = simobj._source_dir + 'uvtables/' + simobj._prefix + '_model_spw*.txt'
    aux_str2 = simobj._source_dir + 'uvtables/' + simobj._prefix + '_uvtable.txt'
    os.system('rm ' + simobj._source_dir + 'uvtables/' + simobj._prefix + '_uvtable.txt')
    os.system('ls -1tr ' + aux_str1 + ' | xargs cat >> ' + aux_str2)
    # Remove individual spw files
    os.system('rm ' + simobj._source_dir + 'uvtables/' + simobj._prefix + '_model_spw*.txt')
    os.system('rm ' + simobj._source_dir + 'uvtables/' + simobj._prefix + '_cont_spw*.txt')
    # Return message
    print (simobj._prefix + 'ms file and uvtable are written')
    return simobj.mod_ms


def get_mod_ms_ft(simobj, generate_ms=True):
    '''
    Generates the model ms file for the simobj. If generate_ms is set to
    ``False``, then the function will only return the string of the ms file
    path, but not generate the ms file itself.
    
    ..warning:: Use it if you want to calculate the visibilities with ``CASA``
                ft.
    
    Args:
        - simobj: (simio_object) **SIMIO** object containing the information of
                    the synthetic observation that will be generated.
        - generate_ms: (bool) Set to ``True`` if the measurement set is to be 
                    generated. Set to ``False`` if only the string with the name
                    of the measurement set is needed.
                    Default: ``True``.
    Returns:
        - mod_ms: Name of the measurement set with the synthetic observation.
    '''
    # Check if ms has to be generated
    simobj.mod_ms = simobj._source_dir + 'msfiles/' + simobj._prefix + '_model.ms'
    if not generate_ms:
        return simobj.mod_ms
    # Read image and generate model file
    im_dotmodel = create_dotmodel(simobj)
    print (' ')
    print (' The model visibilities are calculated from '+im_dotmodel)
    print (' ')
    # List for storing the names of auxiliary ms files
    list_model = []
    # Generate ms files from ascii tables
    for i in simobj._spw_temp:
        # Names
        ms_file     = simobj._source_dir + 'msfiles/'  + simobj._prefix + '_cont_spw'  + str(i) + '.ms'
        ms_file_new = simobj._source_dir + 'msfiles/'  + simobj._prefix + '_model_spw' + str(i) + '.ms'
        ascii_file  = simobj._source_dir + 'uvtables/' + simobj._prefix + '_model_spw' + str(i) + '.txt'
        list_model.append(ms_file_new)
        os.system('rm -rf '+ms_file)
        os.system('rm -rf '+ms_file_new)
        # Split
        split(vis=simobj._ms_temp, outputvis=ms_file, \
              keepflags=True, datacolumn='data', spw=i)
        # Change geometry to calculate visibilities
        change_geom(ms_file=ms_file, inc=simobj.inc, pa=simobj.pa, \
                    dRa=simobj.dRa, dDec=simobj.dDec, \
                    datacolumn1='DATA', datacolumn2='DATA', inverse=False)
        # Calculate fourier transform
        ft(vis=ms_file, spw='0', model=im_dotmodel, usescratch=True)
        # Change geometry back
        change_geom(ms_file=ms_file, inc=simobj.inc, pa=simobj.pa, \
                    dRa=simobj.dRa, dDec=simobj.dDec, \
                    datacolumn1='MODEL_DATA', datacolumn2='MODEL_DATA', inverse=True)
        # Pass model column to data column
        split(vis=ms_file, outputvis=ms_file_new, \
              keepflags=True, datacolumn='model')
        # Remove intermediate file
        os.system('rm -rf '+ms_file)
    # Rejoin best uvmodel
    ms_model = simobj._prefix + '_model'
    os.system('rm -rf '+ simobj._source_dir + 'msfiles/' + ms_model + '.ms')
    concat(vis = list_model, \
           concatvis=simobj._source_dir + 'msfiles/' + ms_model + '.ms', \
           dirtol = '0.1arcsec', copypointing = False)
    # Remove indermediate files
    for i in list_model:
        os.system('rm -rf ' + i)
    # Return name
    return simobj.mod_ms


def change_geom(ms_file, inc=0., pa=0., dRa=0., dDec=0., \
                datacolumn1='DATA', datacolumn2='DATA', inverse=False):
    '''
    Changes the geometry of an observation, by inclining and rotating the
    uv-points themselfs. This function modifies the input ``ms_file``.
    
    Args:
        - ms_file: (str) Name of the measurement set you want to incline, rotate
                    or shift in physical space.
        - inc:  (float) Inclination, in **degrees**. Default: 0.
        - pa: (float) Position angle, measured from north to east,
                    in **degrees**. Default: 0.
        - dRa: (float) Shift in RA to be applied to the visibilities,
                    in **arcsec**. Default: 0.
        - dDec: (float) Shift in Dec to be applied to the visibilities.
                    in **arcsec**. Default: 0.
        - datacolumn1: 'DATA' or 'MODEL_DATA', column from where the data must
                       be read. Default: 'DATA'.
        - datacolumn1: 'DATA' or 'MODEL_DATA', column from where the data must
                       be written. Default:'DATA'
        - inverse (bool): Set ``False`` to deproject, or ``False`` to project.
                        Default: ``False``
    Returns:
        Returns ``True`` if everything worked correctly. The ``ms_file`` will
        have been modified.
    '''
    # Use CASA table tools to get columns of UVW, DATA, WEIGHT, etc.
    tb.open(ms_file)
    data      = tb.getcol(datacolumn1)
    uvw       = tb.getcol('UVW')
    weights   = tb.getcol('WEIGHT')
    wspectrum = tb.getcol('WEIGHT_SPECTRUM')
    ant1      = tb.getcol('ANTENNA1')
    ant2      = tb.getcol('ANTENNA2')
    flags     = tb.getcol('FLAG')
    tb.close()
    # Use CASA ms tools to get the channel/spw info
    ms.open(ms_file)
    spw_info = ms.getspectralwindowinfo()
    nchan = spw_info['0']['NumChan']
    npol = spw_info['0']['NumCorr']
    ms.close()
    # Use CASA table tools to get frequencies
    tb.open(ms_file+'/SPECTRAL_WINDOW')
    freqs = tb.getcol('CHAN_FREQ')
    tb.close()
    # convert spatial frequencies from m to lambda 
    uu = uvw[0,:]*freqs/qa.constants('c')['value']
    vv = uvw[1,:]*freqs/qa.constants('c')['value']
    # check to see whether the polarizations are already averaged
    data = np.squeeze(data)
    wspectrum = np.squeeze(wspectrum)
    flags = np.squeeze(flags)
    
    if npol==1:
        Re = data.real
        Im = data.imag
        wspec = wspectrum
    else:
        # polarization averaging
        Re_xx = data[0,:].real
        Re_yy = data[1,:].real
        Im_xx = data[0,:].imag
        Im_yy = data[1,:].imag
        if nchan==1:
            wspectrum_xx = weights[0,:]
            wspectrum_yy = weights[1,:]
        else:
            wspectrum_xx = wspectrum[0,:,:]
            wspectrum_yy = wspectrum[1,:,:]            
            flags = flags[0,:]*flags[1,:]
            # - weighted averages
        with np.errstate(divide='ignore', invalid='ignore'):
            Re = np.where((wspectrum_xx + wspectrum_yy) != 0, (Re_xx*wspectrum_xx + Re_yy*wspectrum_yy) / (wspectrum_xx + wspectrum_yy), 0.)
            Im = np.where((wspectrum_xx + wspectrum_yy) != 0, (Im_xx*wspectrum_xx + Im_yy*wspectrum_yy) / (wspectrum_xx + wspectrum_yy), 0.)
            wspec = (wspectrum_xx + wspectrum_yy)
    # Figure out if there is autocorrelation data
    ac = np.where(ant1 == ant2)[0] # autocorrelation
    xc = np.where(ant1 != ant2)[0] # correlation
    # check if there's only a single channel
    if nchan==1:
        data_real = Re[xc]
        data_imag = Im[xc]
        data_flags = flags[:,xc]
        data_wspec = wspec[xc]
        data_uu = uu[:,xc].flatten()
        data_vv = vv[:,xc].flatten()
    else:
        data_real = Re[:,xc].flatten()
        data_imag = Im[:,xc].flatten()
        data_flags = flags[:,xc].flatten()
        data_wspec = wspec[:,xc].flatten()
        data_uu = uu[:,xc].flatten()
        data_vv = vv[:,xc].flatten()
    # remove flagged data if user wants to:
#    if np.any(data_flags):
#        data_uu = data_uu[np.logical_not(data_flags)]
#        data_vv = data_vv[np.logical_not(data_flags)]
#        data_real = data_real[np.logical_not(data_flags)]
#        data_imag = data_imag[np.logical_not(data_flags)]
#        data_wspec =data_wspec[np.logical_not(data_flags)]

    # Deproject data
    dep_u, dep_v, dep_re, dep_im = deproject_uv(data_uu, data_vv, data_real, data_imag, inc, pa, dRa, dDec, inverse=inverse)
    # Return u and v to input units
    dep_u = dep_u / freqs * qa.constants('c')['value']
    dep_v = dep_v / freqs * qa.constants('c')['value']
    # Create new uvw array
    new_uvw = np.array([dep_u[0], dep_v[0], uvw[2]])
    # New data has to have the same shape as original data
    data_array = np.zeros((npol, nchan, ant1.shape[0])).astype(complex)
    # Put the model data on both polarizations
    data_array[0, :, xc] = dep_re.reshape(nchan,ant1.shape[0]).transpose() + 1j * dep_im.reshape(nchan,ant1.shape[0]).transpose()
    data_array[1, :, xc] = dep_re.reshape(nchan,ant1.shape[0]).transpose() + 1j * dep_im.reshape(nchan,ant1.shape[0]).transpose()
    # There is no model for the autocorrelation data
    data_array[0, :, ac] = 0 + 0j
    data_array[1, :, ac] = 0 + 0j
    # Add the new data to the ms_file
    tb.open(ms_file, nomodify=False)
    tb.putcol(datacolumn2, data_array)
    tb.flush()
    tb.close()
    # Add the new uv-points
    tb.open(ms_file, nomodify=False)
    tb.putcol('UVW', new_uvw)
    tb.flush()
    tb.close()
    # Return
    return True


