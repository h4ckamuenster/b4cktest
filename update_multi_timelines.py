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
from tkinter import filedialog
import requests

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
assets_ = ['XETHZEUR', 'XREPZEUR', 'XXRPXXBT', 'XXLMZEUR', 'XLTCZEUR', 'XXBTZEUR', 'XETCZEUR', 'XXMRZEUR', 'XETHXXBT', 'GNOEUR', 'XETCXETH', 'XZECZEUR']

def get_multi_closes(api = k, interval = 1, assets = assets_):
    global c
    results = []
    for asset_ in assets:
        timeline_raw = None
        while timeline_raw == None:
            try:
                print(asset_ + ": Asking for closes...")
                timeline_raw = api.query_public('OHLC', req = {'pair':asset_, 'interval':interval})['result'][asset_]
            except:
                api = krakenex.API() #paloaltomünster
                c = krakenex.Connection()
                print("Reconnecting to kraken...")
                time.sleep(10)
        times = []
        closes = []
        
        for entry in timeline_raw:
            times.append(entry[0])
            closes.append(eval(entry[4]))
        
        filename = asset_ + ".txt"
            
        if os.path.isfile(filename):
            old_file = numpy.loadtxt(filename)
            old_times = old_file[:,0]
            old_closes = old_file[:,1] 
            old_max_time = old_times.max()
        else:
            old_max_time = 0
        
        new_times = []
        new_closes = []
        n = 0
        if 'old_file' in locals():
            print('\n' + asset_ + ": Combining old and new data...")
            for time_ in old_times:
                new_times.append(time_)
            for close in old_closes:
                new_closes.append(close)
            for i, time_ in enumerate(times):        
                if time_ > old_max_time:
                    n += 1
                    new_times.append(time_)
                    new_closes.append(closes[i])
            del old_file
        else:
            for i, time_ in enumerate(times):
                n += 1
                new_times.append(time_)
                new_closes.append(closes[i])
        new_entries = n
        print(asset_ + ': Closes cached')
        print(asset_ + ': ' + str(new_entries) + ' new entries.')
        results.append([new_times, new_closes, old_max_time, new_entries])
    return results


        
abort = False        
def multi_update_price(wait = 10 * 60, loop = True, assets = assets_ , interval = 1):
    global abort

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
    
    #Upload latest asset list to ftp server
    print("\nUpdating asset list on server...")
    numpy.savetxt('assets.txt', numpy.array(assets).T, fmt = "%s")
    ftp.upload_to_ftp(server = ftp_server, user = user, password = password, filepath = 'assets.txt', serverpath = 'assets.txt')
    print("Asset list updated.")
    
    
    #Downloading all available old data    
    for asset_ in assets:
        r = requests.head(download_source + asset_ + ".txt", allow_redirects=True, auth=(user, password))
        if r.status_code == 200:
            print('\n' + asset_ + ": Downloading current data...")
            ftp.download_via_url( url = download_source + asset_ + '.txt', localpath = asset_ + '.txt')
            print(asset_ + ": Download successful.")
        else:
            print(asset_ + ": No online data available.")
    print("All online resources considered.")
    
    serverpaths = []
    updatepaths = []
    for asset_ in assets:
        serverpaths.append(asset_ + ".txt")
        updatepaths.append(asset_ + "_updates.txt")
    
    #Main loop
    while(abort == False):
        if loop == False:
            abort = True
        multi_closes = get_multi_closes(interval = interval, assets = assets)
        time0 = time.time()
        for a,asset_ in enumerate(assets):
            times, closes, old_max_time, new_entries = multi_closes[a]
            time_closes_array = numpy.array([times,closes]).T
                                            
            #Writing results
            numpy.savetxt(asset_ + '.txt',time_closes_array)
            print('\n' + asset_ + ": New file saved.")        
            
            to_upload_times = times[-new_entries:]
            to_upload_closes = closes[-new_entries:]
            upload_array = numpy.array([to_upload_times, to_upload_closes]).T
                            
            #Writing file to upload
            numpy.savetxt(asset_ + '_updates.txt', upload_array)
            print(asset_ + ": Update file saved.")
            
            #Converting to readable format
            max_time = max(times)
            days = []
            for utime in times:
                days.append((utime - max_time)/(24*3600))
                
            #Plot results
            pylab.close('all')
            pylab.plot(days, closes)        
            pylab.xlabel('days')
            pylab.savefig(asset_ + '.jpg', dpi = 300)
            print(asset_ + ': Plot updated')
            
        #Update files to server            
        print("Uploading files...")
        ftp.multi_append_to_ftp(server = ftp_server, user = user, password = password, filepaths = updatepaths, serverpaths = serverpaths)
        print("Files uploaded.")        
            
        time_passed = time.time() - time0
        while time_passed < wait:
            if(abort == False):
                print('Waiting ' + str(wait - time_passed) + ' more seconds...')
                time_passed = time.time() - time0
                time.sleep(min(10, (wait - time_passed)))           
            else:
                print("aborted")
                break        

multi_update_thread = threading.Thread(target = multi_update_price)

