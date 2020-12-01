#!/usr/bin/env python3

from PyQt5 import QtCore, QtGui, QtWidgets


class waitingSpinner(QtWidgets.QLabel):

	#@QtCore.pyqtSlot()

	def start(self):

		if hasattr(self, "_movie"):
			self._movie.start()

	#def start

	#@QtCore.pyqtSlot()
	def stop(self):

		if hasattr(self, "_movie"):
			self._movie.stop()

	#def stop

	def setGif(self,filename,type_gif=None):

		if not hasattr(self, "_movie"):
			self.type_gif=type_gif
			self._movie = QtGui.QMovie(self)
			self._movie.setFileName(filename)
			self._movie.frameChanged.connect(self.on_frameChanged)
			if self._movie.loopCount() != -1:
				self._movie.finished.connect(self.start)

		self.stop()
	
	#def setGif    

	@QtCore.pyqtSlot(int)
	def on_frameChanged(self, frameNumber):
		
		if self.type_gif=="flavour":
			self.setPixmap(self._movie.currentPixmap().scaled(25,25))
		else:	
			self.setPixmap(self._movie.currentPixmap().scaled(50,50))

    #def on_frameChanged

  #def waitingSpinner