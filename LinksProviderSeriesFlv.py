#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from LinksProvider import LinksProvider
from Parser import Parser
from Season import Link

class LinksProviderSeriesFlv (LinksProvider):

    def __init__ (self):
        self._URL = 'http://www.seriesflv.net/api/'
        LinksProvider.__init__ (self, 'SeriesFlv')

    def getMainPageLink (self, serieName):
        if serieName == 'house m.d.':
            serieName = 'house, m.d.'

        url = self._URL + 'search/?q=' + serieName.replace(' ', '%20')
        r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })

        if r.status_code != 200:
            raise Exception (' -> error getting serie from SeriesFlv')

        _parser = Parser ()
        data = _parser.feed (r.text)

        if len (data.get_by (tag = 'a')) < 1:
            raise Exception (' -> serie "' + serieName + '" not found in SeriesFlv')

        return data.get_by (tag = 'a')[0].attrs['href'][0]

    def getChapterUrls (self, serieUrl, seasonNumber, chapterNumber):
        r = requests.get (serieUrl, headers={ "user-agent": "Mozilla/5.0" })

        if r.status_code != 200:
            raise Exception ('  -> error getting serie from SeriesFlv')

        _parser = Parser ()
        data = _parser.feed (r.text)
        td = data.get_by (tag = 'td', clazz = 'sape')

        cNumber = ''
        found = False
        if chapterNumber < 10:
            cNumber = '0'
        cNumber += str(chapterNumber)

        chapterUrlArray = []
        for t in td:
            if not found and ' ' + str(seasonNumber) + 'x' + cNumber in str(t.get_childs()[1].attrs['data'][0].encode('utf-8')):
                found = True
                url = str(t.get_childs()[1].attrs['href'][0])
                r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })
                data = _parser.feed (r.text)

                tbody = data.get_by (tag = 'tbody')[0]
                for tr in tbody.get_childs ():
                    l = Link ()

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

                    host = str (tr.get_childs ()[2].get_childs()[0].data[0]).lower ()
                    url = str (tr.get_childs ()[3].get_childs()[0].attrs['href'][0])

                    l.setHost (host)

                    r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })
                    data = _parser.feed (r.text)
                    l.setURL (str(data.get_by (tag = 'meta')[0].attrs['content'][0].split('=')[1]))

                    itemFound = False
                    for item in chapterUrlArray:
                        if str(item.getURL ()) == str(l.getURL ()):
                            itemFound = True

                    if not itemFound:
                        chapterUrlArray.append (l)

        return chapterUrlArray
