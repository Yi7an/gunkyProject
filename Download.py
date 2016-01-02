#! /usr/bin/python

from pyvirtualdisplay import Display
from sys import stdout
import requests

class Download ():

    def downloadVideoFile (self, videoLink, name):
    	r = requests.get (videoLink, stream = True)
    	totalLength = float (r.headers.get ('content-length'))

    	if totalLength < 1024000:
    		raise Exception ('Video with not enough length! ' + str( format (totalLength/1024, '.2f')) + ' KB')

    	stdout.write ('  -> downloading "' + name + '" (' + str( format (totalLength/1024/1024, '.2f')) + ' MB) [')
    	stdout.flush ()

    	downloaded = 0
    	progress = 1
    	if r.status_code == 200:
    		with open ('./tmp-dl/' + name, 'wb') as f:
    			for chunk in r:
    				f.write (chunk)
    				downloaded += len(chunk)

                    		if float (downloaded/totalLength)*10 > progress:
    					progress += 1
    					stdout.write ('#')
    					stdout.flush ()

    		stdout.write (']\n')
    		stdout.flush ()
    		print '  -> "' + name + '" downloaded successfull'
    	else:
    		stdout.write (']\n')
    		stdout.flush ()
    		print '  -> error downloading ' + name

    def checkVideoLink (self, videoLink, name):
    	r = requests.get (videoLink, stream = True)
    	totalLength = float (r.headers.get ('content-length'))

    	if totalLength >= 1024000:
    		return True

    	return False
