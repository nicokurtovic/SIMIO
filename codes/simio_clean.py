# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
##############################################################################

'''
Max Planck Institute for Astronomy
Planet Genesis Group

Nicolas Kurtovic
Contact: kurtovic at mpia.de

This file contains a compilation of functions from reduction_utils.py from
DSHARP (Andrews et al. 2018) and JvM correction from MAPS (Czekala et al. 2021):
https://almascience.eso.org/almadata/lp/DSHARP/scripts/reduction_utils.py
https://github.com/ryanaloomis/beams_and_weighting
'''

import numpy as np
import shutil

################################################################################
#                                    FUNCTIONS                                 #
################################################################################


def delete_wrapper(imagename):
    '''
    Wrapper to delete the images generated by tclean.
    
    Args:
        - imagename: (str) Base name for the images to be deleted.
    '''
    print (' ')
    print ('Removing previous imaging files')
    print (' ')
    sufix = ['.image', '.mask', '.model', '.pb', \
             '.psf', '.residual', '.sumwt']
    for ext in sufix:
        os.system('rm -rf '+ imagename + '*' + ext)
        print (imagename + ext + ' deleted')


def tclean_wrapper(vis, imagename, scales, smallscalebias=0.6, mask ='', \
                   threshold='0.2mJy', spw='', imsize=3000, cellsize='0.01arcsec', \
                   interactive=False, robust=0.5, gain=0.3, niter=50000, \
                   cycleniter=300, cyclefactor=1., uvtaper=[], phasecenter=0, \
                   startmodel='', savemodel='none', uvrange='', field='', nterms=1):
    '''
    Wrapper for tclean with keywords set to values desired for the DSHARP Large 
    Program imaging. Modified to work within SIMIO with a greater free
    parameter freedom.
    See the CASA documentation for tclean to get the definitions of all
    the parameters not defined in the following list.

    Args:
        - vis: (str) Path to the measurement set to be imaged.
        - imagename: (str) Base name for the images.
        - scales: (list of ints) Scales for multiscale parameter
    '''
    
    if phasecenter is 0:
        myms = au.createCasaTool(msmdtool)
        myms.open(vis)
        mydir = myms.phasecenter(phasecenter)
        ra = mydir['m0']['value']
        dec = mydir['m1']['value']
        myms.close()
        phasecenter = au.rad2radec(ra,dec, prec=7, verbose=False)
        phasecenter = phasecenter.replace(':','h',1).replace(':','m',1).replace(':','d',1).replace(':','m',1) + 's'
        phasecenter = phasecenter.replace(',', 's')
        #phasecenter = 'J2000 '+phasecenter

    print (' ')
    print ('Removing previous imaging files, and starting first tclean.')
    print (' ')
    
    sufix = ['.image', '.mask', '.model', '.pb', \
             '.psf', '.residual', '.sumwt']
    for ext in sufix:
        os.system('rm -rf '+ imagename + ext)
    tclean(vis= vis, 
           imagename = imagename, 
           spw = spw, 
           field = field, 
           specmode = 'mfs', 
           deconvolver = 'multiscale',
           scales = scales, 
           weighting='briggs', 
           robust = robust,
           phasecenter=phasecenter, 
           gain = gain,
           imsize = imsize,
           cell = cellsize, 
           smallscalebias = smallscalebias, #set to CASA's default of 0.6
           niter = niter, #we want to end on the threshold
           interactive = interactive,
           threshold = threshold,
           cycleniter = cycleniter,
           cyclefactor = cyclefactor, 
           uvtaper = uvtaper, 
           mask = mask,
           savemodel = savemodel,
           startmodel = startmodel,
           uvrange=uvrange, 
           nterms = nterms)
    # This step is a workaround a bug in tclean that doesn't always save the 
    # model during multiscale clean. See the "Known Issues" section for
    # CASA 5.1.1 on NRAO's website
    if savemodel=='modelcolumn':
          print (' ')
          print ('Running tclean a second time to save the model.')
          print (' ')
          tclean(vis= vis, 
                 imagename = imagename, 
                 spw=spw, 
                 field = field, 
                 specmode = 'mfs', 
                 deconvolver = 'multiscale',
                 scales = scales, 
                 weighting='briggs', 
                 robust = robust,
                 gain = gain,
                 imsize = imsize,
                 cell = cellsize, 
                 smallscalebias = smallscalebias, 
                 niter = 0, 
                 phasecenter = phasecenter, 
                 interactive = False,
                 threshold = threshold,    
                 cycleniter = cycleniter,
                 cyclefactor = 1, 
                 uvtaper = uvtaper, 
                 mask = '',
                 savemodel = savemodel,
                 calcres = False,
                 calcpsf = False,
                 uvrange=uvrange, 
                 nterms = nterms)


