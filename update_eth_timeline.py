# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import krakenex
import numpy
import os
import time
import threading
import matplotlib.pylab as pylab
import ftp_helper as ftp

k = krakenex.API() #paloaltomünster
c = krakenex.Connection()

assetpairs = k.query_public('AssetPairs')['result']
asset_ = 'XETHZEUR'    
asset = assetpairs[asset_]


def get_closes(api = k, interval = 1, filename = 'results.txt'):
    timeline_raw = None
    while timeline_raw == None:
        try:
            timeline_raw = k.query_public('OHLC', req = {'pair':asset_, 'interval':interval})['result'][asset_]
        except:
            print('reconnecting...')
            k = krakenex.API() #paloaltomünster
            c = krakenex.Connection()
            time.sleep(10)
    times = []
    closes = []
    
    for entry in timeline_raw:
        times.append(entry[0])
        closes.append(eval(entry[4]))
    
    if os.path.isfile(filename):
        old_file = numpy.loadtxt(filename)
        old_times = old_file[0]
        old_closes = old_file[1] 
        old_max_time = old_times.max()
    
    new_times = []
    new_closes = []
    
    if 'old_file' in locals():
        for time_ in old_times:
            new_times.append(time_)
        for close in old_closes:
            new_closes.append(close)
        for i, time_ in enumerate(times):        
            if time_ > old_max_time:
                new_times.append(time_)
                new_closes.append(closes[i])
    else:
        for i, time_ in enumerate(times):
            new_times.append(time_)
            new_closes.append(closes[i])
    print('Closes cached')
    return new_times, new_closes


        
abort = False        
def update_price(wait = 90, loop = True, filename = 'results', interval = 1):
    global abort
    while(abort == False):
        if loop == False:
            abort = True
        times,closes = get_closes(interval = interval, filename=filename + '.txt')
        time_closes_array = numpy.array([times,closes])
        numpy.savetxt(filename + '.txt',time_closes_array)
        max_time = max(times)
        days = []
        for utime in times:
            days.append((utime - max_time)/(24*3600))
        pylab.close('all')
        pylab.plot(days, closes)        
        pylab.xlabel('days')
        pylab.savefig(filename + '.jpg', dpi = 300)
        print('prices updated')
        time0 = time.time()
        while time.time() - time0 < wait:
            if(abort == False):
                print('Waiting...')
                time.sleep(10)                
            else:
                print("aborted")
                break
        "Updating finished"

ftp_server = ''
user = ''
password = ''
        
def upload_file(wait = 90, ftp_server = ftp_server, user = user, password = password, filepath = 'results.txt', serverpath = 'results.txt'):
    global abort
    while(abort == False):
        if os.path.isfile(filepath):
            ftp.upload_to_ftp(server = ftp_server, user = user, password = password, filepath = filepath, serverpath=serverpath)
            print("File updated.")
            time0 = time.time()
            while time.time() - time0 < wait:
                if(abort == False):
                    time.sleep(10)
                else:
                    print("aborted")
                    break
        else:
            print("No such file.")
            time.sleep(2)
            pass
        

update_thread = threading.Thread(target = update_price)
#upload_thread = threading.Thread(target = upload_file)
    
