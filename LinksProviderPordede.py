#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyvirtualdisplay import Display
from selenium import webdriver
from LinksProvider import LinksProvider
import requests
import time

from Parser import Parser
from Season import Link
from Queue import Queue

class LinksProviderPordede(LinksProvider):

    def __init__ (self):
        super(LinksProviderPordede, self).__init__('pordede', 'http://pordede.com/')

    def getMainPageLink (self, serieName, q):
        url = self._URL + 'site/login'

        display = Display (visible=0, size=(800, 600))
        display.start ()

        driver = webdriver.Firefox()
        driver.set_page_load_timeout(60)
        driver.get(self._URL)

        tries = 10
        found = False

        while not found and tries > 0:
            try:
                driver.find_element_by_id ('LoginForm_username').send_keys('gunkyProject')
                driver.find_element_by_id ('LoginForm_password').send_keys('123456')
                found = True
            except Exception as e:
                time.sleep (1)
                tries = tries - 1
                if tries == 0:
                    driver.quit()
                    display.stop()
                    raise Exception ('  -> Can\'t enter to SeriesPordede')

        driver.find_element_by_xpath("//form[@id='login-form']/button[1]").submit ()

        tries = 5
        found = False

        while not found and tries > 0:
            try:
                driver.find_element_by_class_name ('rounded1').send_keys(serieName)
                found = True
            except Exception as e:
                time.sleep (1)
                tries = tries - 1

        tries = 5

        while found and tries > 0:
            try:
                elem = driver.find_element_by_class_name ('selected').find_element_by_class_name ('defaultLink').get_attribute ('href')
                driver.quit()
                display.stop()
                q.put((self._name, elem))
                tries = 0
            except Exception as e:
                time.sleep (1)
                tries = tries - 1
                if tries == 0:
                    driver.quit()
                    display.stop()
                    raise Exception ('  -> Serie not found in SeriesPordede')

    def getChapterUrls (self, serieUrl, seasonNumber, chapterNumber, q):

        r = requests.post (self._URL + 'site/login',  headers = {'Accept' : '*/*', \
                                                                 'Accept-Encoding' : 'gzip, deflate', \
                                                                 'Connection' : 'keep-alive', \
                                                                 'Content-Length' : '104', \
                                                                 'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8', \
                                                                 'Host' : 'www.pordede.com', \
                                                                 'Referer' : 'http://www.pordede.com/', \
                                                                 'User-Agent' : 'Mozilla/5.0' },  \
                                                       data = {'LoginForm[username]': 'gunkyProject', \
                                                               'LoginForm[password]': '123456', \
                                                               'popup' : '1', \
                                                               'sesscheck' : 'ne09kk9c0ua7mgdjmcn6qs9fq1'})

        cookies = r.cookies
        r = requests.get (serieUrl, cookies = cookies)

        _parser = Parser ()
        data = _parser.feed (r.text)

        seasons = data.get_by (clazz = 'episodes')

        linkToChapter = ''
        for s in seasons:
            if 'episodes-' + str(seasonNumber) in s.attrs['id'][0]:
                chapters = s.get_by (clazz = 'info')
                for c in chapters:
                    for n in c.get_by (clazz = 'number'):
                        if n.attrs['data'][0] in str(chapterNumber):
                            linkToChapter = self._URL[:-1] + c.get_childs()[0].attrs['href'][0]


        r = requests.get (linkToChapter, cookies = cookies)

        data = _parser.feed (r.text.encode('utf-8'))

        onlineLinks = data.get_by (clazz = 'linksPopup')[0].get_childs()[4]
        chapterLinks = onlineLinks.get_by (clazz = 'a aporteLink done')

        chapterUrlArray = []

        for cl in chapterLinks:
            try:
                l = Link ()
                childs = cl.get_childs()[0].get_childs()
                host = str(childs[0].get_childs()[0].attrs['src'][0].split ('_')[1].split('.')[0])

                l.setProviderName (self._name)

                flags = childs[1].get_by (tag = 'div')

                if 'spanish' in flags[0].attrs['class'][0]:
                    if 'LAT' in flags[0].attrs['data'][0]:
                        l.setLanguage ("Latin")
                    else:
                        l.setLanguage ("Spanish")
                elif 'english' in flags[0].attrs['class'][0]:
                    l.setLanguage ('English')

                if (len (flags) == 2):
                    if 'spanish' in flags[1].attrs['class'][0]:
                        l.setSubtitles ('Spanish')
                    else:
                        l.setSubtitles ('English')


                l.setHost (host)

                url = str(self._URL[:-1] + cl.attrs['href'][0])

                r = requests.get (url, cookies = cookies)
                data = _parser.feed (r.text)
                url = data.get_by (clazz = 'episodeText')[0].attrs['href'][0]

                r =  requests.get (self._URL[:-1] + url, cookies = cookies)
                l.setURL (r.url)

                itemFound = False
                for item in chapterUrlArray:
                    if str(item.getURL ()) == str(l.getURL ()):
                        itemFound = True

                if not itemFound:
                    chapterUrlArray.append (l)
            except Exception as e:
                pass

        for elem in chapterUrlArray:
            q.put((self._name, elem))
