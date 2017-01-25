#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 13:44:34 2017

@author: ONeill
"""

import numpy as np
import matplotlib.pyplot as plt
#from quick_image import display_image, readimage
from quick_image import display_image, readimage
import thacherphot as tp
import hcongrid as h
from astropy.io import fits
from kapteyn import maputils
import sys
import pdb
import os

def make_im(datadir=dir,plot=True):
    '''
    Combines solved images using hcongrid to produce .fits and .png of total field
    Should run on bellerophon in interest of time
    '''
    #Creates master bias and flats
    bias_files, biasfct = tp.get_files(dir=datadir,prefix='P9',suffix='bias.fit')
    flat_files, flatfct = tp.get_files(dir=datadir,prefix='cal',suffix='.fit')
    bias = tp.master_bias(bias_files)
    flat = tp.master_flat(flat_files)
    
    files,fct = tp.get_files(dir=datadir,prefix='P9',suffix='solved.fits')

    #Establishes frame in middle of run as reference file for hcongrid
    zsz = len(files)
    reffile = files[zsz/2]
    image0,header0 = readimage(reffile)
    ysz, xsz = np.shape(image0)
    refh = h.pyfits.getheader(reffile)
    stack = np.zeros((xsz,ysz,zsz))
    
    #Stacks images using hcongrid with middle frame as reference
    for i in range(zsz):
        print 'Starting image '+str(i)+' of '+str(zsz)
        im = h.pyfits.open(files[i])
        #im_orig = im[0].data
        #im_fix = (im[0].data-bias)/flat
        #show_image(im_orig)
        #show_image(im_fix)
        #pdb.set_trace()
        newim = h.hcongrid((im[0].data-bias), im[0].header,refh)
        stack[:,:,i] = newim
    
    #Creates final image and saves as .fits
    final = np.median(stack, axis=2)
    #display_image(final)
    display_image(final)
    
    refs = '/Users/ONeill/astronomy/python/git/planet9/data/PanSTARRS.table'
    
    rmcmd = 'rm -rf '+'P9_sample_image.fits'
    os.system(rmcmd)
    fits.writeto('P9_sample_image.fits', final, refh)
    #sys.exit()
    
    #Adds annotations to final image and saves as .png
    if plot:
        image0,header0 = readimage("P9_sample_image.fits")
        clipmin = np.median(image0)-0.3*np.std(image0)
        clipmax = np.median(image0)+2*np.std(image0)
        f = maputils.FITSimage("P9_sample_image.fits")
        fig = plt.figure()
        frame = fig.add_subplot(1,1,1)
        annim = f.Annotatedimage(frame,cmap="gray", clipmin=clipmin, clipmax=clipmax)
        annim.Image()
        grat = annim.Graticule()
        grat.setp_gratline(visible=True,linestyle='--')
        grat.setp_axislabel("bottom",label=r"$\mathrm{Right\ Ascension\ (J2000)}$",fontsize=16)
        grat.setp_axislabel("left",label=r"$\mathrm{Declination\ (J2000)}$",fontsize=16)
        grat.setp_ticklabel(plotaxis='left',fontsize=14)
        grat.setp_ticklabel(plotaxis='bottom',fontsize=14)
        annim.plot()
        rmcmd = 'rm -rf '+'P9_sample_image.png'
        os.system(rmcmd)
        plt.savefig('P9_sample_image.png',dpi=300)
        plt.show()
        
    return
