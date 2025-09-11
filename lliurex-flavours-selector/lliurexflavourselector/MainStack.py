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

class GatherInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		
	#def __init__
		
	def run(self,*args):
		
		ret=Bridge.flavourSelectorManager.getSupportedFlavour()

	#def run

#class GatherInfo

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.flavourSelectorManager=self.core.flavourSelectorManager
		self._closeGui=False
		self._closePopUp=[True,""]
		self._currentStack=0
		self._currentOptionsStack=0
		self._showStatusMessage=[False,"","Ok"]
		self._feedbackCode=""
		self._isProcessRunning=False
		self._enableApplyBtn=False
		self._enableRemoveBtn=False
		self._showRemoveBtn=False
		self._endProcess=True
		self._endCurrentCommand=False
		self._currentCommand=""
		self._enableKonsole=False
		self._launchedProcess=""
		self._isProgressBarVisible=False
		self._runPkexec=Bridge.flavourSelectorManager.runPkexec
		self.moveToStack=""
		self.waitMaxRetry=1
		self.waitRetryCount=0

	#def __init__

	def initBridge(self):

		self.gatherInfoT=GatherInfo()
		self.gatherInfoT.start()
		self.gatherInfoT.finished.connect(self._gatherInfoRet)

	#def initBridge

	def _gatherInfoRet(self):

		self.core.flavourStack.getInfo()
		self.manageRemoveBtn()
		self.currentStack=2

	#def _gatherInfoRet

	def _getCurrentStack(self):

		return self._currentStack

	#def _getCurrentStack

	def _setCurrentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.on_currentStack.emit()

	#def _setCurrentStack

	def _getCurrentOptionsStack(self):

		return self._currentOptionsStack

	#def _getCurrentOptionsStack

	def _setCurrentOptionsStack(self,currentOptionsStack):

		if self._currentOptionsStack!=currentOptionsStack:
			self._currentOptionsStack=currentOptionsStack
			self.on_currentOptionsStack.emit()

	#def _setCurrentOptionsStack

	def _getFeedbackCode(self):

		return self._feedbackCode

	#def _getFeedbackCode

	def _setFeedbackCode(self,feedbackCode):

		if self._feedbackCode!=feedbackCode:
			self._feedbackCode=feedbackCode
			self.on_feedbackCode.emit()

	#def _setFeedbackCode

	def _getEnableApplyBtn(self):

		return self._enableApplyBtn

	#def _getEnableApplyBtn

	def _setEnableApplyBtn(self,enableApplyBtn):

		if self._enableApplyBtn!=enableApplyBtn:
			self._enableApplyBtn=enableApplyBtn
			self.on_enableApplyBtn.emit()

	#def _setEnableApplyBtn

	def _getEnableRemoveBtn(self):

		return self._enableRemoveBtn

	#def _getEnableRemoveBtn

	def _setEnableRemoveBtn(self,enableRemoveBtn):

		if self._enableRemoveBtn!=enableRemoveBtn:
			self._enableRemoveBtn=enableRemoveBtn
			self.on_enableRemoveBtn.emit()

	#def _setEnableRemoveBtn

	def _getShowRemoveBtn(self):

		return self._showRemoveBtn

	#def _getShowRemoveBtn

	def _setShowRemoveBtn(self,showRemoveBtn):

		if self._showRemoveBtn!=showRemoveBtn:
			self._showRemoveBtn=showRemoveBtn
			self.on_showRemoveBtn.emit()

	#def _setShowRemoveBtn

	def _getIsProcessRunning(self):

		return self._isProcessRunning

	#def _getIsProcessRunning

	def _setIsProcessRunning(self, isProcessRunning):

		if self._isProcessRunning!=isProcessRunning:
			self._isProcessRunning=isProcessRunning
			self.on_isProcessRunning.emit()

	#def _setIsProcessRunning

	def _getShowStatusMessage(self):

		return self._showStatusMessage

	#def _getShowStatusMessage

	def _setShowStatusMessage(self,showStatusMessage):

		if self._showStatusMessage!=showStatusMessage:
			self._showStatusMessage=showStatusMessage
			self.on_showStatusMessage.emit()

	#def _setShowStatusMessage

	def _getClosePopUp(self):

		return self._closePopUp

	#def _getClosePopUp

	def _setClosePopUp(self,closePopUp):

		if self._closePopUp!=closePopUp:
			self._closePopUp=closePopUp
			self.on_closePopUp.emit()

	#def _setClosePopUp

	def _getEndProcess(self):

		return self._endProcess

	#def _getEndProcess	

	def _setEndProcess(self,endProcess):
		
		if self._endProcess!=endProcess:
			self._endProcess=endProcess		
			self.on_endProcess.emit()

	#def _setEndProcess

	def _getEndCurrentCommand(self):

		return self._endCurrentCommand

	#def _getEndCurrentCommand

	def _setEndCurrentCommand(self,endCurrentCommand):
		
		if self._endCurrentCommand!=endCurrentCommand:
			self._endCurrentCommand=endCurrentCommand		
			self.on_endCurrentCommand.emit()

	#def _setEndCurrentCommand

	def _getCurrentCommand(self):

		return self._currentCommand

	#def _getCurrentCommand

	def _setCurrentCommand(self,currentCommand):
		
		if self._currentCommand!=currentCommand:
			self._currentCommand=currentCommand		
			self.on_currentCommand.emit()

	#def _setCurrentCommand

	def _getEnableKonsole(self):

		return self._enableKonsole

	#def _getEnableKonsole

	def _setEnableKonsole(self,enableKonsole):

		if self._enableKonsole!=enableKonsole:
			self._enableKonsole=enableKonsole
			self.on_enableKonsole.emit()

	#def _setEnableKonsole

	def _getLaunchedProcess(self):

		return self._launchedProcess

	#def _getLaunchedProcess

	def _setLaunchedProcess(self,launchedProcess):

		if self._launchedProcess!=launchedProcess:
			self._launchedProcess=launchedProcess
			self.on_launchedProcess.emit()

	#def _setLaunchedProcess

	def _getIsProgressBarVisible(self):

		return self._isProgressBarVisible

	#def _getIsProgressBarVisible

	def _setIsProgressBarVisible(self,isProgressBarVisible):

		if self._isProgressBarVisible!=isProgressBarVisible:
			self._isProgressBarVisible=isProgressBarVisible
			self.on_isProgressBarVisible.emit()

	#def _setIsProgressBarVisible

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.on_closeGui.emit()

	#def _setCloseGui

	def _getRunPkexec(self):

		return self._runPkexec

	#def _getRunPkexec

	@Slot()
	def getNewCommand(self):
		
		self.endCurrentCommand=False
		
	#def getNewCommand

	def manageRemoveBtn(self):

		match=False
		
		if len(Bridge.flavourSelectorManager.pkgsInstalled)-Bridge.flavourSelectorManager.nonManagedPkg:
			self.showRemoveBtn=True
		else:
			self.showRemoveBtn=False
		
		for item in Bridge.flavourSelectorManager.flavourSelected:
			if item in Bridge.flavourSelectorManager.pkgsInstalled:
				match=True
				break
		
		if match:
			self.enableRemoveBtn=True
		else:
			self.enableRemoveBtn=False

	#def manageRemoveBtn

	@Slot()
	def launchInstallProcess(self):

		self.showStatusMessage=[False,"","Ok"]
		self.core.flavourStack.enableJavaList=False
		self.core.flavourStack.filterStatusValue="all"
		self.endProcess=False
		self.enableApplyBtn=False
		self.enableRemoveBtn=False
		self.isProgressBarVisible=True
		self.isProcessRunning=True
		self.launchedProcess="install"
		self.enableKonsole=True
		self.feedbackCode=Bridge.flavourSelectorManager.MSG_FEEDBACK_INTERNET
		self.core.installStack.checkInternetConnection()
	
	#def launchInstallProcess

	@Slot()
	def launchUnInstallProcess(self):

		self.showStatusMessage=[False,"","Ok"]
		self.core.flavourStack.enableJavaList=False
		self.core.flavourStack.filterStatusValue="all"
		self.endProcess=False
		self.enableApplyBtn=False
		self.enableRemoveBtn=False
		self.launchedProcess="uninstall"
		self.enableKonsole=True
		self.feedbackCode=Bridge.flavourSelectorManager.MSG_FEEDBACK_UNINSTALL_RUN
		self.isProcessRunning=True
		self.isProgressBarVisible=True
		self.core.unInstallStack.unInstallProcess()

	#def launchUnInstallProcess

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionsStack!=stack:
			self.currentOptionsStack=stack

	#de manageTransitions

	@Slot()
	def openHelp(self):

		self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=LliureX+Flavours+Selector'

		if self._runPkexec:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.helpCmd="su -c '%s' %s"%(self.helpCmd,user)
		else:
			self.helpCmd="su -c '%s' $USER"%self.helpCmd
		
		self.openHelp_t=threading.Thread(target=self._openHelpRet)
		self.openHelp_t.daemon=True
		self.openHelp_t.start()

	#def openHelp

	def _openHelpRet(self):

		os.system(self.helpCmd)

	#def _openHelpRet

	@Slot()
	def closeApplication(self):

		if self.endProcess:
			self.closeGui=True
		else:
			self.closeGui=False

	#def closeApplication

	
	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_currentOptionsStack=Signal()
	currentOptionsStack=Property(int,_getCurrentOptionsStack,_setCurrentOptionsStack, notify=on_currentOptionsStack)
	
	on_feedbackCode=Signal()
	feedbackCode=Property(int,_getFeedbackCode,_setFeedbackCode,notify=on_feedbackCode)

	on_enableApplyBtn=Signal()
	enableApplyBtn=Property(bool,_getEnableApplyBtn,_setEnableApplyBtn,notify=on_enableApplyBtn)

	on_enableRemoveBtn=Signal()
	enableRemoveBtn=Property(bool,_getEnableRemoveBtn,_setEnableRemoveBtn,notify=on_enableRemoveBtn)

	on_showRemoveBtn=Signal()
	showRemoveBtn=Property(bool,_getShowRemoveBtn,_setShowRemoveBtn,notify=on_showRemoveBtn)

	on_isProcessRunning=Signal()
	isProcessRunning=Property(bool,_getIsProcessRunning,_setIsProcessRunning,notify=on_isProcessRunning)

	on_showStatusMessage=Signal()
	showStatusMessage=Property('QVariantList',_getShowStatusMessage,_setShowStatusMessage,notify=on_showStatusMessage)
	
	on_closePopUp=Signal()
	closePopUp=Property('QVariantList',_getClosePopUp,_setClosePopUp,notify=on_closePopUp)
	
	on_endProcess=Signal()
	endProcess=Property(bool,_getEndProcess,_setEndProcess, notify=on_endProcess)

	on_endCurrentCommand=Signal()
	endCurrentCommand=Property(bool,_getEndCurrentCommand,_setEndCurrentCommand, notify=on_endCurrentCommand)

	on_currentCommand=Signal()
	currentCommand=Property('QString',_getCurrentCommand,_setCurrentCommand, notify=on_currentCommand)

	on_enableKonsole=Signal()
	enableKonsole=Property(bool,_getEnableKonsole,_setEnableKonsole,notify=on_enableKonsole)

	on_launchedProcess=Signal()
	launchedProcess=Property('QString',_getLaunchedProcess,_setLaunchedProcess,notify=on_launchedProcess)
	
	on_isProgressBarVisible=Signal()
	isProgressBarVisible=Property(bool,_getIsProgressBarVisible,_setIsProgressBarVisible,notify=on_isProgressBarVisible)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	runPkexec=Property(bool,_getRunPkexec,constant=True)

#class Bridge

from . import Core

