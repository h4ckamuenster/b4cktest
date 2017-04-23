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

k = krakenex.API() #paloaltomünster
c = krakenex.Connection()

assetpairs = k.query_public('AssetPairs')['result']
asset_ = 'XETHZEUR'    
asset = assetpairs[asset_]

def get_closes(api = k, interval = 1):
    timeline_raw = k.query_public('OHLC', req = {'pair':asset_, 'interval':1})['result'][asset_]
    times = []
    closes = []
    
    for entry in timeline_raw:
        times.append(entry[0])
        closes.append(eval(entry[4]))
    
    if os.path.isfile('results.txt'):
        old_file = numpy.loadtxt('results.txt')
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
def update_price(wait = 60):
    global abort
    while(abort == False):
        times,closes = get_closes()
        time_closes_array = numpy.array([times,closes])
        numpy.savetxt('results.txt',time_closes_array)
        max_time = max(times)
        days = []
        for utime in times:
            days.append((utime - max_time)/(24*3600))
        pylab.close('all')
        pylab.plot(days, closes)        
        pylab.xlabel('days')
        pylab.savefig('results.jpg', dpi = 300)
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
        

update_thread = threading.Thread(target = update_price)
#update_thread.start()
    