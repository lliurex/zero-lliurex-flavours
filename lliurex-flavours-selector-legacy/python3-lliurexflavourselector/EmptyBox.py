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

class EmptyBox(QWidget):
    def __init__(self):
        super(EmptyBox, self).__init__() # Call the inherited classes __init__ method
        
        self.core=Core.Core.get_core()

       	ui_file=self.core.rsrc_dir+"emptyBox.ui"

        uic.loadUi(ui_file, self) # Load the .ui file

        self.scrollArea=self.findChild(QWidget,'scrollAreaWidgetContents')
        self.scrollArea.setStyleSheet("background-color:white")
        self.emptyBox=self.findChild(QHBoxLayout,'emptyBox')
        self.emptyLabel=self.findChild(QLabel,'emptyLabel')
        self.emptyLabel.setText(_("The flavours list is empty"))

    
    #def __init__

#class EmptyBox
from . import Core