def estimate_SNR(imagename, disk_mask, noise_mask):
    '''
    Original from DSHARP.
    Estimate peak SNR of source, given a mask that encompasses the emission
    and another annulus mask to calculate the noise properties.
    
    Args:
        - imagename: (str) Image name ending in '.image'.
        - disk_mask: (str) must be a CASA region format.
        - noise_mask: (str) Annulus to measure image rms, in the CASA region 
                  format.
                  e.g. 'annulus[['0arcsec', '0arcsec'],['1arcsec', '2arcsec']]'.
    '''
    headerlist = imhead(imagename, mode = 'list')
    beammajor = headerlist['beammajor']['value']
    beamminor = headerlist['beamminor']['value']
    beampa = headerlist['beampa']['value']
    print ("#%s" % imagename)
    print ("#Beam %.3f arcsec x %.3f arcsec (%.2f deg)" % (beammajor, \
                                                           beamminor, beampa))
    disk_stats = imstat(imagename = imagename, region = disk_mask)
    disk_flux = disk_stats['flux'][0]
    print ("#Flux inside disk mask: %.2f mJy" % (disk_flux*1000,))
    peak_intensity = disk_stats['max'][0]
    print ("#Peak intensity of source: %.2f mJy/beam" % (peak_intensity*1000,))
    rms = imstat(imagename = imagename, region = noise_mask)['rms'][0]
    print ("#rms: %.2e mJy/beam" % (rms*1000,))
    SNR = peak_intensity/rms
    print ("#Peak SNR: %.2f" % (SNR,))


def write_fits(im_base_name):
    '''
    Given the im_base_name from tclean, it takes the products and write fits
    files of them.
    
    Args:
        - im_base_name: (str) Base name for the images to be written in fits
                        format.
    '''
    # No JvM corrected image
    exportfits(imagename=im_base_name+'.image', \
               fitsimage=im_base_name+'_noJvM.fits', \
               history=False, overwrite=True)
    # JvM corrected, nominal angular resolution
    exportfits(imagename=im_base_name+'.JvMcorr.image', \
               fitsimage=im_base_name+'.fits', \
               history=False, overwrite=True)
    # CLEAN model
    exportfits(imagename=im_base_name+'.model', \
               fitsimage=im_base_name+'_model.fits', \
               history=False, overwrite=True)
    # CLEAN residuals
    exportfits(imagename=im_base_name+'.residual', \
               fitsimage=im_base_name+'_residual.fits', \
               history=False, overwrite=True)
    # CLEAN psf
    exportfits(imagename=im_base_name+'.psf', \
               fitsimage=im_base_name+'_psf.fits', \
               history=False, overwrite=True)


def print_fits(im_base_name):
    '''
    Given the im_base_name from tclean, prints the fits files names.
    
    Args:
        - im_base_name: (str) Base name for the images names to be printed
    '''
    # Print
    print (' ')
    print ('The following fits files were written:')
    print (' ')
    print (im_base_name+'.fits')
    print (im_base_name+'_noJvM.fits')
    print (im_base_name+'.JvMcorr_lowres.fits')
    print (im_base_name+'_model.fits')
    print (im_base_name+'_residual.fits')
    print (im_base_name+'_psf.fits')    
    print (' ')


