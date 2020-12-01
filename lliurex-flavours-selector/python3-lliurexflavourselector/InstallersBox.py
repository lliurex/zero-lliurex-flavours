#!/usr/bin/env python3
import sys
import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon,QPixmap,QCursor
from PyQt5.QtCore import Qt,QEvent,QPoint,QSize
from PyQt5.QtWidgets import QLabel, QWidget,QVBoxLayout,QHBoxLayout,QCheckBox,QSizePolicy,QToolButton,QMenu,QToolTip


from . import waitingSpinner

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class InstallersBox(QWidget):
	def __init__(self):
		super(InstallersBox, self).__init__() # Call the inherited classes __init__ method
		
		self.core=Core.Core.get_core()
		ui_file=self.core.rsrc_dir+"installersBox.ui"
		uic.loadUi(ui_file, self) # Load the .ui fil
		self.boxInstallers=self.findChild(QVBoxLayout,'installersBox')
		self.boxInstallers.setAlignment(Qt.AlignTop)
		self.scrollArea=self.findChild(QWidget,'scrollAreaWidgetContents')
		self.scrollArea.setStyleSheet("background-color:white")
		self.box_selected=[]
		self.flavours_selected=[]
	
	#def __init__

	def drawInstallerList(self):
		
		self.total_flavours=0
		for item in self.core.flavourSelectorManager.flavour_list:
			if self.core.flavourSelectorManager.flavour_list[item]["show"]:
				self.total_flavours+=1

		self.count=0
		for item in self.core.flavourSelectorManager.flavour_list:
			alternative_type=""
			alternative_list=""
			if self.core.flavourSelectorManager.flavour_list[item]["show"]:
				self.count+=1
				if "client" in self.core.flavourSelectorManager.flavour_list[item]["pkg"]:
					if len(self.core.flavourSelectorManager.client_desktop_alternatives)>0:
						alternative_type="client-desktop"
						alternative_list=self.core.flavourSelectorManager.client_desktop_alternatives
					elif len(self.core.flavourSelectorManager.client_lite_alternatives)>0:
						alternative_type="client-lite"
						alternative_list=self.core.flavourSelectorManager.client_lite_alternatives
				if "server" in self.core.flavourSelectorManager.flavour_list[item]["pkg"]:
					if len(self.core.flavourSelectorManager.server_alternatives)>0:
						alternative_type="server"
						alternative_list=self.core.flavourSelectorManager.server_alternatives

				self.newInstallerBox(self.core.flavourSelectorManager.flavour_list[item],item,alternative_type,alternative_list)
			
	#def drawInstallerList

	def newInstallerBox(self,item,order,alternative_type,alternative_list):

		hbox=QHBoxLayout()
		hbox.setContentsMargins(0,0,0,0)
		hbox.setSpacing(0)
		
		checkbox=QCheckBox()
		checkbox.setTristate(False)
		checkbox.stateChanged.connect(self.changeState)
		
		title=self.getTitle(item["pkg"])
		checkbox.setStyleSheet("padding:10px;height:80px")
		checkbox.item=item
		checkbox.pkg=item["pkg"]
		checkbox.alternative_type=alternative_type
		checkbox.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed));
		hbox.addWidget(checkbox)
		
		icon=QLabel()
		pixmap=QPixmap(item["banner"])
		icon.setPixmap(pixmap)
		icon.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)
		icon.setMinimumSize(75,75)
		icon.setMaximumSize(75,75)
		icon.item=item
		hbox.addWidget(icon)
		
		name=QLabel()
		name.setText(item["name"]+": "+title)
		name.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
		if self.count<self.total_flavours:
			name.setStyleSheet("font:10pt;padding:15px;border:3px solid silver;border-top:0px;border-right:0px;border-left:0px;margin-top:0px;")
		else:
			name.setStyleSheet("font:10pt;padding:15px")

		name.item=item
		name.alternative_type=alternative_type
		hbox.addWidget(name,-1)
		
		status=QLabel()
		pixmap=QPixmap(self.core.rsrc_dir+"initial.png")
		status.setPixmap(pixmap)
		status.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
		status.setMinimumSize(35,100)
		status.setMaximumSize(35,100)
		status.item=item
		hbox.addWidget(status)

		waiting=waitingSpinner.waitingSpinner()
		spinner_gif=self.core.rsrc_dir+"loading.gif"
		waiting.setGif(spinner_gif,"flavour")
		waiting.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
		waiting.setMinimumSize(35,100)
		waiting.setMaximumSize(35,100)
		waiting.item=item
		waiting.hide()
		hbox.addWidget(waiting)
		
		if alternative_type!="":
			status.hide()
			menu=QMenu()
			for item in alternative_list:
				action=menu.addAction(item[0])
				action.triggered.connect(lambda chk, item=item: self.itemClicked(item[0],item[1],alternative_type))

			pushbutton =QToolButton()
			icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"editor.svg"))
			pushbutton.setIcon(icn)
			pushbutton.setIconSize(QSize(16,16))
			pushbutton.setToolTip(_("Click to select an option"))
			pushbutton.clicked.connect(lambda:self.buttonPress(alternative_type))

			pushbutton.current=False
			pushbutton.alternative_type=alternative_type
			pushbutton.item=item
			pushbutton.setPopupMode(QToolButton.InstantPopup)
			pushbutton.setStyleSheet("margin-right:12px;background-color:#efefef") 
			pushbutton.setMaximumSize(40,30)
			self.setStyleSheet("""QToolTip { 
	                          background-color:#efefef; 
	                          color: black; 
	                          border: #efefef solid 1px;
	                          }""")
			self.setMenu(menu,alternative_type)
			hbox.addWidget(pushbutton)

		self.boxInstallers.addLayout(hbox)
	
	#def newInstallerBox	

	def setMenu(self,menu,alternative_type):

		if alternative_type=="client-desktop":
			self.menuClientDesktop=menu
			self.setContextMenuPolicy(Qt.CustomContextMenu)
		elif alternative_type=="client-lite":
			self.menuClientLite=menu
			self.setContextMenuPolicy(Qt.CustomContextMenu)
		elif alternative_type=="server":
			self.menuServer=menu
			self.setContextMenuPolicy(Qt.CustomContextMenu)
			
	#def setMenu

	def openContextMenu(self,alternative_type):
		
		if alternative_type=='client-desktop':
			self.menuClientDesktop.exec_(self.sender().mapToGlobal(QPoint(10,23)))
		elif alternative_type=="client-lite":
			self.menuClientLite.exec_(self.sender().mapToGlobal(QPoint(10,23)))
		elif alternative_type=="server":
			self.menuServer.exec_(self.sender().mapToGlobal(QPoint(10,23)))
	
	#def openContextMenu

	def buttonPress(self,alternative_type):
		
		self.openContextMenu(alternative_type)

	#def buttonPress	

	def itemClicked(self,name,pkg,alternative_type):
		
	
		for item in self.boxInstallers.children():
			if item.itemAt(2).widget().alternative_type==alternative_type:
				title=self.getTitle(pkg)
				item.itemAt(2).widget().setText(name+": "+title)
			if item.itemAt(0).widget().alternative_type==alternative_type:
				old_pkg=item.itemAt(0).widget().pkg
				item.itemAt(0).widget().pkg=pkg	
				if old_pkg in self.flavours_selected:
					self.flavours_selected.remove(old_pkg)
					self.flavours_selected.append(pkg)

	#def itemClicked		
	
	def changeState(self,state):

		if self.sender().isChecked():
			for item in self.boxInstallers.children():
				if item.itemAt(0).widget().item==self.sender().item:	
					self.box_selected.append(item)
					self.flavours_selected.append(self.sender().pkg)
				
				else:
					item.itemAt(0).widget().setEnabled(False)	
					
		else:
			for item in self.boxInstallers.children():
				if item.itemAt(0).widget().item==self.sender().item:
					self.box_selected.remove(item)
					self.flavours_selected.remove(self.sender().pkg)	
				else:
					item.itemAt(0).widget().setEnabled(True)	
		
	#def changeState

	def getTitle(self,pkg):

		if 'server-lite' in pkg:
			title=_("similar to install a LliureX Server Lite ISO")
		elif 'server' in pkg:
			title=_("similar to install a LliureX Server ISO")
		elif 'client-lite' in pkg:
			title=_("similar to install  a LliureX Client Lite ISO")
		elif 'minimal-client' in pkg:
			title=_("install only the basic functionalities of a LliureX Client")
		elif 'client' in pkg:
			title=_("similar to install  a LliureX Client ISO")
		elif 'desktop-lite' in pkg:
			title=_("similar to install  a LliureX Desktop Lite ISO")
		elif 'desktop' in pkg:
			title=_("similar to install  a LliureX Desktop ISO")	
		elif 'infantil' in pkg:
			title=_("similar to install a LliureX Infantil ISO")
		elif 'music' in pkg:
			title=_("similar to install LliureX Music ISO")	
		
		return title
	
	#def getTitle				
#class InstallersBox

from . import Core