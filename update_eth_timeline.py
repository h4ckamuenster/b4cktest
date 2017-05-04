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
import tkinter as tk
from tkinter import filedialog#

print('Connecting to kraken...')
while not 'k' in locals():
    try:        
        k = krakenex.API() #paloaltomünster
        c = krakenex.Connection()
    except:
        pass
print('Connected to kraken.')

assetpairs = None

while(assetpairs == None):
    try:
        assetpairs = k.query_public('AssetPairs')['result']
    except:
        pass
asset_ = 'XETHZEUR'    
asset = assetpairs[asset_]

def get_closes(api = k, interval = 1, filename = 'results.txt'):
    global c
    timeline_raw = None
    while timeline_raw == None:
        try:
            print("Asking for closes...")
            timeline_raw = api.query_public('OHLC', req = {'pair':asset_, 'interval':interval})['result'][asset_]
        except:
            api = krakenex.API() #paloaltomünster
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
    else:
        old_max_time = 0
    
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
    new_entries = i
    print('Closes cached')
    return new_times, new_closes, old_max_time,new_entries


        
abort = False        
def update_price(wait = 90, loop = True, filename = 'results_eth', interval = 1, filepath = 'results_eth_updates.txt', serverpath = 'results_eth.txt'):
    global abort
    global file_busy

    #Asking for the identification file    
    root = tk.Tk()
    root.withdraw()
    chosen_file_path = filedialog.askopenfilename()
    file = open(chosen_file_path)
    lines = []
    for line in file:
        lines.append(line)
    ftp_server = lines[0].split('\n')[0]
    user = lines[1].split('\n')[0]
    password = lines[2]
    download_source = lines[3]
    file.close()
    
    print("Downloading current data...")
    ftp.download_via_url( url = download_source + filename + '.txt', localpath = filename + '.txt')
    print("Download successful.")
    
    #Main loop
    while(abort == False):
        if loop == False:
            abort = True
        times, closes, old_max_time, new_entries = get_closes(interval = interval, filename=filename + '.txt')
        time_closes_array = numpy.array([times,closes]).T
                                        
        #Writing results
        numpy.savetxt(filename + '.txt',time_closes_array)
        print("New file saved.")        
        
        to_upload_times = times[-new_entries:]
        to_upload_closes = closes[-new_entries:]
        upload_array = numpy.array([to_upload_times, to_upload_closes]).T
                        
        #Writing file to upload
        numpy.savetxt(filename + '_updates.txt', upload_array)
        print("Update file saved.")
        
        #Converting to readable format
        max_time = max(times)
        days = []
        for utime in times:
            days.append((utime - max_time)/(24*3600))
            
        #Plot results
        pylab.close('all')
        pylab.plot(days, closes)        
        pylab.xlabel('days')
        pylab.savefig(filename + '.jpg', dpi = 300)
        print('prices updated')
        
        time0 = time.time()
        
        if os.path.isfile(filepath):
            print("Uploading file...")
            ftp.append_to_ftp(server = ftp_server, user = user, password = password, filepath = filepath, serverpath=serverpath)
            print("File uploaded.")            
        else:
            print("No such file.")
            pass
        
        time_passed = time.time() - time0
        while time_passed < wait:
            if(abort == False):
                print('Waiting ' + str(wait - time_passed) + ' more seconds...')
                time_passed = time.time() - time0
                time.sleep(10)                
            else:
                print("aborted")
                break        

update_thread = threading.Thread(target = update_price)

