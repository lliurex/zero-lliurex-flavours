#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
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


	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.flavourSelectorManager=self.core.flavourSelectorManager
		self._flavoursModel=FlavoursModel.FlavoursModel()
		self._enableFlavourList=True
		self._filterStatusValue="all"
		self._totalErrorInProcess=0
		self._isAllInstalled=[False,False]
		self.flavoursEntries=[]
		self._flavoursToInstallList=""
		self._flavoursToRemoveList=""
		self._totalElements=0

	#def __init__

	def getInfo(self):

		self._updateFlavoursModel()
		self.isAllInstalled=Bridge.flavourSelectorManager.isAllInstalled()
		self.flavoursEntries=Bridge.flavourSelectorManager.flavoursData
		self.totalElements=len(self.flavoursEntries)
	
	#def getInfo

	def _getIsAllInstalled(self):

		return self._isAllInstalled

	#def _getIsAllInstalled

	def _setIsAllInstalled(self,isAllInstalled):

		if self._isAllInstalled!=isAllInstalled:
			self._isAllInstalled=isAllInstalled
			self.on_isAllInstalled.emit()

	#def _setIsAllInstalled

	def _getTotalErrorInProcess(self):

		return self._totalErrorInProcess

	#def _getTotalErrorInProcess

	def _setTotalErrorInProcess(self,totalErrorInProcess):

		if self._totalErrorInProcess!=totalErrorInProcess:
			self._totalErrorInProcess=totalErrorInProcess
			self.on_totalErrorInProcess.emit()

	#def _setTotalErrorInProcess

	def _getEnableFlavourList(self):

		return self._enableFlavourList

	#def _getEnableFlavourList

	def _setEnableFlavourList(self,enableFlavourList):

		if self._enableFlavourList!=enableFlavourList:
			self._enableFlavourList=enableFlavourList
			self.on_enableFlavourList.emit()

	#def _setEnableFlavourList

	def _getFlavoursToInstallList(self):

		return self._flavoursToInstallList

	#def _getFlavoursToInstallList

	def _setFlavoursToInstallList(self,flavoursToInstallList):

		if self._flavoursToInstallList!=flavoursToInstallList:
			self._flavoursToInstallList=flavoursToInstallList
			self.on_flavoursToInstallList.emit()

	#def _setFlavoursToInstallList

	def _getFlavoursToRemovelList(self):

		return self._flavoursToRemoveList

	#def _getFlavoursToRemoveList

	def _setFlavoursToRemoveList(self,flavoursToRemoveList):

		if self._flavoursToRemoveList!=flavoursToRemoveList:
			self._flavoursToRemoveList=flavoursToRemoveList
			self.on_flavoursToRemoveList.emit()

	#def _setFlavoursToRemoveList

	def _getTotalElements(self):

		return self._totalElements

	#def _getTotalElements

	def _setTotalElements(self,totalElements):

		if self._totalElements!=totalElements:
			self._totalElements=totalElements
			self.on_totalElements.emit()

	#def _setTotalElements

	def _getFlavoursModel(self):

		return self._flavoursModel

	#def _getFlavoursModel

	def _updateFlavoursModel(self):

		ret=self._flavoursModel.clear()
		self.flavoursEntries=Bridge.flavourSelectorManager.flavoursData
		for item in self.flavoursEntries:
			if item["pkgId"]!="":
				self._flavoursModel.appendRow(item["pkgId"],item["pkg"],item["name"],item["isChecked"],item["status"],item["banner"],item["isVisible"],item["resultProcess"],item["showSpinner"],item["isManaged"],item["isExpanded"],item["type"],item["flavourParent"],item["showAction"])

	#def _updateFlavoursModel

	def _getFilterStatusValue(self):

		return self._filterStatusValue

	#def _getFilterStatusValue

	def _setFilterStatusValue(self,filterStatusValue):

		if self._filterStatusValue!=filterStatusValue:
			self._filterStatusValue=filterStatusValue
			self.on_filterStatusValue.emit()

	#def _setFilterStatusValue

	def updateResultFlavoursModel(self,step):

		params=[]
		params.append("showSpinner")
		params.append("resultProcess")
		params.append("showAction")
		params.append("isChecked")
		if step=="end":
			params.append("banner")
			params.append("status")

		self._updateFlavoursModelInfo(params)

	#def updateResultFlavoursModel

	def _updateFlavoursModelInfo(self,params):

		updatedInfo=Bridge.flavourSelectorManager.flavoursData

		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				valuesToUpdate=[]
				index=self._flavoursModel.index(i)
				for item in params:
					tmp={}
					tmp[item]=updatedInfo[i][item]
					valuesToUpdate.append(tmp)
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

		abort=False
		if action=="expand":
			if not Bridge.flavourSelectorManager.allUnExpanded:
				if len(Bridge.flavourSelectorManager.nonExpandedParent)==0:
					abort=True
		else:
			if Bridge.flavourSelectorManager.allUnExpanded:
				abort=True

		if not abort:
			Bridge.flavourSelectorManager.manageExpansionList(action)
			params=[]
			params.append("isExpanded")
			self._updatePackagesModelInfo(params)

	#def manageExpansionList

	@Slot('QVariantList')
	def onExpandedParent(self,info):
		
		Bridge.flavourSelectorManager.onExpandedParent(info)
		params=[]
		params.append(info[1])
		
		self._updatePackagesModelInfo(params)
	
	#def updateModel

	@Slot('QVariantList')
	def onCheckedFlavour(self,info):

		Bridge.flavourSelectorManager.onCheckedPackages(info[0],info[1])
		self._refreshInfo()

	#def onCheckedFlavour

	def _refreshInfo(self):

		params=[]
		params.append("isChecked")
		params.append("showAction")
		self._updatePackagesModelInfo(params)
		enableBtn=False
		showWarning=False
		self.flavoursToInstallList=""
		self.flavoursToRemoveList=""
		self.core.mainStack.enableInstallAction=False
		self.core.mainStack.enableRemoveAction=False
		if len(Bridge.flavourSelectorManager.flavourSelectedToInstall)>0:
			for item in Bridge.flavourSelectorManager.flavourSelectedToInstall:
				self.flavoursToInstallList+="  - %s\n"%item

			enableBtn=True
			self.core.mainStack.enableInstallAction=True

		if len(Bridge.flavourSelectorManager.flavourSelectedToRemove)>0:
			for item in Bridge.flavourSelectorManager.flavourSelectedToRemove:
				self.flavoursToRemoveList+="  - %s\n"%item
				if item not in Bridge.flavourSelectorManager.wantToRemove:
					showWarning=True

			enableBtn=True
			self.core.mainStack.enableRemoveAction=True

		if enableBtn:
			self.core.mainStack.enableApplyBtn=True
		else:
			self.core.mainStack.enableApplyBtn=False

		if showWarning:
			self.core.mainStack.showStatusMessage=[True,Bridge.flavourSelectorManager.MSG_WARNING_REMOVE_META,"Warning"]
		else:
			self.core.mainStack.showStatusMessage=[False,"","Ok"]

	#def _refreshInfo

	def _updatePackagesModelInfo(self,params):

		updatedInfo=Bridge.flavourSelectorManager.flavoursData

		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				valuesToUpdate=[]
				index=self._flavoursModel.index(i)
				for item in params:
					tmp={}
					tmp[item]=updatedInfo[i][item]
					valuesToUpdate.append(tmp)
				self._flavoursModel.setData(index,valuesToUpdate)
	
	#def _updatePackagesModelInfo

	on_isAllInstalled=Signal()
	isAllInstalled=Property('QVariant',_getIsAllInstalled,_setIsAllInstalled,notify=on_isAllInstalled)

	on_totalErrorInProcess=Signal()
	totalErrorInProcess=Property(int,_getTotalErrorInProcess,_setTotalErrorInProcess,notify=on_totalErrorInProcess)

	on_enableFlavourList=Signal()
	enableFlavourList=Property(bool,_getEnableFlavourList,_setEnableFlavourList,notify=on_enableFlavourList)
	
	on_filterStatusValue=Signal()
	filterStatusValue=Property(str,_getFilterStatusValue,_setFilterStatusValue,notify=on_filterStatusValue)

	on_flavoursToInstallList=Signal()
	flavoursToInstallList=Property(str,_getFlavoursToInstallList,_setFlavoursToInstallList,notify=on_flavoursToInstallList)

	on_flavoursToRemoveList=Signal()
	flavoursToRemoveList=Property(str,_getFlavoursToRemovelList,_setFlavoursToRemoveList,notify=on_flavoursToRemoveList)	

	on_totalElements=Signal()
	totalElements=Property(int,_getTotalElements,_setTotalElements,notify=on_totalElements)

	flavoursModel=Property(QObject,_getFlavoursModel,constant=True)

#class Bridge

from . import Core

