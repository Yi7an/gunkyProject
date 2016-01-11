#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CtrlProviders import CtrlProviders
from CtrlDisk import CtrlDisk
from Serie import Serie

from Tools import readInt, isNumber
from sys import exit, stdout
from random import randint

class Domain ():

	def __init__ (self):
		self._ctrlProviders = CtrlProviders ()
		self._ctrlDisk = CtrlDisk()
		self.series = self._ctrlDisk.getSeries ()

	def _serieAlreadyLoaded (self, serieName):
		for s in self.series:
			if s.getName ().lower () == serieName.lower():
				return True
		return False

	def _getSerieLoaded (self, serieName):
		for serie in self.series:
			if serie.getName ().lower () == serieName.lower():
				return serie

	def _updateSerie (self, serieName):
		print ''
		print '  -> finding serie "' + serieName + '"'
		serieData = self._ctrlProviders.loadSerie (serieName.lower())
		if serieData == None:
			raise Exception ('  -> serie "' + serieName + '" not found')
			self._ctrlProviders.printSuggerencies ()

		serieMainPages = self._ctrlProviders.getMainInfo (serieName.lower())


		serie = Serie ()
		serie.loadSerie (serieData)
		serie.setMainPageLinks (serieMainPages)

		self.series.append (serie)
		self._ctrlDisk.storeSerie (serie)

		return serie

	def _getSerie (self, serieName):
		serie = Serie ()
		if self._serieAlreadyLoaded (serieName):
			serie = self._getSerieLoaded (serieName)
		else:
			serie = self._updateSerie (serieName)
		return serie

	def viewSerie (self, serieName):
		serie = Serie ()
		try:
			serie = self._getSerie (serieName)
		except Exception as e:
			print '  -> serie "' + serieName + '" not found'
			self._ctrlProviders.printSuggerencies ()
			return

		serie.printSerie ()

	def updateSerie (self, serieName):
		self._updateSerie (serieName)

	def _selectChapter (self, links):
		possibleLinks = []
		print ''
		for i, l in enumerate(links):
			stdout.write('   -> #' + str( i + 1 ) + ' - ')

			if 'Spanish' in l.getLanguage ():
				if 'streamcloud' in l.getHost ().lower () or \
				   'nowvideo' in l.getHost ().lower () or \
				   'streamin' in l.getHost ().lower () or \
				   'streamplay' in l.getHost ().lower ():
					possibleLinks.append(l)
			l.printLink ()

		if len(possibleLinks) > 1:
			rand = randint (0, len(possibleLinks)-1)
			for j, l in enumerate(links):
				if l.getURL () in possibleLinks [rand].getURL ():
					print ''
					print '  -> link #' + str( j + 1 ) + ' automatically selected'
					return possibleLinks [rand]

		else:
			print ''
			print '  -> can\'t select a link automatically'
			read = readInt ('which download? [1-' + str (len (links)) + ']')
			print ''

			while read > len (links) -1 or read <1:
				print '  -> "' + str(read) + '" is not valid  number'
				read = readInt ('which download? [1-' + str (len (links)) + ']') - 1
				print ''

			return links [read - 1]

	def _buildName (self, serie, seasonNumber, chapterNumber):
		name = ''
		if seasonNumber < 10:
			name += '0'
		name += str(seasonNumber) + 'x'

		if chapterNumber < 10:
			name += '0'
		name += str(chapterNumber) + ' - ' + \
		serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].getName () + '.mp4'

		return name

	def downloadChapter (self, serieName, seasonNumber, chapterNumber):
		serie = Serie ()
		try:
			serie = self._getSerie (serieName)
		except Exception as e:
			print '  -> serie "' + serieName + '" not found'
			self._ctrlProviders.printSuggerencies ()
			return

		if serie.seasonExists (seasonNumber):
			if serie.chapterNumberExists (seasonNumber, chapterNumber):
				print ''
				serie.printChapter (seasonNumber, chapterNumber)

				if len (serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].getLinkArray ()) == 0:
					chapterUrls = self._ctrlProviders.getChapterUrls(serie.getMainPageLinks (), seasonNumber, chapterNumber)
					if isNumber (chapterUrls):
						print '  -> error, can\'t retrieve the chapter (Error ' + str(chapterUrls) + ')'
						raise Exception ('error, can\'t retrieve the chapter')
					serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].appendLinkArray (chapterUrls)
					self._ctrlDisk.storeSerie (serie)

				chapterUrls = serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].getLinkArray ()
				name = self._buildName (serie, seasonNumber, chapterNumber)

				if len(chapterUrls) > 0:
					print ''
					downloadErr = True
					while downloadErr:
						selectedChapter = self._selectChapter (chapterUrls)

						try:
							self._ctrlProviders.downloadVideo (selectedChapter.getURL (), \
													   selectedChapter.getHost (),\
													   name)

							self._ctrlDisk.moveFile (name, serie.getName ())

							downloadErr = False
						except Exception as e:
							print '  -> error downloading chapter "' + name + '"'
							iterator = 0
							deleted = False
							while iterator < len (chapterUrls) and not deleted:
								if selectedChapter.getURL () is chapterUrls [iterator].getURL ():
									print '  -> link deleted'
									print ''
									chapterUrls.pop (iterator)
									serie.getSeasons ()[seasonNumber-1].getChapters ()[chapterNumber-1].setLinkArray (chapterUrls)
									self._ctrlDisk.storeSerie (serie)
									deleted = True
								iterator += 1
				else:
					print '  -> no links found, skipping chapter '
			else:
				print ''
				print ' -> chapter number ' + str(chapterNumber) + ' doesn\'t exist'
		else:
			print ''
			print ' -> season number ' + str(seasonNumber) + ' doesn\'t exist'

	def downloadNext (self, serieName):
		serie = Serie ()
		try:
			serie = self._getSerie (serieName)
		except Exception as e:
			print ' -> serie "' + serieName + '" not found'
			return

		if serie == None:
			return

		lastChapter = self._ctrlDisk.getLastChapter( serie.getName ())
		if lastChapter == None:
			self.downloadChapter (serieName, 1, 1)
		else:
				seasonNumber = int (lastChapter [0:2])
				chapterNumber = int (lastChapter [3:5])

				if serie.chapterNumberExists (seasonNumber, chapterNumber + 1):
					self.downloadChapter (serieName, seasonNumber, chapterNumber + 1)
				else:
					if serie.chapterNumberExists (seasonNumber + 1, 1):
						self.downloadChapter (serieName, seasonNumber + 1, 1)
					else:
						print ' -> chapter 0' + str(seasonNumber + 1) + 'x01 unavailable'

	def downloadSeason (self, serieName, seasonNumber):
		serie = Serie ()
		try:
			serie = self._getSerie (serieName)
		except Exception as e:
			print ' -> serie "' + serieName + '" not found'
			return

		if serie == None:
			return

		lastChapter = self._ctrlDisk.getLastChapterBySeason( serie.getName (), seasonNumber)
		chapterNumber = lastChapter + 1

		if serie.seasonExists (seasonNumber):
			while chapterNumber <= len (serie.getSeasons () [seasonNumber -1].getChapters ()):
				self.downloadChapter (serieName, seasonNumber, chapterNumber)
				chapterNumber += 1
		print ''
		print '  -> season ' + str (seasonNumber) + ' download successful'
		print ''
