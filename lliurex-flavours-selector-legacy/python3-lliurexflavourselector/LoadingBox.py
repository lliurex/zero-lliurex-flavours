#!/usr/bin/env python3
import sys
import os
from PyQt5 import uic
from PyQt5.QtGui import QIcon,QPixmap
from PyQt5.QtCore import Qt,QEvent
from PyQt5.QtWidgets import QLabel, QWidget,QVBoxLayout,QHBoxLayout,QSizePolicy

from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

class LoadingBox(QWidget):
    def __init__(self):
        super(LoadingBox, self).__init__() # Call the inherited classes __init__ method
        
        self.core=Core.Core.get_core()

       	ui_file=self.core.rsrc_dir+"loadingBox.ui"

        uic.loadUi(ui_file, self) # Load the .ui file

        self.spinnerBox = self.findChild(QVBoxLayout, 'spinnerBox')
        self.msgBox=self.findChild(QVBoxLayout,'msgBox')
        self.labelBox=self.findChild(QHBoxLayout,'labelBox')
        self.msgLabel=self.findChild(QLabel,'msgLabel')
        self.msgLabel.setText(_("Checking system..."))

        spinner_gif=self.core.rsrc_dir+"loading.gif"
        self.spinner=self.core.waitingSpinner
        self.spinner.setGif(spinner_gif)
        self.spinnerBox.addWidget(self.spinner)
        self.spinner.setAlignment(Qt.AlignCenter|Qt.AlignBottom)
        self.spinner.start()
    
    #def __init__

#class LoadingBox
from . import Core