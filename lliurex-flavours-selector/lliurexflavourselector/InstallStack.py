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

class InstallStack(QObject):

	GLOBALTOKENS = [
		("updateRepos", "tokenUpdaterepos"),
	]

	PROCESSPKGTOKENS=[
		("updateRepos", "tokenUpdaterepos"),
		("installApp", "tokenInstall"),
		("autoRemove", "tokenAutoRemove"),
		("configureCart","tokenConfigureCart")
	]	

	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.flavourManager=self.core.flavourSelectorManager

	#def __init__

	def checkInternetConnection(self):

		if self.core.mainStack.enableInstallAction:
			self.core.mainStack.feedbackCode=self.flavourManager.MSG_FEEDBACK_INTERNET
			self.flavourManager.checkInternetConnection()
			self.checkConnectionTimer=QTimer()
			self.checkConnectionTimer.timeout.connect(self._checkConnectionTimerRet)
			self.checkConnectionTimer.start(1000)
		else:
			self.core.unInstallStack.unInstallProcess()

	#def checkInternetConnection

	def _checkConnectionTimerRet(self):

		self.flavourManager.getResultCheckConnection()
		if not self.flavourManager.endCheck:
			return

		self.checkConnectionTimer.stop()
		self.core.mainStack.feedbackCode=""

		retConnection=self.flavourManager.retConnection

		if not retConnection.get("status"):
			self.core.mainStack.isProgressBarVisible=False
			self.core.mainStack.endProcess=True
			self.core.mainStack.enableApplyBtn=True	
			self.core.mainStack.showStatusMessage={"show":True,"msgCode":retConnection.get("msgCode"),"type":self.flavourManager.retConnection.get("type")}
				
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

		self.flavourManager.initInstallProcess()
		self.error=False
		self.showError=False
		self.endAction=False
		self.pkgProcessed=False
		countLimit=len(self.flavourManager.flavourSelectedToInstall)
		if countLimit==0:
			self.countLimit=1
		else:
			self.countLimit=countLimit

		self.pkgToSelect=-1
		self.pkgToProcess=""

	#def _initInstallProcess

	def _installProcessTimerRet(self):

		if not self.flavourManager.updateReposLaunched:
			self.core.mainStack.feedbackCode=self.flavourManager.MSG_FEEDBACK_INSTALL_REPOSITORIES
			self.flavourManager.updateReposLaunched=True
			self.core.mainStack.currentCommand=self.flavourManager.getUpdateReposCommand()
			self.core.mainStack.endCurrentCommand=True
		
		if not self.flavourManager.updateReposDone:
			return self._checkProcessTokens()
		
		if not self.pkgProcessed:
			if not self.endAction:
				self.pkgToSelect+=1
				if self.pkgToSelect<self.countLimit:
					self.pkgToProcess=self.flavourManager.flavourSelectedToInstall[self.pkgToSelect]
					self.flavourManager.initPkgInstallProcess(self.pkgToProcess)
					self.core.flavourStack.updateResultFlavoursModel('start')
				else:
					self.endAction=True

			self.pkgProcessed=True

		if not self.endAction:
			if not self.flavourManager.installAppLaunched:
				self.core.mainStack.feedbackCode=self.flavourManager.MSG_FEEDBACK_INSTALL_RUN
				self.flavourManager.installAppLaunched=True
				self.core.mainStack.currentCommand=self.flavourManager.getInstallCommand(self.pkgToProcess)
				self.core.mainStack.endCurrentCommand=True

			if not self.flavourManager.installAppDone:
				return self._checkProcessTokens()

			if not self.flavourManager.checkInstallLaunched:
				self.flavourManager.checkInstallLaunched=True
				self.flavourManager.checkInstall(self.pkgToProcess)

			if not self.flavourManager.checkInstallDone:
				return

			self.core.flavourStack.updateResultFlavoursModel('end')
			if self.flavourManager.feedBackCheck.get("status"):
				self.pkgProcessed=False
			else:
				self.error=True
				self.pkgProcessed=False
				self.totalError+=1
						
		if self.endAction:
			if self.core.mainStack.launchAutoRemove:
				if not self.flavourManager.autoRemoveLaunched:
					self.core.mainStack.feedbackCode=self.flavourManager.MSG_FEEDBACK_AUTOREMOVE
					self.flavourManager.autoRemoveLaunched=True
					self.core.mainStack.currentCommand=self.flavourManager.getAutoRemoveCommand()
					self.core.mainStack.endCurrentCommand=True
			else:
				self.flavourManager.autoRemoveLaunched=True
				self.flavourManager.autoRemoveDone=True

			if not self.flavourManager.autoRemoveDone:
				return self._checkProcessTokens()

			if self.core.mainStack.launchCartConfiguration:
				if not self.flavourManager.configureCartLaunched:
					self.core.mainStack.feedbackCode=self.flavourManager.MSG_FEEDBACK_CONFIGURATION_CART
					self.flavourManager.configureCartLaunched=True
					self.core.mainStack.currentCommand=self.flavourManager.getConfigurationCartCommand()
					self.core.mainStack.endCurrentCommand=True
			else:
				self.flavourManager.configureCartLaunched=True
				self.flavourManager.configureCartDone=True
				
			if not self.flavourManager.configureCartDone:
				return self._checkProcessTokens()

			self.installProcessTimer.stop()
			self._endInstallProcess()

	#def _installProcessTimerRet

	def _endInstallProcess(self):

		if self.totalError>0:
			self.showError=True

		unInstallError=self.core.mainStack.enableRemoveAction and self.core.unInstallStack.showError

		if self.showError:
			if self.flavourManager.errorInConflicts:
				self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.ERROR_PROCESS_CONFLICTS,"type":self.flavourManager.KIRIGAMI_MSG_ERROR}	
			else:
				if unInstallError:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.ERROR_PROCESS,"type":self.flavourManager.KIRIGAMI_MSG_ERROR}	

				elif self.countLimit==1 and self.core.unInstallStack.countLimit==1:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.feedBackCheck.get("msgCode"),"type":self.flavourManager.feedBackCheck.get("type")}
				else:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.ERROR_PARTIAL_INSTALL,"type":self.flavourManager.KIRIGAMI_MSG_ERROR}
		else:
			if not unInstallError:
				if not self.core.mainStack.enableRemoveAction:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.feedBackCheck.get("msgCode"),"type":self.flavourManager.feedBackCheck.get("type")}
				else:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.SUCCESS_PROCESS,"type":self.flavourManager.KIRIGAMI_MSG_OK}
			else:
				if self.core.unInstallStack.countLimit==1:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.ERROR_PROCESS,"type":self.flavourManager.KIRIGAMI_MSG_ERROR}	
				else:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.ERROR_PARTIAL_UNINSTALL,"type":self.flavourManager.KIRIGAMI_MSG_ERROR}

		self.core.mainStack.isProgressBarVisible=False
		self.core.mainStack.endProcess=True
		self.core.mainStack.feedbackCode=""
		self.core.mainStack.isProcessRunning=False

		self.flavourManager.updateTags()

		self.core.flavourStack.isAllInstalled=self.flavourManager.isAllInstalled()
		self.core.flavourStack.enableFlavourList=True
		self.core.mainStack.enableApplyBtn=False
		self.flavourManager.flavourSelectedToInstall=[]
		self.flavourManager.tagsToAdd=[]
		self.flavourManager.tagsToRemove=[]

		if self.core.mainStack.enableRemoveAction:
			self.core.flavourStack.totalErrorInProcess=self.totalError+self.core.unInstallStack.totalError
		else:
			self.core.mainStack.totalErrorInProcess=self.totalError
		
		self.core.mainStack.enableInstallAction=False
		self.core.mainStack.enableRemoveAction=False
		self.core.mainStack.launchAutoRemove=False
		self.core.mainStack.enableCartAction=False
		self.core.mainStack.selectedCart=1		
		
	#def _installProcessTimerRet

	def _checkProcessTokens(self):

		if not self.pkgProcessed:
			for prefix, token in self.GLOBALTOKENS:
				if getattr(self.flavourManager, f"{prefix}Launched") and not getattr(self.flavourManager, f"{prefix}Done"):
					tmpToken=getattr(self.flavourManager,token)
					if not os.path.exists(tmpToken):
						setattr(self.flavourManager, f"{prefix}Done", True)
		else:
			for prefix, token in self.PROCESSPKGTOKENS:
				if getattr(self.flavourManager, f"{prefix}Launched") and not getattr(self.flavourManager, f"{prefix}Done"):
					tmpToken=getattr(self.flavourManager,token)
					if not os.path.exists(tmpToken):
						setattr(self.flavourManager, f"{prefix}Done", True)
			
	#def _checkProcessTokens

#class InstallStack

from . import Core

