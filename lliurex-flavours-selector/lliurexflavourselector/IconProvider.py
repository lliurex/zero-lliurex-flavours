#!/usr/bin/python3

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtSvg import *
from PySide6.QtQuick import QQuickImageProvider
import os

class IconProvider(QQuickImageProvider):

	def __init__(self):

		super(IconProvider,self).__init__(QQuickImageProvider.Image)
		self.checkImage="/usr/lib/python3.12/dist-packages/lliurexflavourselector/rsrc/ok.png"

	#def __init__
	
	def requestImage(self,imagePath,size1,size2):

		return self.createIcon("/%s"%imagePath)

	#def requestImage

	def createIcon(self,imagePath):

		destImage=QImage()

		if "_OK" in imagePath:
			isInstalled=True
			appIcon=imagePath.split("_OK")[0]
		else:
			isInstalled=False
			appIcon=imagePath

		if os.path.exists(appIcon):
			destImage.load(appIcon,"png")
			
		s=QSize(64,64)
		destImage=destImage.scaled(s,aspectMode=Qt.KeepAspectRatio,mode=Qt.SmoothTransformation)
		lastImage=QImage()
		lastImage.load(self.checkImage,"png")
		p=QPainter()
		p.begin(destImage)
		p.drawImage(0,0,destImage)
		if isInstalled:
			p.drawImage(39,41,lastImage)
			p.end()

		return destImage

	#def createIcon

#clas IconProvider
