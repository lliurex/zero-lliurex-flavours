#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

from . import FlavoursModel

signal.signal(signal.SIGINT, signal.SIG_DFL)

class Bridge(QObject):

	isAllInstalledChanged=Signal()
	totalErrorInProcessChanged=Signal()
	enableFlavourListChanged=Signal()
	filterStatusValueChanged=Signal()
	flavoursToInstallListChanged=Signal()
	flavoursToRemoveListChanged=Signal()
	totalElementsChanged=Signal()

	def __init__(self):

		super().__init__()
		self.core=Core.Core.get_core()
		self.flavourManager=self.core.flavourSelectorManager
		self._flavoursModel=FlavoursModel.FlavoursModel()
		self._enableFlavourList=True
		self._filterStatusValue="all"
		self._totalErrorInProcess=0
		self._isAllInstalled={"allInstalled":False,"allAvailable":False}
		self._flavoursToInstallList=""
		self._flavoursToRemoveList=""
		self._totalElements=0
		self.flavoursEntries=[]

	#def __init__

	@Property(dict, notify=isAllInstalledChanged)
	def isAllInstalled(self):

		return self._isAllInstalled

	#def isAllInstalled

	@isAllInstalled.setter
	def isAllInstalled(self,isAllInstalled):

		if self._isAllInstalled!=isAllInstalled:
			self._isAllInstalled=isAllInstalled
			self.isAllInstalledChanged.emit()

	#def isAllInstalled

	@Property(int,notify=totalErrorInProcessChanged)
	def totalErrorInProcess(self):

		return self._totalErrorInProcess

	#def totalErrorInProcess

	@totalErrorInProcess.setter
	def totalErrorInProcess(self,totalErrorInProcess):

		if self._totalErrorInProcess!=totalErrorInProcess:
			self._totalErrorInProcess=totalErrorInProcess
			self.totalErrorInProcessChanged.emit()

	#def totalErrorInProcess

	@Property(bool, notify=enableFlavourListChanged)
	def enableFlavourList(self):

		return self._enableFlavourList

	#def enableFlavourList

	@enableFlavourList.setter
	def enableFlavourList(self,enableFlavourList):

		if self._enableFlavourList!=enableFlavourList:
			self._enableFlavourList=enableFlavourList
			self.enableFlavourListChanged.emit()

	#def enableFlavourList
	
	@Property(str, notify=filterStatusValueChanged)
	def filterStatusValue(self):

		return self._filterStatusValue

	#def filterStatusValue

	@filterStatusValue.setter
	def filterStatusValue(self,filterStatusValue):

		if self._filterStatusValue!=filterStatusValue:
			self._filterStatusValue=filterStatusValue
			self.filterStatusValueChanged.emit()

	#def filterStatusValue

	@Property(str, notify=flavoursToInstallListChanged)
	def flavoursToInstallList(self):

		return self._flavoursToInstallList

	#def flavoursToInstallList

	@flavoursToInstallList.setter
	def flavoursToInstallList(self,flavoursToInstallList):

		if self._flavoursToInstallList!=flavoursToInstallList:
			self._flavoursToInstallList=flavoursToInstallList
			self.flavoursToInstallListChanged.emit()

	#def flavoursToInstallList	

	@Property(str, notify=flavoursToRemoveListChanged)	
	def flavoursToRemoveList(self):

		return self._flavoursToRemoveList

	#def flavoursToRemoveList

	@flavoursToRemoveList.setter
	def flavoursToRemoveList(self,flavoursToRemoveList):

		if self._flavoursToRemoveList!=flavoursToRemoveList:
			self._flavoursToRemoveList=flavoursToRemoveList
			self.flavoursToRemoveListChanged.emit()

	#def flavoursToRemoveList

	@Property(int, notify=totalElementsChanged)
	def totalElements(self):

		return self._totalElements

	#def totalElements

	@totalElements.setter
	def totalElements(self,totalElements):

		if self._totalElements!=totalElements:
			self._totalElements=totalElements
			self.totalElementsChanged.emit()

	#def totalElements

	@Property(QObject,constant=True)
	def flavoursModel(self):

		return self._flavoursModel

	#def packagesModel

	def getInfo(self):

		self._updateFlavoursModel()
		self.isAllInstalled=self.flavourManager.isAllInstalled()
		self.flavoursEntries=self.flavourManager.flavoursData
		self.totalElements=len(self.flavoursEntries)
	
	#def getInfo

	def _getFlavoursModel(self):

		return self._flavoursModel

	#def _getFlavoursModel

	def _updateFlavoursModel(self):

		ret=self._flavoursModel.clear()
		self.flavoursEntries=self.flavourManager.flavoursData
		for item in self.flavoursEntries:
			if item["pkgId"]!="":
				self._flavoursModel.appendRow(item["pkgId"],item["pkg"],item["name"],item["isChecked"],item["status"],item["banner"],item["isVisible"],item["resultProcess"],item["showSpinner"],item["isManaged"],item["isExpanded"],item["type"],item["flavourParent"],item["showAction"])

	#def _updateFlavoursModel

	def updateResultFlavoursModel(self,step):

		params=[]
		params.append("showSpinner")
		params.append("resultProcess")
		params.append("showAction")
		params.append("isChecked")
		params.append("isManaged")
		if step=="end":
			params.append("banner")
			params.append("status")

		self._updateFlavoursModelInfo(params)

	#def updateResultFlavoursModel

	def _updateFlavoursModelInfo(self,params):

		updatedInfo=self.flavourManager.flavoursData

		if not updatedInfo:
			return

		for i,infoItem in enumerate(updatedInfo):
			index=self._flavoursModel.index(i)
			valuesToUpdate=[{param:infoItem[param]} for param in params if param in infoItem]
			if valuesToUpdate:
				self._flavoursModel.setData(index,valuesToUpdate)
	
	#def _updateFlavoursModelInfo

	@Slot(str)
	def manageStatusFilter(self,value):

		self.filterStatusValue=value

	#def manageStatusFilter

	@Slot(int,result='QVariant')
	def getModelData(self,index):
		
		return self.flavoursEntries[index]

	#def getModelData

	@Slot(str)
	def manageExpansionList(self,action):

		if action=="expand":
			if not self.flavourManager.allUnExpanded and len(self.flavourManager.nonExpandedParent)==0:
				return
		else:
			if self.flavourManager.allUnExpanded:
				return

		self.flavourManager.manageExpansionList(action)
		self._updateFlavoursModelInfo(["isExpanded"])

	#def manageExpansionList

	@Slot(dict)
	def onExpandedParent(self,info):
		
		self.flavourManager.onExpandedParent(info)
		self._updateFlavoursModelInfo(["isExpanded"])
	
	#def onExpandedParent

	@Slot(dict)
	def onCheckedFlavour(self,info):

		self.flavourManager.onCheckedPackages(info)
		self._refreshInfo()

	#def onCheckedFlavour

	def _refreshInfo(self):

		self._updateFlavoursModelInfo(["isChecked","showAction"])

		toInstall=self.flavourManager.flavourSelectedToInstall
		toRemove=self.flavourManager.flavourSelectedToRemove

		self.flavoursToInstallList="".join(f"  - {item}\n" for item in toInstall) if toInstall else ""
		self.flavoursToRemoveList="".join(f"  - {item}\n" for item in toRemove) if toRemove else ""
		self.core.mainStack.enableInstallAction=bool(toInstall)
		self.core.mainStack.enableCartAction="lliurex-meta-wifi-alu" in toInstall if toInstall else False
		
		self.core.mainStack.enableRemoveAction=bool(toRemove)

		showWarning=any(item not in self.flavourManager.wantToRemove for item in toRemove) if toRemove else False
		
		self.core.mainStack.enableApplyBtn=bool(toInstall or toRemove)

		if showWarning:
			self.core.mainStack.showStatusMessage={"show":True,"msgCode":self.flavourManager.MSG_WARNING_REMOVE_META,"type":"Warning"}
		else:
			self.core.mainStack.showStatusMessage={"show":False,"msgCode":"","type":""}

	#def _refreshInfo

#class Bridge

from . import Core

