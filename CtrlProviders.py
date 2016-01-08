#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DownloadStreamCloud import DownloadStreamCloud
from DownloadNowVideo import DownloadNowVideo
from DownloadStreamin import DownloadStreamin

from InfoProviderImdb import InfoProviderImdb

from LinksProviderSeriesFlv import LinksProviderSeriesFlv
from LinksProviderSeriesPepito import LinksProviderSeriesPepito
from LinksProviderSeriesAdicto import LinksProviderSeriesAdicto

from Season import Link
from Tools import isNumber

class CtrlProviders ():

	def __init__ (self):
		self._infoProviderImdb = InfoProviderImdb ()

		self._linkProviderSeriesFlv = LinksProviderSeriesFlv ()
		self._linksProviderSeriesPepito = LinksProviderSeriesPepito ()
		self._linksProviderSeriesAdicto = LinksProviderSeriesAdicto ()

	def downloadVideo (self, url, host, name):
		if 'streamcloud' in host.lower():
			d = DownloadStreamCloud ()
			downloadErr = d.downloadVideo (url, name)

		elif 'nowvideo' in host.lower():
			d = DownloadNowVideo ()
			downloadErr = d.downloadVideo (url, name)

		elif 'streamin' in host.lower():
			d =  DownloadStreamin ()
			downloadErr = d.downloadVideo (url, name)
		#elif 'turbovideos' in host.lower():
		#	d =  DownloadTurbovideos ()
		#	downloadErr = d.downloadVideo (url, name)
		else:
			print '  -> host "' + host + '" not defined for download'

	def loadSerie (self, serieName):
		data = self._infoProviderImdb.loadSerie (serieName)
		if data == None:
			#data = self._infoProviderAnime.loadSerie (serieName)
			#if data == None:
				#...
			raise Exception ('Serie "' + serieName + '" not found')
		return data

	def printSuggerencies (self):
		print ''
		print ' -> suggerencies:'
		self._infoProviderImdb.printSuggerencies ()
		#self._infoProviderAnime.printSuggerencies ()
		print ''

	def getMainInfo (self, serieName):
		mainPages = []
		try:
			mainPages.append (self._linkProviderSeriesFlv.getMainPageLink (serieName))
		except Exception as e:
			print str(e)
		try:
			mainPages.append (self._linksProviderSeriesPepito.getMainPageLink (serieName))
		except Exception as e:
			print str(e)
		try:
			mainPages.append (self._linksProviderSeriesAdicto.getMainPageLink (serieName))
		except Exception as e:
			print str(e)

		return mainPages

	def getChapterUrls (self, mainPagesLinks, seasonNumber, chapterNumber):
		data = []
		for mainPage in mainPagesLinks:
			if 'seriesflv' in mainPage:
				chapterUrls = self._linkProviderSeriesFlv.getChapterUrls (mainPage, seasonNumber, chapterNumber)
				data += chapterUrls
			elif 'seriespepito' in mainPage:
				chapterUrls = self._linksProviderSeriesPepito.getChapterUrls (mainPage, seasonNumber, chapterNumber)
				data += chapterUrls
			elif 'seriesadicto' in mainPage:
				chapterUrls = self._linksProviderSeriesAdicto.getChapterUrls (mainPage, seasonNumber, chapterNumber)
				data += chapterUrls

		return data
