import sys
import zmq
# we need a serializer (dont know what this is)
import msgpack
#slow down messages
import time, random

from threading import *

import inspect

from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QHBoxLayout, QLayout, QVBoxLayout, QMainWindow, QPushButton, QShortcut, QLabel, QListWidget, QWidget, QListWidgetItem, QTableWidgetItem, QProxyStyle, QDesktopWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import QCoreApplication, QObject, QThread, QTimer, pyqtSignal, Qt, QRunnable, QThreadPool
from PyQt5.QtGui import QColor, QFont, QKeySequence, QFontInfo, QPalette, QPixmap

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

#https://github.com/Givo29/pyqt5-threading

#https://realpython.com/python-pyqt-qthread/
#https://wiki.python.org/moin/PyQt5/Threading%2C_Signals_and_Slots

class menu_page(QMainWindow):
    def __init__(self):
        super(QMainWindow,self).__init__() 
        loadUi('surfaces.ui',self)

        self.reportProgress = 0

        self.brokeButt.clicked.connect(self.Broke)
        self.initButt.clicked.connect(self.Driver)
        self.stopButt.clicked.connect(self.StopData)

        self.threadpool = QThreadPool()

        self.sigs = WorkerSignals()
    
    def Broke(self):
        if self.broketxt.text() == "1":
            self.broketxt.setText("2")
        else:
            self.broketxt.setText("1")

    def Driver(self):
        self.statustxt.setText("Streaming data...")

        self.worker = Worker()
        self.worker.signals.result.connect(self.Updater)
        self.worker.signals.finished.connect(self.DoneStreaming)
        self.threadpool.start(self.worker)

        self.initButt.setEnabled(False)

    def DoneStreaming(self):
        self.statustxt.setText("Done streaming.")

    def StopData(self):
        self.worker.signals.end.emit()


    def Updater(self, confidence, state, subnum):
        if confidence >= .9:
            match subnum:
                case 0:
                    self.MessageChange(state,self.s1txt)
                case 1:
                    self.MessageChange(state,self.s2txt)
                case 2:
                    self.MessageChange(state,self.s3txt)
                case 3:
                    self.MessageChange(state,self.s4txt)
                case 4:
                    self.MessageChange(state,self.s5txt)
                case 5:
                    self.MessageChange(state,self.s6txt)
                case _:
                    print("[ERROR] Invalid subnum")

    def MessageChange(self,state,label):
        if state:
            label.setText("!!!LOOKING!!!")
        else:
            label.setText("!!!LOOKING!!!")

#signal class
class WorkerSignals(QObject):
    finished = pyqtSignal()
    #this signal passes confidence, state, and sub number back to handler function
    result = pyqtSignal(float, bool, int)
    end = pyqtSignal()

