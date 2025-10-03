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


	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.flavourSelectorManager=self.core.flavourSelectorManager
		self._flavoursModel=FlavoursModel.FlavoursModel()
		self._enableFlavourList=True
		self._uncheckAll=False
		self._filterStatusValue="all"
		self._totalErrorInProcess=0
		self._isAllInstalled=[False,False]
		self.flavoursEntries=[]

	#def __init__

	def getInfo(self):

		self._updateFlavoursModel()
		self.uncheckAll=Bridge.flavourSelectorManager.uncheckAll
		self.isAllInstalled=Bridge.flavourSelectorManager.isAllInstalled()
		self.flavoursEntries=Bridge.flavourSelectorManager.flavoursData

	#def showInfo

	def _getUncheckAll(self):

		return self._uncheckAll

	#def _getUncheckAll

	def _setUncheckAll(self,uncheckAll):

		if self._uncheckAll!=uncheckAll:
			self._uncheckAll=uncheckAll
			self.on_uncheckAll.emit()

	#def _setUncheckAll

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

	@Slot('QVariantList')
	def onExpandedParent(self,info):
		
		Bridge.flavourSelectorManager.onExpandedParent(info)
		params=[]
		params.append(info[1])
		self._updatePackagesModelInfo(params)
	
	#def updateModel

	@Slot('QVariantList')
	def onCheckedFlavour(self,info):

		self.filterStatusValue="all"
		Bridge.flavourSelectorManager.onCheckedPackages(info[0],info[1])
		self._refreshInfo()

	#def onCheckedFlavour

	@Slot()
	def selectAll(self):

		Bridge.flavourSelectorManager.selectAll()
		self.filterStatusValue="all"
		self._refreshInfo()
		
	#def selectAll

	def _refreshInfo(self):

		params=[]
		params.append("isChecked")
		params.append("showAction")
		self._updatePackagesModelInfo(params)
		#self.uncheckAll=Bridge.flavourSelectorManager.uncheckAll
		if len(Bridge.flavourSelectorManager.flavourSelectedToInstall) or len(Bridge.flavourSelectorManager.flavourSelectedToRemove)>0:
			self.core.mainStack.enableApplyBtn=True
		else:
			self.core.mainStack.enableApplyBtn=False


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

	on_uncheckAll=Signal()
	uncheckAll=Property(bool,_getUncheckAll,_setUncheckAll,notify=on_uncheckAll)

	on_isAllInstalled=Signal()
	isAllInstalled=Property('QVariant',_getIsAllInstalled,_setIsAllInstalled,notify=on_isAllInstalled)

	on_totalErrorInProcess=Signal()
	totalErrorInProcess=Property(int,_getTotalErrorInProcess,_setTotalErrorInProcess,notify=on_totalErrorInProcess)

	on_enableFlavourList=Signal()
	enableFlavourList=Property(bool,_getEnableFlavourList,_setEnableFlavourList,notify=on_enableFlavourList)
	
	on_filterStatusValue=Signal()
	filterStatusValue=Property(str,_getFilterStatusValue,_setFilterStatusValue,notify=on_filterStatusValue)

	flavoursModel=Property(QObject,_getFlavoursModel,constant=True)

#class Bridge

from . import Core

