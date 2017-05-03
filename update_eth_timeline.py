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

k = krakenex.API() #paloaltomünster
c = krakenex.Connection()

assetpairs = k.query_public('AssetPairs')['result']
asset_ = 'XETHZEUR'    
asset = assetpairs[asset_]

file_busy = False
file_upload_rdy = False

def get_closes(api = k, interval = 1, filename = 'results.txt'):
    global c
    timeline_raw = None
    while timeline_raw == None:
        try:
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
    global file_busy
    global file_upload_rdy
    while(abort == False):
        if loop == False:
            abort = True
        times,closes = get_closes(interval = interval, filename=filename + '.txt')
        time_closes_array = numpy.array([times,closes])
        while(file_busy == True or file_upload_rdy == False):
            time.sleep(5)
            print("File busy. Update waiting...")
        if file_busy == False:
            file_busy = True
            numpy.savetxt(filename + '.txt',time_closes_array)
            file_busy = False
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

ftp_server = ''
user = ''
password = ''
        
def upload_file(wait = 180, ftp_server = ftp_server, user = user, password = password, filepath = 'results.txt', serverpath = 'results.txt'):
    global abort
    global file_busy
    global file_upload_rdy
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
    print("Preparing first upload...")
    ftp.upload_to_ftp(server = ftp_server, user = user, password = password, filepath = filepath, serverpath=serverpath)
    print("File uploaded.")
    file_upload_rdy = True
    while(abort == False):
        if os.path.isfile(filepath):
            while(file_busy == True):
                time.sleep(5)
                print("File busy. Upload waiting...")
            if file_busy == False:
                file_busy = True
                try:
                    ftp.upload_to_ftp(server = ftp_server, user = user, password = password, filepath = filepath, serverpath=serverpath)
                    print("File uploaded.")
                except:
                    print("Could not upload file. Retry in " + str(wait) + " seconds...")
                file_busy = False
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
upload_thread = threading.Thread(target = upload_file)
    
