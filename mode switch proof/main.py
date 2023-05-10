import sys

from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QHBoxLayout, QLayout, QVBoxLayout, QMainWindow, QPushButton, QShortcut, QLabel, QListWidget, QWidget, QListWidgetItem, QTableWidgetItem, QProxyStyle, QDesktopWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import QCoreApplication, QObject, QThread, QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QColor, QFont, QKeySequence, QFontInfo, QPalette, QPixmap

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

"""
1) Open Menu, get user input for desired resolution
2) load UI file based on user in
3) complete button functionality
"""

class menu_page(QMainWindow):
    def __init__(self):
        super().__init__() #dont understand this line
        #load Ui, populate dropdown, create button functionality
        loadUi('resoSelect.ui',self)
        
        self.comboBox.addItem("1920x1080")
        self.comboBox.addItem("1280x720")
        
        self.pushButton.clicked.connect(self.hitButt)
    
    def hitButt(self):
        #create instance of worker window, pass in comboBox input
        self.pushButton.setText('clickd')
        self.working = worker(reso = self.comboBox.currentText())
        #self.working.show()
        self.working.showFullScreen()


class worker(QMainWindow):
    def __init__(self, reso):
        super().__init__()

        #open UI window corresponding to reso
        if reso == "1920x1080":
            loadUi('1080.ui',self)
        else:
            loadUi('720.ui',self)
        
        #button functionality connection
        self.left.clicked.connect(self.switchRight)
        self.right.clicked.connect(self.switchLeft)

    def switchRight(self):
        self.pic.setPixmap(QtGui.QPixmap('./img/monkee.jpg'))

    def switchLeft(self):
        self.pic.setPixmap(QtGui.QPixmap('./img/OG.jpg'))
        

app = QApplication(sys.argv)
window = menu_page()
window.show()
app.exec()