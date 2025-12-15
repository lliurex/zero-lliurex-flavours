#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

signal.signal(signal.SIGINT, signal.SIG_DFL)

class InstallStack(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		InstallStack.flavourSelectorManager=self.core.flavourSelectorManager

	#def __init__

	def checkInternetConnection(self):

		if self.core.mainStack.enableInstallAction:
			self.core.mainStack.feedbackCode=InstallStack.flavourSelectorManager.MSG_FEEDBACK_INTERNET
			InstallStack.flavourSelectorManager.checkInternetConnection()
			self.checkConnectionTimer=QTimer()
			self.checkConnectionTimer.timeout.connect(self._checkConnectionTimerRet)
			self.checkConnectionTimer.start(1000)
		else:
			self.core.unInstallStack.unInstallProcess()

	#def checkInternetConnection

	def _checkConnectionTimerRet(self):

		InstallStack.flavourSelectorManager.getResultCheckConnection()
		if InstallStack.flavourSelectorManager.endCheck:
			self.checkConnectionTimer.stop()
			self.core.mainStack.feedbackCode=""
			if InstallStack.flavourSelectorManager.retConnection[0]:
				self.core.mainStack.isProgressBarVisible=False
				self.core.mainStack.endProcess=True
				self.core.mainStack.enableApplyBtn=True
				self.core.mainStack.showStatusMessage=[True,InstallStack.flavourSelectorManager.retConnection[1],"Error"]
				
			else:
				if self.core.mainStack.enableRemoveAction:
					self.core.unInstallStack.unInstallProcess()
				else:
					self.installProcess()

	#def _checkConnectionTimerRet

	def installProcess(self):

		self.totalError=0
		self.core.flavourStack.totalErrorInProcess=0
		self.core.mainStack.launchedProcess="install"
		self.core.mainStack.enableKonsole=True
		self._initInstallProcess()
		self.installProcessTimer=QTimer(None)
		self.installProcessTimer.timeout.connect(self._installProcessTimerRet)
		self.installProcessTimer.start(100)		

	#def _installProcess

	def _initInstallProcess(self):

		InstallStack.flavourSelectorManager.initInstallProcess()
		self.error=False
		self.showError=False
		self.endAction=False
		self.pkgProcessed=False
		countLimit=len(InstallStack.flavourSelectorManager.flavourSelectedToInstall)
		if countLimit==0:
			self.countLimit=1
		else:
			self.countLimit=countLimit

		self.pkgToSelect=-1
		self.pkgToProcess=""

	#def _initInstallProcess

	def _installProcessTimerRet(self):

		if not InstallStack.flavourSelectorManager.updateReposLaunched:
			self.core.mainStack.feedbackCode=InstallStack.flavourSelectorManager.MSG_FEEDBACK_INSTALL_REPOSITORIES
			InstallStack.flavourSelectorManager.updateReposLaunched=True
			self.core.mainStack.currentCommand=InstallStack.flavourSelectorManager.getUpdateReposCommand()
			self.core.mainStack.endCurrentCommand=True
		
		if InstallStack.flavourSelectorManager.updateReposDone:
			if not self.pkgProcessed:
				if not self.endAction:
					self.pkgToSelect+=1
					if self.pkgToSelect<self.countLimit:
						self.pkgToProcess=InstallStack.flavourSelectorManager.flavourSelectedToInstall[self.pkgToSelect]
						InstallStack.flavourSelectorManager.initPkgInstallProcess(self.pkgToProcess)
						self.core.flavourStack.updateResultFlavoursModel('start')
					else:
						self.endAction=True

				self.pkgProcessed=True

			if not self.endAction:
				if not InstallStack.flavourSelectorManager.installAppLaunched:
					self.core.mainStack.feedbackCode=InstallStack.flavourSelectorManager.MSG_FEEDBACK_INSTALL_RUN
					InstallStack.flavourSelectorManager.installAppLaunched=True
					self.core.mainStack.currentCommand=InstallStack.flavourSelectorManager.getInstallCommand(self.pkgToProcess)
					self.core.mainStack.endCurrentCommand=True

				if InstallStack.flavourSelectorManager.installAppDone:
					if not InstallStack.flavourSelectorManager.checkInstallLaunched:
						InstallStack.flavourSelectorManager.checkInstallLaunched=True
						InstallStack.flavourSelectorManager.checkInstall(self.pkgToProcess)

					if InstallStack.flavourSelectorManager.checkInstallDone:
						self.core.flavourStack.updateResultFlavoursModel('end')
						if InstallStack.flavourSelectorManager.feedBackCheck[0]:
							self.pkgProcessed=False
						else:
							self.error=True
							self.pkgProcessed=False
							self.totalError+=1
						
		if self.endAction:
			if self.core.mainStack.launchAutoRemove:
				if not InstallStack.flavourSelectorManager.autoRemoveLaunched:
					self.core.mainStack.feedbackCode=InstallStack.flavourSelectorManager.MSG_FEEDBACK_AUTOREMOVE
					InstallStack.flavourSelectorManager.autoRemoveLaunched=True
					self.core.mainStack.currentCommand=InstallStack.flavourSelectorManager.getAutoRemoveCommand()
					self.core.mainStack.endCurrentCommand=True
			else:
				InstallStack.flavourSelectorManager.autoRemoveLaunched=True
				InstallStack.flavourSelectorManager.autoRemoveDone=True

			if InstallStack.flavourSelectorManager.autoRemoveDone:
				if self.totalError>0:
					self.showError=True

				if self.showError:
					if InstallStack.flavourSelectorManager.errorInConflicts:
						self.core.mainStack.showStatusMessage=[True,InstallStack.flavourSelectorManager.ERROR_PROCESS_CONFLICTS,"Error"]	
					else:
						installError=True
						if self.core.mainStack.enableRemoveAction:
							if self.core.unInstallStack.showError:
								installError=False
								self.core.mainStack.showStatusMessage=[True,InstallStack.flavourSelectorManager.ERROR_PROCESS,"Error"]	

						if installError:
							if self.countLimit==1 and self.core.unInstallStack.countLimit==1:
								self.core.mainStack.showStatusMessage=[True,InstallStack.flavourSelectorManager.feedBackCheck[1],InstallStack.flavourSelectorManager.feedBackCheck[2]]
							else:
								self.core.mainStack.showStatusMessage=[True,InstallStack.flavourSelectorManager.ERROR_PARTIAL_INSTALL,"Error"]
				else:
					unInstallError=False
					if self.core.mainStack.enableRemoveAction:
						if self.core.unInstallStack.showError:
							unInstallError=True

					if not unInstallError:
						if not self.core.mainStack.enableRemoveAction:
							self.core.mainStack.showStatusMessage=[True,InstallStack.flavourSelectorManager.feedBackCheck[1],InstallStack.flavourSelectorManager.feedBackCheck[2]]
						else:
							self.core.mainStack.showStatusMessage=[True,InstallStack.flavourSelectorManager.SUCCESS_PROCESS,"Ok"]
					else:
						if self.core.unInstallStack.countLimit==1:
								self.core.mainStack.showStatusMessage=[True,InstallStack.flavourSelectorManager.feedBackCheck[1],InstallStack.flavourSelectorManager.feedBackCheck[2]]
						else:
							self.core.mainStack.showStatusMessage=[True,InstallStack.flavourSelectorManager.ERROR_PARTIAL_UNINSTALL,"Error"]

				self.core.mainStack.isProgressBarVisible=False
				self.core.mainStack.endProcess=True
				self.core.mainStack.feedbackCode=""
				self.core.mainStack.isProcessRunning=False
				InstallStack.flavourSelectorManager.updateTags()
				self.core.flavourStack.isAllInstalled=InstallStack.flavourSelectorManager.isAllInstalled()
				self.core.flavourStack.enableFlavourList=True
				self.core.mainStack.enableApplyBtn=False
				self.installProcessTimer.stop()
				InstallStack.flavourSelectorManager.flavourSelectedToInstall=[]
				InstallStack.flavourSelectorManager.tagsToAdd=[]
				InstallStack.flavourSelectorManager.tagsToRemove=[]
				if self.core.mainStack.enableRemoveAction:
					self.core.flavourStack.totalErrorInProcess=self.totalError+self.core.unInstallStack.totalError
				else:
					self.core.mainStack.totalErrorInProcess=self.totalError
				self.core.mainStack.enableInstallAction=False
				self.core.mainStack.enableRemoveAction=False
				self.core.mainStack.launchAutoRemove=False		
		
		if InstallStack.flavourSelectorManager.updateReposLaunched:
			if not InstallStack.flavourSelectorManager.updateReposDone:
				if not os.path.exists(InstallStack.flavourSelectorManager.tokenUpdaterepos[1]):
					InstallStack.flavourSelectorManager.updateReposDone=True

		if self.pkgProcessed:
			if InstallStack.flavourSelectorManager.installAppLaunched:
				if not InstallStack.flavourSelectorManager.installAppDone:
					if not os.path.exists(InstallStack.flavourSelectorManager.tokenInstall[1]):
						InstallStack.flavourSelectorManager.installAppDone=True
				else:
					if InstallStack.flavourSelectorManager.autoRemoveLaunched:
						if not InstallStack.flavourSelectorManager.autoRemoveDone:
							if not os.path.exists(InstallStack.flavourSelectorManager.tokenAutoRemove[1]):
								InstallStack.flavourSelectorManager.autoRemoveDone=True
	
	#def _installProcessTimerRet

#class InstallStack

from . import Core