def easy_mod_tclean(simobj, interactive=False, remove_end=True, \
                    manual_threshold=str(2.4e-02)+'mJy'):
    '''
    Function wrapper of tclean, estimate SNR, JvM correction and delete wrapper.
    It uses the values from the template and simobj to fill the tclean wrapper.
    For a more customized clean, see 'custom_clean' function.

    Args:
        - simobj: (simio_object) A simio object that already went through
                  the 'get_mod_ms' function.
        - interactive: (boolean) Interactive clean. Recommended to set ``True``.
                  Default: ``False``
        - remove_end: (Boolean) If ``True``, will remove the folder files after
                  finishing the imaging.
                  Default: ``True``
        - manual_threshold: Set the threshold for tclean. By default it cleans to
                  2sigma of DSHARP-like rms.
                  Default: '2.4e-02mJy'
    '''
    # Check if simobj has ms
    try:
        print (' ')
        print ('Cleaning '+simobj.mod_ms)
        print (' ')
    except:
        print (' ')
        print (' You must run get_mod_ms(simobj) before')
        print (' executing easy_mod_tclean')
        print (' ')
        return 0
    # Base name
    im_base_name = simobj._source_dir + 'images/' + simobj._prefix + '_im'
    # Check if a mask exists
    try:
        _ = simobj.mask_obj
    except:
        print (' ')
        print (' Create a mask for your simio_object before')
        print (' executing easy_mod_tclean')
        print (' ')
        return 0    
    # tclean
    tclean_wrapper(vis=simobj.mod_ms, \
                   imagename=im_base_name, \
                   imsize=simobj._clean_imsize, \
                   cellsize=simobj._clean_cellsize, \
                   mask=simobj.mask_obj, \
                   scales=[0, 4, 8, 24], \
                   robust=simobj._clean_robust, \
                   gain=0.06, \
                   smallscalebias=0.50, \
                   cyclefactor=1.75, \
                   threshold=manual_threshold, \
                   savemodel='modelcolumn', \
                   niter=15000, \
                   interactive=interactive)
    # Apply JvM correction
    epsilon = JvM_correction(im_base_name)
    # Print estimate S/N
    print (' ')
    estimate_SNR(im_base_name + '.image', \
                 disk_mask = simobj.mask_obj, \
                 noise_mask = simobj.res_mask_obj)
    print ('#Epsilon: '+str(epsilon))
    print (' ')
    # Export to fits
    write_fits(im_base_name)
    # Print names
    print_fits(im_base_name)
    # Remove folder files
    if remove_end:
        delete_wrapper(im_base_name)
    # Return True
    return 1


def custom_tclean(simobj, imsize, cellsize, robust, mask, threshold, \
                  scales=[0, 3, 8], gain=0.05, smallscalebias=0.45, \
                  cyclefactor=1.75, niter=10000, imagename=None, \
                  interactive=False, remove_end=True):
    '''
    Function wrapper of tclean, estimate SNR, JvM correction and delete wrapper.
    It allows for a more customized clean compared to easy_mod_tclean.
    For more details on some of these parameters, check the tclean task in:
    https://casa.nrao.edu/docs/taskref/tclean-task.html

    Args:
        - simobj: (simio_object) A simio object that already went through
                    the 'get_mod_ms' function.
        - imsize: (int) Image size in pixels.
        - cellsize: (float) Pixel size, must be input in arcsec.
        - mask: (str) Mask for cleaning the emission, must be a CASA region
                    format.
        - threshold: (float) Threshold for how deep the CLEAN should go, in mJy.
                    For JvM corrected images, set the threshold to be 4 times
                    the rms of the image.
                    For model comparison with other models, you should clean up
                    to 2 or 1 sigma.
        - scales: (list of int) Scales to use in multiscale, in pixels.
                    Default: [0, 3, 8]
        - gain: (float) Fraction of the source flux to subtract out of the
                    residual image for the CLEAN algorithm.
                    Default: 0.05
        - smallscalebias: (float) Controls the bias towards smaller scales.
                    Default: 0.45
        - cyclefactor: (float) Computes the minor-cycle stopping threshold.
                    Default: 1.75
        - niter: (int) Total number of iterations.
                    Default: 10000
        - imagename: (str) Sufix name for the images, it will be saved in the
                    same folder as in default.
                    Default: None
        - interactive: (boolean) Interactive clean. Recommended to set ``True``.
                    Default: ``False``
        - remove_end: (boolean) If ``True``, will remove the folder files after
                    finishing the imaging.
                    Default: None
    '''
    # If imagename was not input, use nominal
    if imagename is None:
        imagename = simobj._source_dir + 'images/' + simobj._prefix + '_custom_im'
    else:
        imagename = simobj._source_dir + 'images/' + imagename
    # Run tclean
    tclean_wrapper(vis=simobj.mod_ms, \
                   imagename=imagename, \
                   imsize=imsize, \
                   cellsize=str(cellsize)+'arcsec', \
                   mask=mask, \
                   scales=scales, \
                   robust=robust, \
                   gain=gain, \
                   smallscalebias=smallscalebias, \
                   cyclefactor=cyclefactor, \
                   threshold=str(threshold)+'mJy', \
                   savemodel='modelcolumn', \
                   niter=niter, \
                   interactive=interactive)
    # Apply JvM correction
    epsilon = JvM_correction(imagename)
    # Print estimate S/N
    print (' ')
    estimate_SNR(imagename+'.image', \
                 disk_mask = mask, \
                 noise_mask = simobj.res_mask_obj)
    print ('#Epsilon: ', epsilon)
    print (' ')
    # Export to fits
    write_fits(imagename)
    # Print names
    print_fits(imagename)
    # Remove folder files
    if remove_end:
        delete_wrapper(im_base_name)


