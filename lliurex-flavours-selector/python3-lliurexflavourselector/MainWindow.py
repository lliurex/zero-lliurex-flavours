#!/usr/bin/env python3
import sys
import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon,QPixmap,QPainter
from PyQt5.QtCore import Qt,QEvent,QTimeLine,QThread,pyqtSignal,QSize,QTimer,QEventLoop,QObject
#from PyQt5.QtWidgets import QLabel, QWidget,QVBoxLayout,QHBoxLayout,QSizePolicy,QMainWindow,QPushButton,QStackedLayout,QDesktopWidget,QMessageBox
from PyQt5.QtWidgets import *

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

class getPackages(QThread):

	def __init__(self,*args):
		
		QThread.__init__(self)
		self.meta_list=args[0]
		self.core=Core.Core.get_core()

	
	#def __init__

	def run(self,*args):

		self.core.flavourSelectorManager.getNumberPackages(self.meta_list)
	#def run

#class getPackages

class Worker(QObject):

	_finished=pyqtSignal()
	_progress=pyqtSignal(str)

	def __init__(self,*args):
		
		QObject.__init__(self)
		self.core=Core.Core.get_core()
		self.maxRetry=3
		self.timeToCheck=10
		self.isWorked=False
		self.aptStop=False
		self.aptRun=True
		self.unpackedRun=False
		self.count=0
		self.running=False
		self.countDown=self.maxRetry
	
	#def __init__

	def run(self):

		while self.running:
			self._updateProgress()
			time.sleep(self.timeToCheck)
	
	#def run

	def _updateProgress(self):

		if not self.isWorked:
			self.isWorked=True
			if not self.aptStop:
				isAptRunning=self.core.flavourSelectorManager.isAptRunning()
				if self.count==2:
					self.aptRun=isAptRunning
				else:
					self.count+=1

			if not self.aptRun:
				if not self.aptStop:	
					self._progress.emit("unpack")
					self.aptStop=True
					self.unpackedRun=True

				if self.countDown==self.maxRetry:
					self.countDown=0
					if self.unpackedRun:
						self.core.flavourSelectorManager.checkProgressUnpacked()
						if self.core.flavourSelectorManager.progressUnpacked!=len(self.core.flavourSelectorManager.initialNumberPackages):
							self._progress.emit("unpack")
						else:
							self._progress.emit("install")
							self.unpackedRun=False
					else:
						self.core.flavourSelectorManager.checkProgressInstallation()
						if self.core.flavourSelectorManager.progressInstallation!=len(self.core.flavourSelectorManager.initialNumberPackages):
							self._progress.emit("install")
						else:
							self.running=False
							self._progress.emit("end")
							self._finished.emit()
				else:
					self.countDown+=1

			self.isWorked=False

	#def _updateProgress

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
		self.messageImg=self.findChild(QLabel,'messageImg')
		self.messageLabel=self.findChild(QLabel,'messageLabel')
		self.progressBar=self.findChild(QProgressBar,'progressBar')

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
		#self.messageLabel.hide()
		self.manage_msg_box(True,False)	
		self.applyButton.hide()
		self.helpButton.hide()

		qtRectangle = self.frameGeometry()
		centerPoint = QDesktopWidget().availableGeometry().center()
		qtRectangle.moveCenter(centerPoint)
		self.move(qtRectangle.topLeft())
		centerPoint = QDesktopWidget().availableGeometry().center()
		qtRectangle.moveCenter(centerPoint)
		self.move(qtRectangle.topLeft())
		
		self.exitLocked=True
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
				flavour=item.split("lliurex-meta-")[1]
				if flavour=="music":
					flavour="multimedia"
				flavour=flavour.title()	
				tmp=tmp+flavour

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
			self.manage_msg_box(True,False)	
			self.applyButton.show()
			self.helpButton.show()
			
		else:
			self.manage_msg_box(False,True)	
			self.loadingBox.spinner.hide()
			self.messageLabel.setText(_("No Flavours version availables detected"))	
		
		self.exitLocked=False
	#def _finishProcess

	def applyButtonClicked(self):

		self.othersBox=[]
		self.flavoursToInstall=self.installersBox.flavours_selected
		self.boxSelected=self.installersBox.box_selected

		self.manage_msg_box(True,False)	
		self.messageLabel.setText("")
		if len(self.flavoursToInstall)>0:
			if not self.core.flavourSelectorManager.isIncompatibleMeta(self.flavoursToInstall[0]):
				if 'client' in self.flavoursToInstall[0]:
					ret=self.core.flavourSelectorManager.isMirrorInSourceslist()
					if not ret:
						self.showMirrorDialog()
				
				self.showConfirmDialog()
			else:
				self.manage_msg_box(False,True)	
				self.messageLabel.setText(_("The selected flavor is not compatible with those already installed"))
	
		else:
			self.manage_msg_box(False,True)	
			self.messageLabel.setText(_("You must select a Flavour to install"))

	#def applyButtonClicked 
	
	def launchInstall(self):				

		self.applyButton.setEnabled(False)

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

		self.exitLocked=True
		
		self.getPackages=getPackages(self.flavoursToInstall[0])
		self.manage_msg_box(True,False)
		self.messageLabel.setText(_("1 of 5: Obtaining information about the flavor to install..."))
		self.progressBar.show()
		self.getPackages.start()
		self.getPackages.finished.connect(self._finishGetPackages)
		
	#def launchInstall

	def _finishGetPackages(self):

		self.messageLabel.setText(_("2 of 5: Downloading packages..."))
		self.progressBar.setValue(100)
		
		self.checkProgress=QThread()
		self.worker=Worker()
		self.worker.moveToThread(self.checkProgress)
		self.checkProgress.started.connect(self.worker.run)
		self.worker._finished.connect(self.checkProgress.quit)
		self.worker._progress.connect(self._updateMessage)
		self.install=installProcess(self.flavoursToInstall[0],self.mirrorRepository)
		self.install.start()
		self.install.finished.connect(self._finishInstall)
		self.worker.running=True
		self.checkProgress.start()

	#def _finishGetPackages
	
	def _updateMessage(self,step):

		if step=="unpack":
			self.messageLabel.setText(_("3 of 5: Unpacking packages: %s of %s packages")%(str(self.core.flavourSelectorManager.progressUnpacked),len(self.core.flavourSelectorManager.initialNumberPackages)))
		elif step=="install":
			self.messageLabel.setText(_("4 of 5: Configuring packages: %s of %s packages")%(str(self.core.flavourSelectorManager.progressInstallation),len(self.core.flavourSelectorManager.initialNumberPackages)))
		elif step=="end":
			self.messageLabel.setText(_("5 of 5: Finishing the installation..."))
		
		self._updateProgressBar(step)
	#def _updateMessage		

	def _updateProgressBar(self,step):

		if step=="unpack":
			if self.core.flavourSelectorManager.progressUnpackedPercentage==0.00:
				self.progressBar.setValue(200)
			else:
				p_value=2+float(self.core.flavourSelectorManager.progressUnpackedPercentage)
				self.progressBar.setValue(p_value*100)
		elif step=="install":
			if self.core.flavourSelectorManager.progressInstallationPercentage==0.00:
				self.progressBar.setValue(300)
			else:
				p_value=3+float(self.core.flavourSelectorManager.progressInstallationPercentage)
				self.progressBar.setValue(p_value*100)
		elif step=="end":
			self.progressBar.setValue(400)

	#def _updateProgressBar

	def _finishInstall(self):

		self.progressBar.hide()
		self.worker.running=False
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
			self.manage_msg_box(False,True)	
			self.messageLabel.setText(_("An error ocurred. See log in /var/log/lliurex-flavours-selector"))					     
		else:
			self.manage_msg_box(False,False)	
			self.messageLabel.setText(_("Installation succesful. A reboot is required"))					     

		self.exitLocked=False	
	
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
		
		#mirrorDialog.buttonClicked.connect(self.mirrorDialogClicked)

		ret=mirrorDialog.exec_()
		
		if ret==QMessageBox.Yes:
			self.mirrorRepository=True
		else:
			self.mirrorRepository=False

	
	#showMirrorDialog
	'''
	def mirrorDialogClicked(self,i):

		if str(i.text()) in ["Yes","Si"]:
			self.mirrorRepository=True
		else:
			self.mirrorRepository=False
		
	#def mirrorDialogClicked
	'''
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
		
		#confirmDialog.buttonClicked.connect(self.confirmDialogClicked)

		ret=confirmDialog.exec_()
		
		if ret==QMessageBox.Ok:
			self.launchInstall()	
	
	#def showConfirmDialog

	'''
	def confirmDialogClicked(self,i):

		if str(i.text()) in ["Ok","Aceptar","D'acord"]:
			self.launchInstall()
		
	#def confirmDialogClicked
	'''
	def helpButtonClicked(self):

		lang=os.environ["LANG"]
		language=os.environ["LANGUAGE"]
		run_pkexec=False
		
		if "PKEXEC_UID" in os.environ:
			run_pkexec=True

		exec_lang=""
		app_lang=""

		if language=="":
			app_lang=lang
		else:
			language=language.split(":")[0]
			app_lang=language
		
		if 'valencia' in app_lang:
			exec_lang="LANG=ca_ES.UTF-8@valencia"
			cmd=exec_lang+' xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Canviar-sabor-en-LliureX'
		else:
			exec_lang="LANG=es_ES.UTF-8"
			cmd=exec_lang+' xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Cambiar++sabor+en+LliureX'

		if not run_pkexec:
			self.fcmd="su -c '%s' $USER" %cmd
		else:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.fcmd="su -c '" +cmd+ "' "+ user
			
		os.system(self.fcmd)

	#def helpButtonClicked		

	def closeEvent(self,event):

		if self.exitLocked:
			event.ignore()
		else:
			event.accept()			

	#def closeEvent

	def manage_msg_box(self,hide,error):

		self.progressBar.hide()
		if hide:
			self.messageImg.setStyleSheet("background-color: transparent")
			self.messageLabel.setStyleSheet("background-color: transparent")
			self.messageImg.hide()
			self.messageLabel.setAlignment(Qt.AlignCenter|Qt.AlignVCenter)

		else:
			if error:
				self.messageImg.setStyleSheet("border-bottom: 1px solid #da4453;border-left: 1px solid #da4453;border-top: 1px solid #da4453;background-color: #ebced2")
				self.messageLabel.setStyleSheet("border-bottom: 1px solid #da4453;border-right: 1px solid #da4453;border-top: 1px solid #da4453;background-color: #ebced2")
				pixmap=QPixmap(self.core.rsrc_dir+"dialog-error.png")
				self.messageImg.setPixmap(pixmap)
				self.messageImg.show()
				self.messageLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
				self.messageLabel.show()			
			else:
				self.messageImg.setStyleSheet("border-bottom: 1px solid #27ae60;border-left: 1px solid #27ae60;border-top: 1px solid #27ae60;background-color: #c7e3d4")
				self.messageLabel.setStyleSheet("border-bottom: 1px solid #27ae60;border-right: 1px solid #27ae60;border-top: 1px solid #27ae60;background-color: #c7e3d4")
				pixmap=QPixmap(self.core.rsrc_dir+"dialog-positive.png")
				self.messageImg.setPixmap(pixmap)
				self.messageImg.show()
				self.messageLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
				self.messageLabel.show()			

	#def manage_msg_box
#class MainWindow

from . import Core
