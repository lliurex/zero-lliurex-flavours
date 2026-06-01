#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QTimer
import os
import signal
import sys


signal.signal(signal.SIGINT, signal.SIG_DFL)

class UnInstallStack(QObject):

	GLOBALTOKENS = [
		("disableMetaProtection", "tokenDisableMetaProtection"),
	]

	PROCESSPKGTOKENS=[
		("removePkg", "tokenUnInstall"),
		("autoRemove", "tokenAutoRemove"),
		("enableMetaProtection","tokenEnableMetaProtection")
	]	


	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.countLimit=1
		self.flavourManager=self.core.flavourSelectorManager

	#def __init__

	def unInstallProcess(self):

		self.core.mainStack.launchedProcess="uninstall"
		self.core.mainStack.enableKonsole=True
		self.core.mainStack.feedbackCode=self.flavourManager.MSG_FEEDBACK_UNINSTALL_RUN
		self.core.flavourStack.totalErrorInProcess=0
		self.endAction=False
		self.pkgProcessed=False
		self.error=False
		self.totalError=0
		self.showError=False
		countLimit=len(self.flavourManager.flavourSelectedToRemove)
		if countLimit==0:
			self.countLimit=1
		else:
			self.countLimit=countLimit

		self.pkgToSelect=-1
		self.pkgToProcess=""
		self.flavourManager.preUninstallProcess()
		self.uninstallProcessTimer=QTimer(None)
		self.uninstallProcessTimer.timeout.connect(self._uninstallProcessTimerRet)
		self.uninstallProcessTimer.start(100)		

	#def _checkMetaProtectionRet

	def _uninstallProcessTimerRet(self):

		if not self.flavourManager.disableMetaProtectionLaunched:
			self.flavourManager.disableMetaProtectionLaunched=True
			self.core.mainStack.currentCommand=self.flavourManager.getDisableProtectionCommand()
			self.core.mainStack.endCurrentCommand=True
		
		if not self.flavourManager.disableMetaProtectionDone:
			return self._checkProcessTokens()

		if not self.pkgProcessed:
			if not self.endAction:
				self.pkgToSelect+=1
				if self.pkgToSelect<self.countLimit:
					self.pkgToProcess=self.flavourManager.flavourSelectedToRemove[self.pkgToSelect]
					self.flavourManager.initUnInstallProcess(self.pkgToProcess)
					self.core.flavourStack.updateResultFlavoursModel('start')
					if not self.flavourManager.removePkgLaunched:
						self.flavourManager.removePkgLaunched=True
						self.core.mainStack.currentCommand=self.flavourManager.getUnInstallCommand(self.pkgToProcess)
						self.core.mainStack.endCurrentCommand=True
				else:
					self.endAction=True

				self.pkgProcessed=True

		if not self.endAction:
			if not self.flavourManager.removePkgDone:
				return self._checkProcessTokens()

			if not self.flavourManager.checkRemoveLaunched:
				self.flavourManager.checkRemoveLaunched=True
				self.flavourManager.checkRemove(self.pkgToProcess)

			if not self.flavourManager.checkRemoveDone:
				return 

			self.core.flavourStack.updateResultFlavoursModel("end")
			if not self.flavourManager.feedBackCheck.get("status"):
				self.error=True
				self.totalError+=1
			self.pkgProcessed=False
							
		
		if self.endAction:
			if not self.flavourManager.enableMetaProtectionLaunched:
				self.flavourManager.enableMetaProtectionLaunched=True
				self.core.mainStack.currentCommand=self.flavourManager.getEnableProtectionCommand()
				self.core.mainStack.feedbackCode=self.flavourManager.MSG_FEEDBACK_PROTECTION
				self.core.mainStack.endCurrentCommand=True
	
			if not self.flavourManager.enableMetaProtectionDone:
				return self._checkProcessTokens()

			if self.core.mainStack.launchAutoRemove and not self.core.mainStack.enableInstallAction:
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

			self.uninstallProcessTimer.stop()
			self._endUninstallProcess()

	#def _uninstallProcessTimerRet

	def _endUninstallProcess(self):

		if self.totalError>0:
			self.showError=True

		self.flavourManager.flavourSelectedToRemove=[]
		self.flavourManager.wantToRemove=[]

		if self.core.mainStack.enableInstallAction:
			self.core.installStack.installProcess()
		else:
			self.core.mainStack.enableRemoveAction=False
			self.core.mainStack.isProgressBarVisible=False
			self.core.mainStack.isProcessRunning=False
			self.core.mainStack.endProcess=True
			self.core.mainStack.feedbackCode=""
			self.core.mainStack.enableApplyBtn=False
			self.core.flavourStack.enableFlavourList=True
			self.core.flavourStack.isAllInstalled=self.flavourManager.isAllInstalled()
			self.core.flavourStack.totalErrorInProcess=self.totalError
			self.flavourManager.updateTags()
			self.flavourManager.tagsToRemove=[]

			self.core.mainStack.launchAutoRemove=False
			
			if self.showError:
				if self.countLimit==1:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.feedBackCheck.get("msgCode"),"type":self.flavourManager.feedBackCheck.get("type")}
				else:
					self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.ERROR_PARTIAL_UNINSTALL,"type":self.flavourManager.KIRIGAMI_MSG_ERROR}
			
			else:
				self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.feedBackCheck.get("msgCode"),"type":self.flavourManager.feedBackCheck.get("type")}
						

	#def _uninstallProcessTimerRet

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


#class UnInstallStack

from . import Core

