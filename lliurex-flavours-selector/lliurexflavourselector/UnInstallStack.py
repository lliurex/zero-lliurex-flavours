#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

signal.signal(signal.SIGINT, signal.SIG_DFL)

class UnInstallStack(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		UnInstallStack.flavourSelectorManager=self.core.flavourSelectorManager

	#def __init__

	def unInstallProcess(self):

		UnInstallStack.flavourSelectorManager.totalUninstallError=0
		self.core.flavourStack.totalErrorInProcess=UnInstallStack.flavourSelectorManager.totalUninstallError
		self.endAction=False
		self.pkgProcessed=False
		self.error=False
		self.totalError=0
		self.showError=False
		countLimit=len(UnInstallStack.flavourSelectorManager.flavourSelected)
		if countLimit==0:
			self.countLimit=1
		else:
			self.countLimit=countLimit

		self.pkgToSelect=-1
		self.pkgToProcess=""
		self.uninstallProcessTimer=QTimer(None)
		self.uninstallProcessTimer.timeout.connect(self._uninstallProcessTimerRet)
		self.uninstallProcessTimer.start(100)		

	#def _checkMetaProtectionRet

	def _uninstallProcessTimerRet(self):

		if not self.pkgProcessed:
			if not self.endAction:
				self.pkgToSelect+=1
				if self.pkgToSelect<self.countLimit:
					self.pkgToProcess=UnInstallStack.flavourSelectorManager.flavourSelected[self.pkgToSelect]
					UnInstallStack.flavourSelectorManager.initUnInstallProcess(self.pkgToProcess)
					self.core.flavourStack.updateResultFlavoursModel('start')
					if not UnInstallStack.flavourSelectorManager.removePkgLaunched:
						UnInstallStack.flavourSelectorManager.removePkgLaunched=True
						self.core.mainStack.currentCommand=UnInstallStack.flavourSelectorManager.getUnInstallCommand(self.pkgToProcess)
						self.core.mainStack.endCurrentCommand=True
				else:
					self.endAction=True

				self.pkgProcessed=True

		if not self.endAction:
			if UnInstallStack.flavourSelectorManager.removePkgDone:
				if not UnInstallStack.flavourSelectorManager.checkRemoveLaunched:
					UnInstallStack.flavourSelectorManager.checkRemoveLaunched=True
					UnInstallStack.flavourSelectorManager.checkRemove(self.pkgToProcess)

				if UnInstallStack.flavourSelectorManager.checkRemoveDone:
					self.core.flavourStack.updateResultFlavoursModel("end")
					if not UnInstallStack.flavourSelectorManager.feedBackCheck[0]:
						self.error=True
						self.totalError+=1
					self.pkgProcessed=False
							
		
		else:
			if self.totalError>0:
				self.showError=True

			self.core.mainStack.isProgressBarVisible=False
			self.core.mainStack.isProcessRunning=False
			self.core.mainStack.endProcess=True
			self.core.mainStack.feedbackCode=""
			self.core.mainStack.enableApplyBtn=True
			self.core.flavourStack.enableFlavourList=True
			self.core.flavourStack.isAllInstalled=UnInstallStack.flavourSelectorManager.isAllInstalled()
			self.core.flavourStack.totalErrorInProcess=UnInstallStack.flavourSelectorManager.totalUninstallError
			self.core.mainStack.manageRemoveBtn()
			UnInstallStack.flavourSelectorManager.updateFlavourRegister()
			self.uninstallProcessTimer.stop()
			
			if self.showError:
				if self.countLimit==1:
					self.core.mainStack.showStatusMessage=[True,UnInstallStack.flavourSelectorManager.feedBackCheck[1],UnInstallStack.flavourSelectorManager.feedBackCheck[2]]
				else:
					self.core.mainStack.showStatusMessage=[True,UnInstallStack.flavourSelectorManager.ERROR_PARTIAL_UNINSTALL,"Error"]
			else:
				self.core.mainStack.showStatusMessage=[True,UnInstallStack.flavourSelectorManager.feedBackCheck[1],UnInstallStack.flavourSelectorManager.feedBackCheck[2]]
				

		if UnInstallStack.flavourSelectorManager.removePkgLaunched:
			if not UnInstallStack.flavourSelectorManager.removePkgDone:
				if not os.path.exists(UnInstallStack.flavourSelectorManager.tokenUnInstall[1]):
					UnInstallStack.flavourSelectorManager.removePkgDone=True
		
	#def _uninstallProcessTimerRet

#class UnInstallStack

from . import Core

