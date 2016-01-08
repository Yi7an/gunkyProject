#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from LinksProvider import LinksProvider
from Parser import Parser
from Season import Link

class LinksProviderSeriesAdicto (LinksProvider):

    def __init__ (self):
        self._URL = 'http://seriesadicto.com/'
        LinksProvider.__init__ (self, 'SeriesAdicto')

    def getMainPageLink (self, serieName):
        url = self._URL + 'buscar/' + serieName.replace(' ', '%20')
        r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })

        if r.status_code != 200:
            raise Exception ('  -> error getting serie from SeriesFlv')

        _parser = Parser ()
        data = _parser.feed (r.text)

        clazz = data.get_by (clazz = 'col-xs-6 col-sm-4 col-md-2')
        if len (clazz) != 1:
            raise Exception ('  -> serie "' + serieName + '" not found in SeriesFlv')

        return self._URL[:-1] + str(clazz[0].get_childs()[0].attrs['href'][0])

    def getChapterUrls (self, serieUrl, seasonNumber, chapterNumber):
        r = requests.get (serieUrl, headers={ "user-agent": "Mozilla/5.0" })

        if r.status_code != 200:
            raise Exception ('  -> error getting serie from SeriesFlv')

        _parser = Parser ()
        data = _parser.feed (r.text)
        td = data.get_by (tag = 'td', clazz = 'sape')

        cNumber = ''
        found = False

        chapterUrlArray = []
        for t in td:
            if not found and '/' + str(seasonNumber) + '/' + str(chapterNumber) in str(t.get_childs()[1].attrs['href'][0]):
                found = True
                url = self._URL + str(t.get_childs()[1].attrs['href'][0])

                r = requests.get (url, headers={ "user-agent": "Mozilla/5.0" })
                data = _parser.feed (r.text)

                tbody = data.get_by (tag = 'tbody')[0]
                for tr in tbody.get_childs ():
                    l = Link ()

                    langFlagUrl = str (tr.get_childs ()[0].get_childs()[0].attrs['src'][0])
                    langFlagImg = langFlagUrl.split ('/') [len (langFlagUrl.split ('/')) -1]

                    if '1.' in langFlagImg:
                        l.setLanguage ('Spanish')
                    elif '2.' in langFlagImg:
                        l.setLanguage ('Latin')
                    elif '3.' in langFlagImg:
                        l.setLanguage ('English')
                        l.setSubtitles ('Spanish')
                    elif '4.' in langFlagImg:
                        l.setLanguage ('English')

                    host = str (tr.get_childs ()[1].data[0]).lower ()
                    url = str (tr.get_childs ()[2].get_childs()[0].attrs['href'][0])

                    l.setHost (host)
                    l.setURL (url)

                    itemFound = False
                    for item in chapterUrlArray:
                        if str(item.getURL ()) == str(l.getURL ()):
                            itemFound = True

                    if not itemFound:
                        chapterUrlArray.append (l)

        return chapterUrlArray
