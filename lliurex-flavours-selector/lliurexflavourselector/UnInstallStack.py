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
		self.countLimit=1
		UnInstallStack.flavourSelectorManager=self.core.flavourSelectorManager

	#def __init__

	def unInstallProcess(self):

		self.core.mainStack.launchedProcess="uninstall"
		self.core.mainStack.enableKonsole=True
		self.core.mainStack.feedbackCode=UnInstallStack.flavourSelectorManager.MSG_FEEDBACK_UNINSTALL_RUN
		self.core.flavourStack.totalErrorInProcess=0
		self.endAction=False
		self.pkgProcessed=False
		self.error=False
		self.totalError=0
		self.showError=False
		countLimit=len(UnInstallStack.flavourSelectorManager.flavourSelectedToRemove)
		if countLimit==0:
			self.countLimit=1
		else:
			self.countLimit=countLimit

		self.pkgToSelect=-1
		self.pkgToProcess=""
		UnInstallStack.flavourSelectorManager.preUninstallProcess()
		self.uninstallProcessTimer=QTimer(None)
		self.uninstallProcessTimer.timeout.connect(self._uninstallProcessTimerRet)
		self.uninstallProcessTimer.start(100)		

	#def _checkMetaProtectionRet

	def _uninstallProcessTimerRet(self):

		if not UnInstallStack.flavourSelectorManager.disableMetaProtectionLaunched:
			UnInstallStack.flavourSelectorManager.disableMetaProtectionLaunched=True
			self.core.mainStack.currentCommand=UnInstallStack.flavourSelectorManager.getDisableProtectionCommand()
			self.core.mainStack.endCurrentCommand=True
		
		if UnInstallStack.flavourSelectorManager.disableMetaProtectionDone:
			if not self.pkgProcessed:
				if not self.endAction:
					self.pkgToSelect+=1
					if self.pkgToSelect<self.countLimit:
						self.pkgToProcess=UnInstallStack.flavourSelectorManager.flavourSelectedToRemove[self.pkgToSelect]
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
							
		
		if self.endAction:
			if not UnInstallStack.flavourSelectorManager.enableMetaProtectionLaunched:
				UnInstallStack.flavourSelectorManager.enableMetaProtectionLaunched=True
				self.core.mainStack.currentCommand=UnInstallStack.flavourSelectorManager.getEnableProtectionCommand()
				self.core.mainStack.feedbackCode=UnInstallStack.flavourSelectorManager.MSG_FEEDBACK_PROTECTION
				self.core.mainStack.endCurrentCommand=True
	
			if UnInstallStack.flavourSelectorManager.enableMetaProtectionDone:
				if self.core.mainStack.launchAutoRemove and not self.core.mainStack.enableInstallAction:
					if not UnInstallStack.flavourSelectorManager.autoRemoveLaunched:
						self.core.mainStack.feedbackCode=UnInstallStack.flavourSelectorManager.MSG_FEEDBACK_AUTOREMOVE
						UnInstallStack.flavourSelectorManager.autoRemoveLaunched=True
						self.core.mainStack.currentCommand=UnInstallStack.flavourSelectorManager.getAutoRemoveCommand()
						self.core.mainStack.endCurrentCommand=True

				else:
					UnInstallStack.flavourSelectorManager.autoRemoveLaunched=True
					UnInstallStack.flavourSelectorManager.autoRemoveDone=True

				if UnInstallStack.flavourSelectorManager.autoRemoveDone:		
					if self.totalError>0:
						self.showError=True

					UnInstallStack.flavourSelectorManager.flavourSelectedToRemove=[]
					UnInstallStack.flavourSelectorManager.wantToRemove=[]

					if self.core.mainStack.enableInstallAction:
						self.uninstallProcessTimer.stop()
						self.core.installStack.installProcess()
					else:
						self.core.mainStack.enableRemoveAction=False
						self.core.mainStack.isProgressBarVisible=False
						self.core.mainStack.isProcessRunning=False
						self.core.mainStack.endProcess=True
						self.core.mainStack.feedbackCode=""
						self.core.mainStack.enableApplyBtn=False
						self.core.flavourStack.enableFlavourList=True
						self.core.flavourStack.isAllInstalled=UnInstallStack.flavourSelectorManager.isAllInstalled()
						self.core.flavourStack.totalErrorInProcess=self.totalError
						self.uninstallProcessTimer.stop()
						self.core.mainStack.launchAutoRemove=False
						
						if self.showError:
							if self.countLimit==1:
								self.core.mainStack.showStatusMessage=[True,UnInstallStack.flavourSelectorManager.feedBackCheck[1],UnInstallStack.flavourSelectorManager.feedBackCheck[2]]
							else:
								self.core.mainStack.showStatusMessage=[True,UnInstallStack.flavourSelectorManager.ERROR_PARTIAL_UNINSTALL,"Error"]
						
						else:
							self.core.mainStack.showStatusMessage=[True,UnInstallStack.flavourSelectorManager.feedBackCheck[1],UnInstallStack.flavourSelectorManager.feedBackCheck[2]]
						

		if UnInstallStack.flavourSelectorManager.disableMetaProtectionLaunched:
			if not UnInstallStack.flavourSelectorManager.disableMetaProtectionDone:
				if not os.path.exists(UnInstallStack.flavourSelectorManager.tokenDisableMetaProtection[1]):
					UnInstallStack.flavourSelectorManager.disableMetaProtectionDone=True
			else:
				if UnInstallStack.flavourSelectorManager.removePkgLaunched:
					if not UnInstallStack.flavourSelectorManager.removePkgDone:
						if not os.path.exists(UnInstallStack.flavourSelectorManager.tokenUnInstall[1]):
							UnInstallStack.flavourSelectorManager.removePkgDone=True
		
		if UnInstallStack.flavourSelectorManager.enableMetaProtectionLaunched:
			if not UnInstallStack.flavourSelectorManager.enableMetaProtectionDone:
				if not os.path.exists(UnInstallStack.flavourSelectorManager.tokenEnableMetaProtection[1]):
					UnInstallStack.flavourSelectorManager.enableMetaProtectionDone=True
			else:
				if UnInstallStack.flavourSelectorManager.autoRemoveLaunched:
					if not UnInstallStack.flavourSelectorManager.autoRemoveDone:
						if not os.path.exists(UnInstallStack.flavourSelectorManager.tokenAutoRemove[1]):
							UnInstallStack.flavourSelectorManager.autoRemoveDone=True
		
	#def _uninstallProcessTimerRet

#class UnInstallStack

from . import Core

