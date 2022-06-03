#!/usr/bin/env python3
import sys

from . import settings
from . import waitingSpinner
from . import LoadingBox
from . import InstallersBox
from . import EmptyBox
from . import MainWindow
from . import flavourSelectorManager

class Core:

	singleton=None
	DEBUG=False
	
	@classmethod
	def get_core(self):
		
		if Core.singleton==None:
			Core.singleton=Core()
			Core.singleton.init()

		return Core.singleton


	def __init__(self,args=None):
		
		self.dprint("Init...")
		
	#def __init__
	
	def init(self):

		self.rsrc_dir= settings.RSRC_DIR + "/"
		self.supported_flavours=settings.SUPPORTED_FLAVOUR+"/"
		self.banners=settings.BANNERS+"/"
		self.flavourSelectorManager=flavourSelectorManager.flavourSelectorManager()
		self.waitingSpinner=waitingSpinner.waitingSpinner()
		self.loadingBox=LoadingBox.LoadingBox()
		self.installersBox=InstallersBox.InstallersBox()
		self.emptyBox=EmptyBox.EmptyBox()
		self.mainWindow=MainWindow.MainWindow()

		self.mainWindow.show()
		self.mainWindow.loadGui()

	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
		