# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 15:41:22 2017

@author: Brownies
This script is supposed to be a useful toolbox to upload files to a ftp server
and get them back via url.
"""

import ftplib
import urllib.request
import time


def upload_to_ftp(server = None, user = None, password = None, filepath = None, serverpath = None, blocksize = 8192):
    #Upload a file to ftp server
    #server: ftp server
    #filepath: local path of the file including its name
    #serverpath: path on ftp server WITHOUT preceding '/' and including name
    if server == None or user == None or password == None or filepath == None or serverpath == None:
        print("Information missing. Aborting.")
        return
    session = ftplib.FTP(server, user, password)
    file = open(filepath, 'rb')
    session.storbinary('STOR '+serverpath, file, blocksize = blocksize)
    file.close()
    session.quit()
    
def append_to_ftp(server = None, user = None, password = None, filepath = None, serverpath = None, blocksize = 8192)    :
    #Only append data to a file on ftp server
    #server: ftp server
    #filepath: local path of the file including its name
    #serverpath: path on ftp server WITHOUT preceding '/' and including name
    if server == None or user == None or password == None or filepath == None or serverpath == None:
        print("Information missing. Aborting.")
        return
    session = None
    print("Connecting to ftp server...")
    while(session == None):
        try:
            print("Opening session...")
            session = ftplib.FTP(server, user, password)
            print("Connected.")
        except:
            print("Retry connecting to ftp server...")
            del session
            session = None
            time.sleep(3)
    file = open(filepath, 'rb')
    session.storbinary('APPE ' + serverpath, file, blocksize = blocksize)
    file.close()
    session.quit()
        
def multi_append_to_ftp(server = None, user = None, password = None, filepaths = None, serverpaths = None, blocksize = 8192)    :
    #Append data to several files on ftp server
    #server: ftp server
    #filepath: local path of the file including its name
    #serverpath: path on ftp server WITHOUT preceding '/' and including name
    if server == None or user == None or password == None or filepaths == None or serverpaths == None:
        print("Information missing. Aborting.")
        return
    session = None
    print("Connecting to ftp server...")
    while(session == None):
        try:
            print("Opening session...")
            session = ftplib.FTP(server, user, password)
            print("Connected.")
        except:
            print("Retry connecting to ftp server...")
            del session
            session = None
            time.sleep(3)
    for f, filepath in enumerate(filepaths):
        file = open(filepath, 'rb')
        print(filepath + ": Uploading file.")
        session.storbinary('APPE ' + serverpaths[f], file, blocksize = blocksize)
        print(filepath + ": File uploaded.")
        file.close()
    session.quit()            
    
def download_via_url(url = None, localpath = None):
    if url == None or localpath == None:
        print("Information missing. Aborting.")
        return
    urllib.request.urlretrieve(url, filename=localpath)
