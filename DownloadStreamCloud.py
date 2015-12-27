#! /usr/bin/python

from selenium import webdriver
from Download import Download
import time

class DownloadStreamCloud (Download):

    def __init__ (self):
        Download.__init__ (self)

    def getVideoLink (self, totalLines):
        for line in totalLines:
            if 'file: "http://' in line:
                return line.split ('"')[1]

    def waitForLink (self, elem):
        print '  -> waiting for the page load'
        while not 'blue' in elem.get_attribute("class"):
            time.sleep(1)

    def downloadVideo (self, link, name):
        self.driver = webdriver.Firefox()
        self.driver.set_page_load_timeout(60)

        print '  -> going to ' + link

        self.driver.get(link)
        elem = self.driver.find_element_by_id ('btn_download')

        self.waitForLink (elem)
        elem.submit ()

        videoLink = self.getVideoLink (self.driver.page_source.split ('\n'))
        self.downloadVideoFile (videoLink, name)

        self.driver.quit()
