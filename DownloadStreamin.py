#! /usr/bin/python

from selenium import webdriver
from Download import Download
import time

class DownloadStreamin (Download):

    def getVideoLink (self, totalLines):
        for line in totalLines:
            if '{file:' in line:
                return line.split ('\'')[1]

    def waitForLink (self, elem):
        print '  -> waiting for the page load'
        while 'disabled' in elem.get_attribute('innerHTML'):
            time.sleep(1)

    def downloadVideo (self, link, name):

        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

        self.driver = webdriver.Firefox()
        self.driver.set_page_load_timeout(60)

        print '  -> going to ' + link

        self.driver.get(link)
        time.sleep (5)
        elem = self.driver.find_element_by_id ('btn_download')

        self.waitForLink (elem)
        elem.submit ()

        videoLink = self.getVideoLink (self.driver.page_source.split ('\n'))
        self.downloadVideoFile (videoLink, name)

        self.driver.quit()
        self.display.stop ()