#worker thread
class Worker(QRunnable):
    def __init__(self):
        super(Worker, self).__init__()

        self.signals = WorkerSignals()
        self.runflag = True
        #self.signals.end.connect(self.Stop)
        

    
    # def Stop(self):
    #     self.runflag = False

    def run(self):
        print("running...")

        i = 0
        while i < 200:          
            self.signals.result.emit(.95, bool(random.randint(0,1)), i % 6);
            time.sleep(.25)
            i += 1
            print(i)

        print("done.")
        self.signals.finished.emit()

    
    # def run(self):
    #     print("running...")
    #     # INIT datastream in done in init of class
    #     self.ctx = zmq.Context()
    #     # The REQ talks to Pupil remote and receives the session unique IPC SUB PORT
    #     self.pupil_remote = self.ctx.socket(zmq.REQ)

    #     self.ip = 'localhost'  # If you talk to a different machine use its IP.
    #     self.port = 50020  # The port defaults to 50020. Set in Pupil Capture GUI.

    #     self.pupil_remote.connect(f'tcp://{self.ip}:{self.port}')

    #     # Request 'SUB_PORT' for reading data
    #     self.pupil_remote.send_string('SUB_PORT')
    #     self.sub_port = self.pupil_remote.recv_string()

    #     # Request 'PUB_PORT' for writing data
    #     self.pupil_remote.send_string('PUB_PORT')
    #     self.pub_port = self.pupil_remote.recv_string()

    #     # Assumes `sub_port` to be set to the current subscription port
    #     #init all the subscribers for the surface data collection
    #     self.subscriber_s1 = self.ctx.socket(zmq.SUB)
    #     self.subscriber_s2 = self.ctx.socket(zmq.SUB)
    #     self.subscriber_s3 = self.ctx.socket(zmq.SUB)
    #     self.subscriber_s4 = self.ctx.socket(zmq.SUB)
    #     self.subscriber_s5 = self.ctx.socket(zmq.SUB)
    #     self.subscriber_s6 = self.ctx.socket(zmq.SUB)

    #     self.subscriber_s1.connect(f'tcp://{self.ip}:{self.sub_port}')
    #     self.subscriber_s1.subscribe('surfaces.s1') # receive all surface.s1 messages
    #     # self.subscriber_s2.connect(f'tcp://{self.ip}:{self.sub_port}')
    #     # self.subscriber_s2.subscribe('surfaces.s2') # receive all surface.s1 messages
    #     # self.subscriber_s3.connect(f'tcp://{self.ip}:{self.sub_port}')
    #     # self.subscriber_s3.subscribe('surfaces.s3') # receive all surface.s1 messages
    #     # self.subscriber_s4.connect(f'tcp://{self.ip}:{self.sub_port}')
    #     # self.subscriber_s4.subscribe('surfaces.s4') # receive all surface.s1 messages
    #     # self.subscriber_s5.connect(f'tcp://{self.ip}:{self.sub_port}')
    #     # self.subscriber_s5.subscribe('surfaces.s5') # receive all surface.s1 messages
    #     # self.subscriber_s6.connect(f'tcp://{self.ip}:{self.sub_port}')
    #     # self.subscriber_s6.subscribe('surfaces.s6') # receive all surface.s1 messages
        
    #     #list of subscribers
    #     self.subs = [self.subscriber_s1, self.subscriber_s2, self.subscriber_s3, self.subscriber_s4, self.subscriber_s5, self.subscriber_s6]

    #     i = 0
    #     messagecounter = 0
    #     while i < 1000:
    #         for obj in self.subs:
    #             topic, payload = obj.recv_multipart()
    #             message = msgpack.loads(payload)
    #             vals = message.get(b'gaze_on_surfaces')
    #             vals = vals[0]
    #             self.signals.result.emit(vals.get(b'confidence'), vals.get(b'on_surf'), messagecounter % 6);
    #             messagecounter += 1
    #         #load the most recent message
    #         # topic, payload = self.subscriber_s1.recv_multipart()
    #         # message = msgpack.loads(payload)
    #         # vals = message.get(b'gaze_on_surfaces')
    #         # vals = vals[0]
    #         # self.signals.result.emit(vals.get(b'confidence'), vals.get(b'on_surf'));
    #         i += 1
    #     print("done")
            

    # def recordData(self):
    #     print('in recordData call')
    #     self.i = 0
    #     while self.i < 200:
    #         self.topic, self.payload = self.subscriber.recv_multipart()
    #         self.message = msgpack.loads(self.payload)
    #         self.vals = self.message.get(b'gaze_on_surfaces')
            
    #         self.i += 1
    #         for object in self.vals:
    #             #print(self.i)
    #             self.tf = object.get(b'on_surf')
    #             if self.tf is True:
    #                 #self.indi.setText("Looking")
    #                 print('l')
    #             elif self.tf is False:
    #                 #self.indi.setText("Not looking")
    #                 print('nl')
    #             else:
    #                 #self.indi.setText("not t/f")
    #                 print('n')
    #         # if self.vals[0].get(b'on_surf') is True:
    #         #     self.indi.setText("Looking")
    #         # else:
    #         #     self.indi.setText("Not looking")        

app = QApplication(sys.argv)
window = menu_page()
window.show()
app.exec()

#https://realpython.com/python-pyqt-qthread/




