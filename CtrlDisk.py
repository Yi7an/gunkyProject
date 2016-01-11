#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
import os
import shutil

from Season import Season, Chapter
from Serie import Serie

class CtrlDisk ():

	def __init__ (self):
		self.SERIE_PATH = '/mnt/sdcard1/Multimedia/'
		if not os.path.exists ('./tmp-dl'):
			os.makedirs ('./tmp-dl')

	def moveFile (self, fromPath, toPath):
		if not os.path.exists (self.SERIE_PATH + '/' + toPath):
			os.makedirs (self.SERIE_PATH + '/' + toPath)

		shutil.move ('./tmp-dl/' + fromPath, self.SERIE_PATH + '/' + toPath.replace ('?',''))

	def getLastChapter (self, serieName):
		if not os.path.exists (self.SERIE_PATH + '/' + serieName):
			os.makedirs (self.SERIE_PATH + '/' + serieName)

		data = os.listdir (self.SERIE_PATH + '/' + serieName)
		if len (data) == 0:
			return None
		return sorted (data) [len (data) -1]

	def getLastChapterBySeason (self, serieName, seasonNumber):
		if not os.path.exists (self.SERIE_PATH + '/' + serieName):
			os.makedirs (self.SERIE_PATH + '/' + serieName)

		data = os.listdir (self.SERIE_PATH + '/' + serieName)

		lastChapter = 0
		seasonNumberStr = ''

		if seasonNumber < 10:
			seasonNumberStr = '0'
		seasonNumberStr += str(seasonNumber)

		for d in sorted (data):
			if seasonNumberStr + 'x' in d:
				lastChapter = int (d [3:5])
		return lastChapter

	def getSeries (self):
		series = []

		try:
			try:
				self._cache = shelve.open ('cache.db', 'r')
			except:
				self._cache = shelve.open ('cache.db', 'n')

			seriesName = self._cache ['seriesName']
			for sN in seriesName:
				s = Serie ()
				s.setName (sN [0])
				s.setDescription (sN[1])
				s.setMainPageLinks (sN[2])

				seasons = []
				try:
					seasons = self._cache [sN[0].encode ('utf-8')]
				except Exception as e:
					print '  -> Error ' + str(e)

				s.setSeasons (seasons)
				series.append (s)
		except Exception as e:
			pass

		try:
			self._cache.close ()
		except Exception as e:
			pass
		return series

	def storeSerie (self, serie):
		try:
			self._cache = shelve.open ('cache.db', 'w')
		except:
			self._cache = shelve.open ('cache.db', 'n')

		serieName = serie.getName ()
		description = serie.getDescription ()
		mainPages = serie.getMainPageLinks ()
		seasons = serie.getSeasons ()

		data = []
		data.append (serieName)
		data.append (description)
		data.append (mainPages)

		if not self._cache.has_key ('seriesName'):
			res = []
			res.append (data)

			self._cache ['seriesName'] = res
			self._cache [serieName.encode ('utf-8')] = serie.getSeasons ()

		else:
			series = self._cache ['seriesName']
			count = 0
			found = False
			while count < len (series):
				if series [count] [0] == serieName and not found:
					series [count] == data
					self._cache [serieName.encode ('utf-8')] = serie.getSeasons ()

					found = True
				count += 1

			series.append (data)
			self._cache ['seriesName'] = series
			self._cache [serieName.encode ('utf-8')] = serie.getSeasons ()

		self._cache.close ()
