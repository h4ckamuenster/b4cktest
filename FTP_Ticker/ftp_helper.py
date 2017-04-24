# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 15:41:22 2017

@author: Brownies
This script is supposed to be a useful toolbox to upload files to a ftp server
and get them back via url.
"""

import ftplib
import urllib.request


def upload_to_ftp(server = None, user = None, password = None, filepath = None, serverpath = None):
    #Upload a file to ftp server
    #server: ftp server
    #filepath: local path of the file including its name
    #serverpath: path on ftp server WITHOUT preceding '/' and including name
    if server == None or user == None or password == None or filepath == None or serverpath == None:
        print("Information missing. Aborting.")
        return
    session = ftplib.FTP(server, user, password)
    file = open(filepath, 'rb')
    session.storbinary('STOR '+serverpath, file)
    file.close()
    session.quit()
    
def download_via_url(url = None, localpath = None):
    if url == None or localpath == None:
        print("Information missing. Aborting.")
        return
    urllib.request.urlretrieve(url, filename=localpath)