def create_dotmodel(simobj, imagename=None):
    '''
    Function to create a .model image that mimics the .out, with the coordinate
    information of the template.

    Args:
        - simobj: (simio_object) SIMIO object that will be used to generate the
                    synthetic observation.
        - imagename: (str) Name of the image model to be generated.
    Returns:
        - (str) with the name of the .model image generated.
    '''
    # If imagename was not input, use nominal
    if imagename is None:
        imagename = simobj._source_dir + 'images/' + simobj._prefix + '_orig_model_im'
    else:
        imagename = simobj._source_dir + 'images/' + imagename
    # Remove all previous files
    sufix = ['.image', '.mask', '.model', '.pb', \
             '.psf', '.residual', '.sumwt']
    for ext in sufix:
        os.system('rm -rf '+ imagename + '*' + ext)
    # Run tclean to generate images with exact pixel size and coordinate system
    tclean(vis=simobj._ms_temp, \
           imagename=imagename, \
           robust = 0.5, \
           imsize=simobj.sim_im.imsize, \
           cell=str(simobj.sim_im.pxsize_arcsec)+'arcsec', \
           niter = 0, \
           threshold = '1mJy', \
           interactive = False)
    # Remove all the files that are not .image
    sufix = ['.mask', '.model', '.pb', 'fits', \
             '.psf', '.residual', '.sumwt']
    for ext in sufix:
        os.system('rm -rf '+ imagename + '*' + ext)
    # Read the coordinate system of the template model
    ia.open(imagename+'.image')
    coord_sys = ia.coordsys()
    shape_mod = ia.shape()
    ia.close()
    # Create a .model with the simio model
    os.system('rm -rf '+imagename+'.model')
    ia.fromarray(outfile=imagename+'.model', \
                 pixels=np.array([[simobj.sim_im.scaled_model_im]]).reshape(shape_mod), \
                 csys=coord_sys.torecord(), \
                 overwrite=True)
    ia.close()
    # Remove intermediate file
    os.system('rm -rf '+imagename+'.image')
    # Save model to fits file
    exportfits(imagename=imagename+'.model', \
               fitsimage=imagename+'.fits', \
               history=False, overwrite=True)
    # Add model information to simio object
    simobj.ft_model_name = imagename+'.model'
    # Return
    return imagename+'.model'


def add_noise(mod_ms, level='10.2mJy'):
    '''
    Wrapper for sm.setnoise from CASA. This function receives the name of
    the model measurement set in (mod_ms from SIMIO tutorials), and returns
    a measurement set with the same name, but with added simple thermal noise.
    
    ..warning: The noise level in the measurement set will not be the same as
                    you input in ``level``. After succesful execution, generate
                    an image to measure the noise level in the residuals image,
                    and then run SIMIO again to iteratively find the correct
                    ``level`` for the noise desired.
    
    Args:
        - mod_ms: (str) Name of the measurement set to be modified.
        - level: (str) Level of noise to be given to ``sm.setnoise``, and
                    passed directly to ``simplenoise``.
    Returns:
        - (int) Returns 1 if everything worked correctly. The noiseless
                    measurement set will be copied into a file with the same
                    name but ending in '_no_noise.ms', while the ``mod_ms``
                    file will be modified to include the requested 
                    noise.
    '''
    # Corrupt
    os.system('cp -rf '+mod_ms+' '+mod_ms[:-3]+'.no_noise.ms')
    os.system('rm -rf '+mod_ms)
    os.system('cp -rf '+mod_ms[:-3]+'.no_noise.ms '+mod_ms)
    sm.openfromms(mod_ms)
    sm.setnoise(mode='simplenoise', \
                simplenoise=level)
    sm.corrupt()
    sm.done()
    # Print names
    print (' Noise was added to:')
    print ('   '+mod_ms)
    print (' ')
    print (' The noiseless measurement set was renamed to:')
    print ('   '+mod_ms[:-3]+'.no_noise.ms')
    print (' ')
    print (' If you image with easy_mod_tclean, the default measurement set')
    print (' to image will be the observation with noise.')
    print (' ')
    print (' After generating the images, check the residuals image to ')
    print (' measure the noise level.')
    print (' ')
    # Return True
    return 1


