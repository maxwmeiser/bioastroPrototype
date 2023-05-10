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

'''
This simple program is meant to demonstrate pyqt multithreading and reading data in from the PupilLabs eyetracking API simultaneously

A primary issue with reading the eyetracking data in the main pyqt event thread was that it would clog the thread, not giving any time
for updates/changes to the GUI. By using a worker thread and signals, I was able to send interpreted data from the eyetracking API to the
main thread to update elements of the GUI real time
'''
#for future work and two-way signaling https://stackoverflow.com/questions/35527439/pyqt4-wait-in-thread-for-user-input-from-gui/35534047#35534047

#https://github.com/Givo29/pyqt5-threading

#https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
#this ^ is the resource I used most

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
    
    #small proccess to indicate the main GUI thread isnt stuck and the GUI can be updated 
    def Broke(self):
        if self.broketxt.text() == "1":
            self.broketxt.setText("2")
        else:
            self.broketxt.setText("1")

    #Creates and starts worker thread 
    def Driver(self):
        self.statustxt.setText("Streaming data...")

        self.worker = Worker()
        self.worker.signals.result.connect(self.Updater)
        self.worker.signals.finished.connect(self.DoneStreaming)
        self.threadpool.start(self.worker)

        self.initButt.setEnabled(False)

    #This method runs when we're done streaming data. It cleans up the opened threads
    def DoneStreaming(self):
        self.statustxt.setText("Done streaming.")

    def StopData(self):
        #this doesnt do anything
        self.sigs.end.emit()

    #updates the surface labels based of data from worker signals
    def Updater(self, confidence, state, subnum):
        print(str(state) + " firing " + str(subnum))
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

    #helper function for updater
    def MessageChange(self,state,label):
        if state:
            label.setText("!!!LOOKING!!!")
        else:
            label.setText("not looking")

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
    
    #we must override the run function. This method automatically runs when the thread is started
    def run(self):
        print("running...")
        # INIT datastream in done in init of class
        self.ctx = zmq.Context()
        # The REQ talks to Pupil remote and receives the session unique IPC SUB PORT
        self.pupil_remote = self.ctx.socket(zmq.REQ)

        self.ip = 'localhost'  # If you talk to a different machine use its IP.
        self.port = 50020  # The port defaults to 50020. Set in Pupil Capture GUI.

        self.pupil_remote.connect(f'tcp://{self.ip}:{self.port}')

        # Request 'SUB_PORT' for reading data
        self.pupil_remote.send_string('SUB_PORT')
        self.sub_port = self.pupil_remote.recv_string()

        # Request 'PUB_PORT' for writing data
        self.pupil_remote.send_string('PUB_PORT')
        self.pub_port = self.pupil_remote.recv_string()

        # Assumes `sub_port` to be set to the current subscription port
        #init all the subscribers for the surface data collection
        self.subscriber_s1 = self.ctx.socket(zmq.SUB)
        self.subscriber_s2 = self.ctx.socket(zmq.SUB)
        self.subscriber_s3 = self.ctx.socket(zmq.SUB)
        self.subscriber_s4 = self.ctx.socket(zmq.SUB)
        self.subscriber_s5 = self.ctx.socket(zmq.SUB)
        self.subscriber_s6 = self.ctx.socket(zmq.SUB)

        self.subscriber_s1.connect(f'tcp://{self.ip}:{self.sub_port}')
        self.subscriber_s1.subscribe('surfaces.s1') # receive all surface.s1 messages
        self.subscriber_s2.connect(f'tcp://{self.ip}:{self.sub_port}')
        self.subscriber_s2.subscribe('surfaces.s2') # receive all surface.s2 messages
        self.subscriber_s3.connect(f'tcp://{self.ip}:{self.sub_port}')
        self.subscriber_s3.subscribe('surfaces.s3') # receive all surface.s3 messages
        self.subscriber_s4.connect(f'tcp://{self.ip}:{self.sub_port}')
        self.subscriber_s4.subscribe('surfaces.s4') # receive all surface.s4 messages
        
        #list of subscribers
        self.subs = [self.subscriber_s1, self.subscriber_s2, self.subscriber_s3, self.subscriber_s4]

        i = 0
        messagecounter = 0
        while i < 1000:
            for obj in self.subs:
                topic, payload = obj.recv_multipart()
                message = msgpack.loads(payload)
                vals = message.get('gaze_on_surfaces')
                vals = vals[0]
                self.signals.result.emit(vals.get(b'confidence'), vals.get(b'on_surf'), messagecounter % 6);
                messagecounter += 1
            i += 1
        print("done")
        self.signals.finished.emit()

    # another overloaded run function. This method doesnt require eyetracking data. It randomly updates the surfaces text
    # def run(self):
    #     print("running...")
    #     i = 0
    #     while i < 25:          
    #         self.signals.result.emit(.95, bool(random.randint(0,1)), i % 6);
    #         time.sleep(.25)
    #         i += 1
    #         print(i)
    #     print("done.")
    #     self.signals.finished.emit()    

app = QApplication(sys.argv)
window = menu_page()
window.show()
app.exec()




