#!/usr/bin/env python3

import pysigproc
import numpy as np

def fil_data(fil_file,tstart,tstop):
    """
    :param fil_file: name of the filterbank file
    :param tstart: start time in seconds
    :param tstop: stop time in seconds
    :return 2d data array, freqs, time series, sampling time 
    """
    fil_obj=pysigproc.SigprocFile(fil_file)
    nstart=int(tstart/fil_obj.tsamp)
    nsamp=int((tstop-tstart)/fil_obj.tsamp)
    img=fil_obj.get_data(nstart=nstart,nsamp=nsamp)[:,0,:]
    freqs=fil_obj.chan_freqs
    ts=np.linspace(tstart,tstop,endpoint=True,num=img.shape[0])
    return(img,freqs,ts,fil_obj.tsamp)

def dedisp(img, dm,freq,t_bin):
    """
    :param img: 2d array of frequency-time data
    :param dm: dispersion measure
    :param freq: frequency (MHz)
    :param t_bin: Sampling time (s)
    :return: dedispersed 2d array
    """
    nt, nf = img.shape
    assert nf == len(freq)
    dmk = 4148808.0
    inv_flow_sq = 1.0 / freq[-1] ** 2
    delay_time = np.array([dmk * dm  * (inv_flow_sq - 1/(f_chan**2)) for f_chan in freq])
    delay_bins = np.round(delay_time*1e-3/t_bin).astype('int64')
    dedisp_arr=np.zeros(img.shape)
    for ii, delay in enumerate(delay_bins):
        dedisp_arr[:,ii]=np.roll(img[:,ii],delay)
    return dedisp_arr

def bandpass(fil_file):
    """
    no explanation needed
    """
    fil_obj=pysigproc.SigprocFile(fil_file)
    bandpass=fil_obj.get_data(nstart=0,nsamp=int(fil_obj.nspectra))[:,0,:].sum(0)/fil_obj.nspectra
    return(fil_obj.chan_freqs,bandpass) 

def append_spectra(f, spectra):
    # Move to end of file
    f.seek(0, os.SEEK_END)
    f.write(spectra.flatten().astype(spectra.dtype))


def make_header(filobj):
    filobj.source_name = 'source'
    filobj.machine_id = int(0)
    filobj.barycentric = int(0)
    filobj.telescope_id = int(6)
    filobj.src_raj = 123456
    filobj.src_dej = 123456
    filobj.fch1 = 1919.882812
    filobj.foff = -0.234375
    filobj.nchans = 4096
    filobj.nbeams = 1
    filobj.nbits = 8
    filobj.tstart = 58289.609664351679
    filobj.tsamp = 0.000256
    filobj.nifs = 1
    return filobj


def write_header(filobj,filename):
    '''
    write fiterbank header
    :param filobj: object from pysigproc
    :param filename: file
    :return : object from pysigproc
    '''
    with open(filename,'wb') as f:
        filobj.send_string('HEADER_START',f)
        for k in list(filobj._type.keys()):
            filobj.send(k,f)
        filobj.send_string('HEADER_END',f)
    return filobj
