#!/usr/bin/env python3
import sys
import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon,QPixmap,QPainter
from PyQt5.QtCore import Qt,QEvent,QTimeLine,QThread,pyqtSignal,QSize
from PyQt5.QtWidgets import QLabel, QWidget,QVBoxLayout,QHBoxLayout,QSizePolicy,QMainWindow,QPushButton,QStackedLayout,QDesktopWidget,QMessageBox

import time
import subprocess
import pwd

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class gatherInfo(QThread):
	def __init__(self,*args):
		QThread.__init__(self)

		self.errMsg=""
		self.err=0
		self.core=Core.Core.get_core()
	#def __init__
		
	def run(self,*args):

		try:
			self.core.flavourSelectorManager.getSupportedFlavour()
		except Exception as e:
			self.errMsg=("Failed when updating config: %s")%e
			self.err=1
	#def run	

#clas gatherInfo

class installProcess(QThread):

	def __init__(self,*args):
		
		QThread.__init__(self)
		self.errMsg=""
		self.err=0
		self.core=Core.Core.get_core()
		self.meta_list=args[0]
		self.mirrorRepository=args[1]
	#def __init__

	def run(self,*args):

		try:
			self.core.flavourSelectorManager.installMeta(self.meta_list,self.mirrorRepository)
		except Exception as e:
			self.errMsg=("Failed when updating config: %s")%e
			self.err=1
	#def run
# class installProcess
class FaderWidget(QWidget):
	
	def __init__(self, old_widget, new_widget):

		QWidget.__init__(self, new_widget)
		self.old_pixmap = QPixmap(new_widget.size())
		old_widget.render(self.old_pixmap)
		self.pixmap_opacity = 1.0
		self.timeline = QTimeLine()
		self.timeline.valueChanged.connect(self.animate)
		self.timeline.finished.connect(self.close)
		self.timeline.setDuration(222)
		self.timeline.start()
		self.resize(new_widget.size())
		self.show()
	#def __init__

	def paintEvent(self, event):

		painter = QPainter()
		painter.begin(self)
		painter.setOpacity(self.pixmap_opacity)
		painter.drawPixmap(0, 0, self.old_pixmap)
		painter.end()
	
	#def paint
	def animate(self, value):

		self.pixmap_opacity = 1.0 - value
		self.repaint()

	#def animante
#class FaderWidget	

