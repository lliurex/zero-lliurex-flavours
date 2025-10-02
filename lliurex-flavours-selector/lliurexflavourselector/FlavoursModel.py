#!/usr/bin/python3
import os
import sys
from PySide6 import QtCore, QtGui, QtQml

class FlavoursModel(QtCore.QAbstractListModel):

	PkgIdRole=QtCore.Qt.UserRole+1000
	PkgRole= QtCore.Qt.UserRole + 1001
	IsCheckedRole=QtCore.Qt.UserRole+1002
	NameRole=QtCore.Qt.UserRole+1003
	BannerRole=QtCore.Qt.UserRole+1004
	StatusRole=QtCore.Qt.UserRole+1005
	IsVisibleRole=QtCore.Qt.UserRole+1006
	ResultProcessRole=QtCore.Qt.UserRole+1007
	ShowSpinnerRole = QtCore.Qt.UserRole + 1008
	IsManagedRole=QtCore.Qt.UserRole+1009
	IsExpandedRole=QtCore.Qt.UserRole+1010
	TypeRole=QtCore.Qt.UserRole+1011
	FlavourParentRole=QtCore.Qt.UserRole+1012

	def __init__(self,parent=None):
		
		super(FlavoursModel, self).__init__(parent)
		self._entries =[]
	
	#def __init__

	def rowCount(self, parent=QtCore.QModelIndex()):
		
		if parent.isValid():
			return 0
		return len(self._entries)

	#def rowCount

	def data(self, index, role=QtCore.Qt.DisplayRole):
		
		if 0 <= index.row() < self.rowCount() and index.isValid():
			item = self._entries[index.row()]
			if role == FlavoursModel.PkgIdRole:
				return item["pkgId"]
			elif role == FlavoursModel.PkgRole:
				return item["pkg"]
			elif role == FlavoursModel.IsCheckedRole:
				return item["isChecked"]
			elif role == FlavoursModel.NameRole:
				return item["name"]
			elif role == FlavoursModel.BannerRole:
				return item["banner"]
			elif role == FlavoursModel.StatusRole:
				return item["status"]
			elif role == FlavoursModel.IsVisibleRole:
				return item["isVisible"]
			elif role == FlavoursModel.ResultProcessRole:
				return item["resultProcess"]
			elif role == FlavoursModel.ShowSpinnerRole:
				return item["showSpinner"]
			elif role == FlavoursModel.IsManagedRole:
				return item["isManaged"]
			elif role == FlavoursModel.IsExpandedRole:
				return item["isExpanded"]
			elif role == FlavoursModel.TypeRole:
				return item["type"]
			elif role == FlavoursModel.FlavourParentRole:
				return item["flavourParent"]	
	#def data

	def roleNames(self):
		
		roles = dict()
		roles[FlavoursModel.PkgIdRole]=b"pkgId"
		roles[FlavoursModel.PkgRole] = b"pkg"
		roles[FlavoursModel.IsCheckedRole] = b"isChecked"
		roles[FlavoursModel.NameRole] = b"name"
		roles[FlavoursModel.BannerRole] = b"banner"
		roles[FlavoursModel.StatusRole] = b"status"
		roles[FlavoursModel.IsVisibleRole] = b"isVisible"
		roles[FlavoursModel.ResultProcessRole] = b"resultProcess"
		roles[FlavoursModel.ShowSpinnerRole] = b"showSpinner"
		roles[FlavoursModel.IsManagedRole]=b"isManaged"
		roles[FlavoursModel.IsExpandedRole]=b"isExpanded"
		roles[FlavoursModel.TypeRole]=b"type"
		roles[FlavoursModel.FlavourParentRole]=b"flavourParent"



		return roles

	#def roleName

	def appendRow(self,ide,pkg,na,isc,st,ba,isv,rpr,ss,im,ie,ty,pr):
		
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
		self._entries.append(dict(pkgId=ide,pkg=pkg, name=na,isChecked=isc,status=st,banner=ba,isVisible=isv,resultProcess=rpr,showSpinner=ss,isManaged=im,isExpanded=ie,type=ty,flavourParent=pr))
		self.endInsertRows()

	#def appendRow

	def setData(self, index, valuesToUpdate, role=QtCore.Qt.EditRole):
		
		if role == QtCore.Qt.EditRole:
			row = index.row()
			for item in valuesToUpdate:
				for param in item:
					if param in ["status","banner","showSpinner","isVisible","isChecked","resultProcess","isExpanded"]:
						self._entries[row][param]=item[param]
						self.dataChanged.emit(index,index)

	#def setData

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class FlavoursModel
