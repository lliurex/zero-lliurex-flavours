#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import subprocess
import threading
import signal
import copy
import time
import sys
import pwd

signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherInfo(QThread):

	infoGathered=Signal()

	def __init__(self,manager):

		super().__init__()
		self.manager=manager
		
	#def __init__
		
	def run(self,*args):
		
		self.manager.getSupportedFlavour()
		self.infoGathered.emit()

	#def run

#class GatherInfo

class Bridge(QObject):

	currentStackChanged=Signal()
	currentOptionsStackChanged=Signal()
	feedbackCodeChanged=Signal()
	enableApplyBtnChanged=Signal()
	isProcessRunningChanged=Signal()
	showStatusMessageChanged=Signal()
	enableInstallActionChanged=Signal()
	enableRemoveActionChanged=Signal()
	enableCartActionChanged=Signal()
	selectedCartChanged=Signal()
	endProcessChanged=Signal()
	endCurrentCommandChanged=Signal()
	currentCommandChanged=Signal()
	enableKonsoleChanged=Signal()
	launchedProcessChanged=Signal()
	isProgressBarVisibleChanged=Signal()
	closeGuiChanged=Signal()

	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.flavourManager=self.core.flavourSelectorManager
		self._closeGui=False
		self._currentStack=0
		self._currentOptionsStack=0
		self._showStatusMessage={"show":False,"msgCode":"","type":""}
		self._feedbackCode=""
		self._isProcessRunning=False
		self._enableApplyBtn=False
		self._endProcess=True
		self._endCurrentCommand=False
		self._currentCommand=""
		self._enableKonsole=False
		self._launchedProcess=""
		self._isProgressBarVisible=False
		self._enableInstallAction=False
		self._enableRemoveAction=False
		self._enableCartAction=False
		self._selectedCart=1
		self.moveToStack=""
		self.waitMaxRetry=1
		self.waitRetryCount=0
		self.launchAutoRemove=False
		self.launchCartConfiguration=False
		self.runPkexec=self.flavourManager.runPkexec

	#def __init__

	@Property(int, notify=currentStackChanged)
	def currentStack(self):

		return self._currentStack

	#def currentStack

	@currentStack.setter
	def currentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.currentStackChanged.emit()

	#def currentStack

	@Property(int, notify=currentOptionsStackChanged)
	def currentOptionsStack(self):

		return self._currentOptionsStack

	#def currentOptionsStack

	@currentOptionsStack.setter
	def currentOptionsStack(self,currentOptionsStack):

		if self._currentOptionsStack!=currentOptionsStack:
			self._currentOptionsStack=currentOptionsStack
			self.currentOptionsStackChanged.emit()

	#def currentOptionsStack

	@Property(int, notify=feedbackCodeChanged)
	def feedbackCode(self):

		return self._feedbackCode

	#def feedbackCode

	@feedbackCode.setter
	def feedbackCode(self,feedbackCode):

		if self._feedbackCode!=feedbackCode:
			self._feedbackCode=feedbackCode
			self.feedbackCodeChanged.emit()

	#def feedbackCode

	@Property(bool, notify=enableApplyBtnChanged)
	def enableApplyBtn(self):

		return self._enableApplyBtn

	#def enableApplyBtn

	@enableApplyBtn.setter
	def enableApplyBtn(self,enableApplyBtn):

		if self._enableApplyBtn!=enableApplyBtn:
			self._enableApplyBtn=enableApplyBtn
			self.enableApplyBtnChanged.emit()

	#def enableApplyBtn

	@Property(bool, notify=isProcessRunningChanged)
	def isProcessRunning(self):

		return self._isProcessRunning

	#def isProcessRunning

	@isProcessRunning.setter
	def isProcessRunning(self, isProcessRunning):

		if self._isProcessRunning!=isProcessRunning:
			self._isProcessRunning=isProcessRunning
			self.isProcessRunningChanged.emit()

	#def isProcessRunning

	@Property(dict, notify=showStatusMessageChanged)
	def showStatusMessage(self):

		return self._showStatusMessage

	#def showStatusMessage

	@showStatusMessage.setter
	def showStatusMessage(self,showStatusMessage):

		if self._showStatusMessage!=showStatusMessage:
			self._showStatusMessage=showStatusMessage
			self.showStatusMessageChanged.emit()

	#def showStatusMessage

	@Property(bool, notify=enableInstallActionChanged)
	def enableInstallAction(self):

		return self._enableInstallAction

	#def enableInstallAction

	@enableInstallAction.setter
	def enableInstallAction(self,enableInstallAction):

		if self._enableInstallAction!=enableInstallAction:
			self._enableInstallAction=enableInstallAction
			self.enableInstallActionChanged.emit()

	#def enableInstallAction

	@Property(bool, notify=enableRemoveActionChanged)
	def enableRemoveAction(self):

		return self._enableRemoveAction

	#def enableRemoveAction

	@enableRemoveAction.setter
	def enableRemoveAction(self,enableRemoveAction):

		if self._enableRemoveAction!=enableRemoveAction:
			self._enableRemoveAction=enableRemoveAction
			self.enableRemoveActionChanged.emit()

	#def enableRemoveAction

	@Property(bool, notify=enableCartActionChanged)
	def enableCartAction(self):

		return self._enableCartAction

	#def enableCartAction

	@enableCartAction.setter
	def enableCartAction(self,enableCartAction):

		if self._enableCartAction!=enableCartAction:
			self._enableCartAction=enableCartAction
			self.enableCartActionChanged.emit()

	#def enableCartAction	
	
	@Property(int, notify=selectedCartChanged)
	def selectedCart(self):

		return self._selectedCart

	#def selectedCart

	@selectedCart.setter
	def selectedCart(self,selectedCart):

		if self._selectedCart!=selectedCart:
			self._selectedCart=selectedCart
			self.selectedCartChanged.emit()

	#def selectedCart

	@Property(bool, notify=endProcessChanged)
	def endProcess(self):

		return self._endProcess

	#def endProcess	

	@endProcess.setter
	def endProcess(self,endProcess):
		
		if self._endProcess!=endProcess:
			self._endProcess=endProcess		
			self.endProcessChanged.emit()

	#def endProcess

	@Property(bool, notify=endCurrentCommandChanged)
	def endCurrentCommand(self):

		return self._endCurrentCommand

	#def endCurrentCommand

	@endCurrentCommand.setter
	def endCurrentCommand(self,endCurrentCommand):
		
		if self._endCurrentCommand!=endCurrentCommand:
			self._endCurrentCommand=endCurrentCommand		
			self.endCurrentCommandChanged.emit()

	#def endCurrentCommand

	@Property(str, notify=currentCommandChanged)
	def currentCommand(self):

		return self._currentCommand

	#def currentCommand

	@currentCommand.setter
	def currentCommand(self,currentCommand):
		
		if self._currentCommand!=currentCommand:
			self._currentCommand=currentCommand		
			self.currentCommandChanged.emit()

	#def currentCommand
	
	@Property(bool, notify=enableKonsoleChanged)
	def enableKonsole(self):

		return self._enableKonsole

	#def enableKonsole

	@enableKonsole.setter
	def enableKonsole(self,enableKonsole):

		if self._enableKonsole!=enableKonsole:
			self._enableKonsole=enableKonsole
			self.enableKonsoleChanged.emit()

	#def enableKonsole
	
	@Property(str, notify=launchedProcessChanged)
	def launchedProcess(self):

		return self._launchedProcess

	#def lLaunchedProcess

	@launchedProcess.setter
	def launchedProcess(self,launchedProcess):

		if self._launchedProcess!=launchedProcess:
			self._launchedProcess=launchedProcess
			self.launchedProcessChanged.emit()

	#def launchedProcess

	@Property(bool, notify=isProgressBarVisibleChanged)
	def isProgressBarVisible(self):

		return self._isProgressBarVisible

	#def isProgressBarVisible

	@isProgressBarVisible.setter
	def isProgressBarVisible(self,isProgressBarVisible):

		if self._isProgressBarVisible!=isProgressBarVisible:
			self._isProgressBarVisible=isProgressBarVisible
			self.isProgressBarVisibleChanged.emit()

	#def isProgressBarVisible

	@Property(bool, notify=closeGuiChanged)
	def closeGui(self):

		return self._closeGui

	#def closeGui	

	@closeGui.setter
	def closeGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.closeGuiChanged.emit()

	#def closeGui

	def initBridge(self):

		self.gatherInfoT=GatherInfo(self.flavourManager)
		self.gatherInfoT.start()
		self.gatherInfoT.infoGathered.connect(self._gatherInfoRet)
		self.gatherInfoT.finished.connect(self.gatherInfoT.deleteLater)

	#def initBridge

	@Slot()
	def _gatherInfoRet(self):

		self.core.flavourStack.getInfo()
		self.currentStack=2

	#def _gatherInfoRet

	@Slot(bool)
	def onAutoRemoveChecked(self,value):

		self.launchAutoRemove=value

	#def onAutoRemoveChecked

	@Slot(bool)
	def onConfigureCartChecked(self,value):

		self.launchCartConfiguration=value

	#def onConfigureCartChecked

	@Slot(int)
	def updateCart(self,value):

		self.selectedCart=int(value)+1

		if self.selectedCart==1:
			self.launchCartConfiguration=False

	#def updateCart

	@Slot()
	def getNewCommand(self):
		
		self.endCurrentCommand=False
		
	#def getNewCommand

	@Slot()
	def launchChangeProcess(self):

		self.showStatusMessage={"show":False,"msgCode":"","type":""}
		self.core.flavourStack.enableFlavourList=False
		self.endProcess=False
		self.enableApplyBtn=False
		self.isProgressBarVisible=True
		self.isProcessRunning=True
		if self.selectedCart==1:
			self.launchCartConfiguration=False
		self.flavourManager.initLog(self.launchAutoRemove,self.launchCartConfiguration,self.selectedCart)
		self.core.installStack.checkInternetConnection()

	#def launchChangeProcess

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.currentOptionsStack=stack

	#de manageTransitions

	@Slot()
	def openHelp(self):

		self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Configurar-sabores-en-LliureX-en-el-nuevo-modelo'

		if self.runPkexec:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.helpCmd=f"su -c '{self.helpCmd}' {user}"
		else:
			self.helpCmd=f"su -c '{self.helpCmd}' $USER"

		self.openHelp_t=threading.Thread(target=self._openHelpRet)
		self.openHelp_t.daemon=True
		self.openHelp_t.start()

	#def openHelp

	def _openHelpRet(self):

		subprocess.run(self.helpCmd,shell=True)

	#def _openHelpRet

	@Slot()
	def closeApplication(self):

		if self.endProcess:
			self.closeGui=True
		else:
			self.closeGui=False

	#def closeApplication

#class Bridge

from . import Core