class MainWindow(QMainWindow):
	
	def __init__(self):

		super(MainWindow, self).__init__() # Call the inherited classes __init__ method
		self.core=Core.Core.get_core()
		
	def loadGui(self):

		ui_file=self.core.rsrc_dir+"mainWindow.ui"
		uic.loadUi(ui_file, self) # Load the .ui file
		
		self.optionsBox=self.findChild(QHBoxLayout,'optionsBox')
		self.flavourTitle=self.findChild(QLabel,'flavourTitle')

		self.mainBox=self.findChild(QVBoxLayout,'mainBox')
		self.bannerBox=self.findChild(QLabel,'bannerLabel')
		self.bannerBox.setStyleSheet("background-color: #07237f") 
		self.messageBox=self.findChild(QVBoxLayout,'messageBox')
		self.messageLabel=self.findChild(QLabel,'messageLabel')
		self.controlsBox=self.findChild(QVBoxLayout,'controlsBox')
		self.applyButton=self.findChild(QPushButton,'applyButton')
		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"gtk-ok.svg"))
		self.applyButton.setIcon(icn)
		self.applyButton.setText(_("Install"))
		self.applyButton.clicked.connect(self.applyButtonClicked)
		self.helpButton=self.findChild(QPushButton,'helpButton')
		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"help-whatsthis.svg"))
		self.helpButton.setIcon(icn)
		self.helpButton.setText(_("Help"))
		self.helpButton.clicked.connect(self.helpButtonClicked)
		
		self.loadingBox=self.core.loadingBox
		self.installersBox=self.core.installersBox

		self.QtStack=QStackedLayout()
		self.QtStack.addWidget(self.loadingBox)
		self.QtStack.addWidget(self.installersBox)
		
		self.mainBox.addLayout(self.QtStack)
		self.gatherInfo=gatherInfo()
		
		self.flavourTitle.hide()
		
		self.mirrorRepository=False
		self.messageLabel.hide()
		self.applyButton.hide()
		self.helpButton.hide()

		qtRectangle = self.frameGeometry()
		centerPoint = QDesktopWidget().availableGeometry().center()
		qtRectangle.moveCenter(centerPoint)
		self.move(qtRectangle.topLeft())
		centerPoint = QDesktopWidget().availableGeometry().center()
		qtRectangle.moveCenter(centerPoint)
		self.move(qtRectangle.topLeft())
		self.gatherInfo.start()
		self.gatherInfo.finished.connect(self._finishProcess)
		
	#def loadGui

	def _finishProcess(self):

		self.loadingBox.spinner.stop()
		tmp=""
		flavours_installed=len(self.core.flavourSelectorManager.flavours_installed)
		count=1
		if flavours_installed>0:
			for item in self.core.flavourSelectorManager.flavours_installed:
				tmp=tmp+item.split("lliurex-meta-")[1]
				if count<flavours_installed:
					tmp=tmp+", "
				count+=1	
		else:
			tmp=_("None")

		title=(_("Current flavours installed: ")+tmp)

		self.flavourTitle.setText(title)		
		self.flavourTitle.show()
		
		if len(self.core.flavourSelectorManager.flavour_list)>0:
			self.installersBox.drawInstallerList()
			self.fader_widget = FaderWidget(self.QtStack.currentWidget(), self.QtStack.widget(1))
			self.QtStack.setCurrentIndex(1)
			self.messageLabel.show()
			self.applyButton.show()
			self.helpButton.show()
			
		else:
			self.messageLabel.show()
			self.loadingBox.spinner.hide()
			self.messageLabel.setText(_("No Flavours version availables detected"))	
		
	#def _finishProcess

	def applyButtonClicked(self):

		self.othersBox=[]
		self.flavoursToInstall=self.installersBox.flavours_selected
		self.boxSelected=self.installersBox.box_selected
		
		self.messageLabel.setText("")
		if len(self.flavoursToInstall)>0:
			if not self.core.flavourSelectorManager.isIncompatibleMeta(self.flavoursToInstall[0]):
				if 'client' in self.flavoursToInstall[0]:
					ret=self.core.flavourSelectorManager.isMirrorInSourceslist()
					if not ret:
						self.showMirrorDialog()
				
				self.showConfirmDialog()
			else:
				self.messageLabel.setText(_("The selected flavor is not compatible with those already installed"))
	
		else:		
			self.messageLabel.setText(_("You must select a Flavour to install"))

	#def applyButtonClicked 
	
	def launchInstall(self):				

		self.applyButton.setEnabled(False)
		self.messageLabel.setText(_("Installing selected Flavour. Wait a moment..."))

		for item in self.boxSelected:
			item.itemAt(0).widget().setEnabled(False)
			item.itemAt(3).widget().hide()
			item.itemAt(4).widget().show()
			item.itemAt(4).widget().start()
			try:
				item.itemAt(5).widget().hide()
			except:
				pass	

		for item in self.installersBox.boxInstallers.children():
				item.itemAt(0).widget().setEnabled(False)	
				try:
					item.itemAt(5).widget().setEnabled(False)
				except:
					pass	
				self.othersBox.append(item)	

		self.install=installProcess(self.flavoursToInstall[0],self.mirrorRepository)
		self.install.start()
		self.install.finished.connect(self._finishInstall)

	#def launchInstall
			
	def _finishInstall(self):

		result=self.core.flavourSelectorManager.thread_ret
		error=False
		if result==0:
			for element in self.boxSelected:
				element.itemAt(4).widget().stop()
				element.itemAt(4).widget().hide()
				pixmap=QPixmap(self.core.rsrc_dir+"check.png")
				element.itemAt(3).widget().setPixmap(pixmap)
				element.itemAt(0).widget().setChecked(False)
				element.itemAt(3).widget().show()
		else:
			for element in self.boxSelected:
				element.itemAt(4).widget().stop()
				element.itemAt(4).widget().hide()
				pixmap=QPixmap(self.core.rsrc_dir+"error.png")
				element.itemAt(3).widget().setPixmap(pixmap)
				element.itemAt(0).widget().setChecked(False)
				element.itemAt(0).widget().setEnabled(True)
				element.itemAt(3).widget().show()
			error=True		
		
		if error:
			self.messageLabel.setText(_("An error ocurred. See log in /var/log/lliurex-flavours-selector"))					     
		else:
			self.messageLabel.setText(_("Installation succesful. A reboot is required"))					     

	#def _finishInstall
			
	
	def showMirrorDialog(self):

		mirrorDialog=QMessageBox()
		mirrorDialog.setIcon(QMessageBox.Information)
		mirrorDialog.setText(_("Do you want to add the classroom server \nmirror repository to the sources list?"))
		mirrorDialog.setStyleSheet("font:11pt")
		mirrorDialog.setWindowTitle("Lliurex Flavour Selector")
		mirrorDialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		
		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"dialog-ok.svg"))
		mirrorDialog.children()[2].children()[1].setIcon(icn)
		mirrorDialog.children()[2].children()[1].setText(_("Yes"))
		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"dialog-cancel.svg"))
		mirrorDialog.children()[2].children()[2].setIcon(icn)
		mirrorDialog.children()[2].children()[2].setText(_("No"))
		
		mirrorDialog.buttonClicked.connect(self.mirrorDialogClicked)

		try:
			mirrorDialog.exec_()
		except:
			pass	
	
	#showMirrorDialog

	def mirrorDialogClicked(self,i):

		if str(i.text()) in ["Yes","Si"]:
			self.mirrorRepository=True
		else:
			self.mirrorRepository=False
		
	#def mirrorDialogClicked

	def showConfirmDialog(self):

		confirmDialog=QMessageBox()
		confirmDialog.setIcon(QMessageBox.Warning)
		confirmDialog.setText(_("The selected flavours will be installed. Do you wish to continue?"))
		confirmDialog.setStyleSheet("font:11pt")
		confirmDialog.setWindowTitle("Lliurex Flavour Selector")
		confirmDialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"dialog-ok.svg"))
		confirmDialog.children()[2].children()[1].setIcon(icn)
		confirmDialog.children()[2].children()[1].setText(_("Ok"))
		icn=QIcon.fromTheme(os.path.join(settings.ICONS_THEME,"dialog-cancel.svg"))
		confirmDialog.children()[2].children()[2].setIcon(icn)
		confirmDialog.children()[2].children()[2].setText(_("Cancel"))
		
		confirmDialog.buttonClicked.connect(self.confirmDialogClicked)

		try:
			confirmDialog.exec_()
		except:
			pass	
	
	#def showConfirmDialog

	def confirmDialogClicked(self,i):

		if str(i.text()) in ["Ok","Aceptar","Accepta"]:
			self.launchInstall()
		
	#def confirmDialogClicked

	def helpButtonClicked(self):

		lang=os.environ["LANG"]
		run_pkexec=False
		
		if "PKEXEC_UID" in os.environ:
			run_pkexec=True
		
		if 'ca_ES' in lang:
			cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Canviar-sabor-en-LliureX-19'
		else:
			cmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Cambiar++sabor+en+LliureX+19'

		if not run_pkexec:
			self.fcmd="su -c '%s' $USER" %cmd
		else:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.fcmd="su -c '" +cmd+ "' "+ user
			
		os.system(self.fcmd)

	#def helpButtonClicked		

from . import Core