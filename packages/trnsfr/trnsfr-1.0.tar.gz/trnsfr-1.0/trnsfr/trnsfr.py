#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import time
import posixpath

import code
import pprint

import requests
import requests_toolbelt
import tqdm
import validators


# Globals
VERSION = '1.0'

INSTANCE_URL = 'https://transfer.adminforge.de/'

# Options definition
parser = argparse.ArgumentParser(description="version: " + VERSION)
parser.add_argument('file', help = 'File(s) to upload', nargs = '+')

server_grp = parser.add_argument_group('Server parameters')
server_grp.add_argument('-s', '--server', help='Server instance URL (default: "%s")' % INSTANCE_URL, default = INSTANCE_URL)

upload_grp = parser.add_argument_group('Upload parameters')
upload_grp.add_argument('-k', '--max-days', help='Maximum number of days to keep file on the server', type = int, default = None)
upload_grp.add_argument('-t', '--max-downloads', help='Maximum number of times that file can be downloaded', type = str, default = None)

output_grp = parser.add_argument_group('Output parameters')
output_grp.add_argument('-d', '--show-delete-url', help='Show URL to delete (default: False)', action='store_true', default = False)

display_grp = parser.add_argument_group('Display parameters')
display_grp = display_grp.add_mutually_exclusive_group()
display_grp.add_argument('-v', '--verbose', help='Verbose output (default: False)', action='store_true', default = False)
display_grp.add_argument('-n', '--no-progress-bar', help='Do not display the progress bar (default: False)', action='store_true', default = False)
display_grp.add_argument('-q', '--quiet', help='Display only the download link without progress bar (default: False)', action='store_true', default = False)

encrypt_grp = parser.add_argument_group('Confidentiality parameters')
encrypt_grp.add_argument('-e', '--encrypt-password', help='Encrypt file with that password on the server-side (default: None)', type = str, default = None)

security_grp = parser.add_argument_group('Malware scan parameters')
malware_scan_provider_clamav = 'clamav'
malware_scan_provider_virustotal = 'virustotal'
malware_scan_choices = [malware_scan_provider_clamav, malware_scan_provider_virustotal]
security_grp.add_argument('-m', '--scan-malware', help=r'Scan for malware with ClamAV or Virustotal (possible values: %s ; default: None): /!\ this feature can be unavailable on the server and hence failing the whole upload ! (default: False)' % malware_scan_choices, choices = malware_scan_choices, type = str.lower, default = False)


def upload_files(options):
    disable_progress_bar = False
    if options.quiet or options.no_progress_bar:
        disable_progress_bar = True
    
    disable_prints = False
    if options.quiet:
        disable_prints = True
    
    for file_to_upload in options.file:
        if os.path.isfile(file_to_upload):
            print('\n[+] File to upload: "%s"' % file_to_upload) if not(disable_prints) else None
            
            with tqdm.tqdm(disable=disable_progress_bar, leave=False, desc=file_to_upload, total=os.path.getsize(file_to_upload), unit="B", unit_scale=True, unit_divisor=1024) as progress_bar:
                with open(file_to_upload, 'rb') as data:
                    # Upload file
                    fields = {"file": (file_to_upload, data)}
                    headers = {}
                    # Option to indicate the maximum number of days
                    if options.max_days is not None:
                        headers['Max-Days'] = str(options.max_days)
                    
                    # Option to indicate the maximum number of downloads
                    if options.max_downloads is not None:
                        headers['Max-Downloads'] = str(options.max_downloads)
                    
                    if options.encrypt_password is not None:
                        headers['X-Encrypt-Password'] = options.encrypt_password

                    m = requests_toolbelt.MultipartEncoderMonitor(
                        requests_toolbelt.MultipartEncoder(fields=fields),
                        lambda monitor: progress_bar.update(monitor.bytes_read - progress_bar.n))
                    
                    headers['Content-Type'] = m.content_type
                    
                    file_name = os.path.basename(file_to_upload)
                    remote_url = options.server
                    request_method = 'post'
                    
                    if options.scan_malware:
                        request_method = 'put'
                        if options.scan_malware == malware_scan_provider_clamav:
                            remote_url = posixpath.join(remote_url, file_name, 'scan')
                            
                        elif options.scan_malware == malware_scan_provider_virustotal:
                            remote_url = posixpath.join(remote_url, file_name, 'virustotal')
                    
                    download_url = ''
                    delete_url = ''
                    
                    try:
                        if request_method == 'post':
                            req = requests.post(remote_url, data=m, headers=headers)
                        
                        elif request_method == 'put':
                            req = requests.put(remote_url, data=m, headers=headers)
                            
                        if req.ok:
                            download_link = req.text.strip()
                            if validators.url(download_link):
                                download_url = download_link
                            
                            if 'x-url-delete' in req.headers:
                                delete_link = req.headers['x-url-delete'].strip()
                                if validators.url(delete_link):
                                    delete_url = delete_link
                            
                            if options.verbose:
                                print('[+] Download URL: "%s"' % download_url)
                                if options.show_delete_url:
                                    print('[+] Delete URL:   "%s"' % delete_url)
                            else:
                                print('%s' % download_url)
                                if options.show_delete_url:
                                    print('%s' % delete_url)
                            
                        else:
                            print('[!] Error while uploading "%s" | HTTP return code %s | Returned response "%s"' % (file_to_upload, req.status_code, req.content.decode('utf-8').strip()))
                    
                    except Exception as e:
                        print('[!] Exception while uploading "%s": "%s"' % (file_to_upload, e))
                        pass
    
    return None


def main():
    global parser
    options = parser.parse_args()
    
    res = upload_files(options)
    
    return None

if __name__ == "__main__" :
    main()