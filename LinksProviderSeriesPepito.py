#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyvirtualdisplay import Display
from selenium import webdriver
from LinksProvider import LinksProvider
import requests
import time

from Parser import Parser
from Season import Link

class LinksProviderSeriesPepito(LinksProvider):

    def __init__ (self):
        super(LinksProviderSeriesPepito, self).__init__('seriespepito', 'http://www.seriespepito.to/')

    def getMainPageLink (self, serieName, q):
        if serieName == 'house m.d.':
            serieName = 'house, m.d.'
        elif serieName == 'sons of anarchy':
            serieName = 'hijos de la anarquia'

        display = Display(visible=0, size=(800, 600))
        display.start()

        driver = webdriver.Firefox()
        driver.set_page_load_timeout(60)
        driver.get(self._URL)

        driver.find_element_by_name ('searchquery').send_keys(serieName)

        menuItemFound = False
        tries = 5
        while not menuItemFound:
            try:
                _parser = Parser ()
                li = driver.find_element_by_class_name ('ui-menu-item')
                data = _parser.feed(str(li.get_attribute('innerHTML').encode('utf-8')))
                menuItemFound = True
                driver.quit()
                display.stop()
                q.put((self._name, data.get_childs()[0].attrs['href'][0]))

            except Exception as e:
                time.sleep (1)
                tries -= 1
                if tries == 0:
                    driver.quit()
                    display.stop()
                    raise Exception ('  -> Serie not found in SeriesPepito')

    def getChapterUrls (self, serieUrl, seasonNumber, chapterNumber, q):
        r = requests.get (serieUrl, headers={ "user-agent": "Mozilla/5.0" })

        if r.status_code != 200:
            raise Exception ('  -> error getting serie from SeriesPepito')

        _parser = Parser ()
        data = _parser.feed (r.text)
        td = data.get_by (tag = 'td')

        found = False

        chapterUrlArray = []
        for t in td:
            if not found and 'temporada-' + str (seasonNumber) + '/capitulo-' + str (chapterNumber) in str (t.get_childs () [0].attrs ['href'] [0]):
                found = True
                url = str (t.get_childs() [0].attrs ['href'] [0])
                r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })
                data = _parser.feed (r.text)

                tbody = data.get_by (tag = 'tbody')[1]

                for tr in tbody.get_childs ():
                    l = Link ()

                    l.setProviderName (self._name)

                    langFlagUrl = str (tr.get_childs ()[0].get_childs()[0].attrs['src'][0])
                    langFlagImg = langFlagUrl.split ('/') [len (langFlagUrl.split ('/')) -1]

                    if 'es.' in langFlagImg:
                        l.setLanguage ('Spanish')
                    elif 'la.' in langFlagImg:
                        l.setLanguage ('Latin')
                    elif 'sub.' in langFlagImg:
                        l.setLanguage ('English')
                        l.setSubtitles ('Spanish')
                    elif 'en.' in langFlagImg:
                        l.setLanguage ('English')

                    host = str (tr.get_childs ()[2].get_childs()[0].data[0]).strip ().lower ()
                    url = str (tr.get_childs ()[3].get_childs()[0].attrs['href'][0])

                    l.setHost (host)

                    r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })
                    data = _parser.feed (r.text)
                    l.setURL (str(data.get_by (clazz = 'btn btn-mini enlace_link')[0].attrs['href'][0]))

                    itemFound = False
                    for item in chapterUrlArray:
                        if str(item.getURL ()) == str(l.getURL ()):
                            itemFound = True

                    if not itemFound:
                        chapterUrlArray.append (l)

        for elem in chapterUrlArray:
            q.put((self._name,elem))