def gaussian_eval(params, data, center):
    '''
    Original from MAPS codes.
    Returns a 2D gaussian with the given parameters. Made for JvM correction.
    Please, also refer to Czekala et al. (2021) for reference.
    '''
    width_x, width_y, rotation = params
    rotation = 90 - rotation
    width_x = float(width_x)
    width_y = float(width_y)
    rotation = np.deg2rad(rotation)
    x, y = np.indices(data.shape) - center
    xp = x * np.cos(rotation) - y * np.sin(rotation)
    yp = x * np.sin(rotation) + y * np.cos(rotation)
    g = 1. * np.exp( -( (xp / width_x)**2 + (yp / width_y)**2 ) / 2.)
    return g


def JvM_correction(root):
    '''
    Original from MAPS codes.
    JvM correction. Check ALMA MAPS Large Program codes for more detailed
    explanation. Please, also refer to Czekala et al. (2021) for reference.
    '''
    # Get the psf file to fit
    psf_file = root + '.psf'
    model_file = root + '.model'
    residual_file = root + '.residual'
    npix_window = 301
    # Open psf and read off the metadata
#    ia = casac.image()
    ia.open(psf_file)
    psf_data_raw = ia.getregion()
    hdr = ia.summary(list=False)
    ia.close()
    delta = np.abs(hdr['incr'][0]*206265)
    try:
        rb = hdr['restoringbeam']
        major = rb['major']['value']
        minor = rb['minor']['value']
        phi = rb['positionangle']['value']
    except:
        major = hdr['perplanebeams']['beams']['*0']['*0']['major']['value']
        minor = hdr['perplanebeams']['beams']['*0']['*0']['minor']['value']
        phi = hdr['perplanebeams']['beams']['*0']['*0']['positionangle']['value']
    print('The CASA fitted beam is ' + str(major) + 'x' + str(minor) + \
                                       ' at ' + str(phi) + 'deg')
    npix = psf_data_raw.shape[0]         # Assume image is square
    # Check if image cube, or just single psf; this example doesn't handle the full
    # polarization case - implicitly assumes we can drop Stokes
    # If single psf, add an axis so we can use a single loop
    psf_data = np.squeeze(psf_data_raw)
    if len(psf_data.shape) == 2:
        psf_data = np.expand_dims(psf_data, axis=2)
    # Roll the axes to make looping more straightforward
    psf_rolled = np.rollaxis(psf_data,2)
    # Window out the region we want to consider
    i_min = int(npix/2-(npix_window-1)/2)
    i_max = int(npix/2+(npix_window-1)/2 + 1)
    psf_windowed = psf_rolled[0][i_min:i_max,i_min:i_max]
    # Mask out anything beyond the first null
    psf_windowed[psf_windowed<0.] = -1.
    psf_windowed = np.fft.fftshift(psf_windowed)
    for i in range(psf_windowed.shape[0]):
        left_edge = np.argmax(psf_windowed[i] < 0.)
        right_edge = npix_window-np.argmax(psf_windowed[i][::-1] < 0.)
        psf_windowed[i][left_edge:right_edge] = 0.
    psf_windowed = np.fft.fftshift(psf_windowed)
    # Create a clean beam to evaluate against
    clean_beam = gaussian_eval([major/2.355/delta, minor/2.355/delta, phi], \
                               psf_windowed, (npix_window-1)/2)
    # Calculate epsilon
    epsilon = np.sum(clean_beam)/np.sum(psf_windowed)
    print('Epsilon = ' + str(epsilon))
    # Regular JvM correction
    # create the convolved model
    convolved_temp_image = '{:s}_convolved_model_temp.image'.format(root)
    imsmooth(imagename=model_file, major=str(major)+'arcsec', minor=str(minor)+'arcsec',
             pa=str(phi)+'deg', targetres=True, outfile=convolved_temp_image)
    # doing the correction
    try:
        shutil.rmtree(root+'.JvMcorr.image')
    except:
        pass
    immath(imagename=[convolved_temp_image, residual_file],
           expr='IM0 + ' + str(epsilon) + '*IM1', outfile=root+'.JvMcorr.image')
    print('Wrote ' + root + '.JvMcorr.image')
    # clean up
    shutil.rmtree(convolved_temp_image)
    return epsilon


