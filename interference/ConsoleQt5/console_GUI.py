#!/usr/bin/env python
# Tested on Windows with Python 3.6
import os
import sys
print(sys.path)
sys.path.append("..")
# conda install pyqt
# Windows Install DLLs: https://www.qt.io/download-qt-installer

import PyQt5
from PyQt5 import QtGui,QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from config import initConfig,formatConfig
from qtdbg import QDbgConsole

from console_exec import job_execute

ICONFN = "win7_ico_shell32_dll-119.png"
def window():
    ''' Base window '''
    global win
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    initial_message()
    sys.exit(app.exec_())


''' window configuration '''
class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.basecnf = initConfig()
        self.initUI()
        self.CreateUI()
        self.show()
    
    def initUI(self): # Tabs not working
        self.setWindowIcon(QtGui.QIcon(ICONFN))
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        self.setGeometry(1500, 620, 400, 250)
        self.setWindowTitle('Network Interference Manager')
        ''' Progress Bar '''
        self.progress = QtWidgets.QProgressBar(self)
        #self.progress.setGeometry(80, 80, 600, 5)

    def CreateUI(self):
        self.CreateMenus()
        self.CreateMain()

    def CreateMenus(self):
        bar = self.menuBar()
        # file = bar.addMenu("File")

        quit = QAction("Quit",self) 
        quit.setShortcut("Ctrl+Q")
        quit.triggered.connect(QtWidgets.qApp.quit)   
        # file.addAction(quit)

    def CreateMain(self):
        widgmain = QWidget()
        vboxmain = QVBoxLayout()
        ''' Configure UI '''
        
        ''' options '''
        vboxoptions = QVBoxLayout()
        hboxoptions = QHBoxLayout()
        vboxcheck = QVBoxLayout()
        
        cbox1=QLabel()
        cbox1.setText("Options:")
        cbox1.setAlignment(Qt.AlignLeft)
        
        ''' Check Boxes '''
        self.option_list = {
            "zero":{"MESSAGE":"Run with no added latency (e.g., wired, wifi)","type":"button"},
            "NLTE":{"MESSAGE":"Run as 4G LTE network","type":"button"},
            "N5G":{"MESSAGE":"Run as 5G Network","type":"button"},
            "RANDOM":{"MESSAGE":"Run with mix","type":"button"},
            "PROFILE":{"MESSAGE":"Run with profile","type":"button"},
            "APIGEN":{"MESSAGE":"Regenerate APIs for this sandbox/scenario combo","type":"button"},
            "interference":{"MESSAGE":"Run with interference","type":"checkbox"},
            "lbo":{"MESSAGE":"Run with edge computing","type":"checkbox"}
        }
        
        ''' Option Buttons '''
        self.cb_option_buttons = {}
        for key in self.option_list.keys():
            if self.option_list[key]['type'] == "button":
                self.cb_option_buttons[key] = option_button(key,self.option_list[key],self.basecnf,self)
                vboxoptions.addWidget(self.cb_option_buttons[key])
                
            elif self.option_list[key]['type'] == "checkbox":
                self.cb_option_buttons[key] = option_checkbox(key,self.option_list[key],self.basecnf,self)
                hboxoptions.addWidget(self.cb_option_buttons[key])
        ''' Add Boxes and Buttons to UI '''
        

        vboxoptions.addLayout(hboxoptions)

        ''' add options to main layout '''
        vboxmain.addLayout(vboxoptions)
        
        ''' Form '''
        cnf = self.basecnf
        vboxform = QFormLayout()
        l1 = QLabel("Sandbox")
        default_sandBox = cnf['SANDBOX'] if 'SANDBOX' in cnf else "horizon-filter-1"
        self.sandBox = QLineEdit(default_sandBox)

        l2 = QLabel("Scenario")
        default_scenario = cnf['SCENARIO'] if 'SCENARIO' in cnf else "horizon-filter-1"
        self.scenario = QLineEdit(default_scenario)
        
        l3 = QLabel("Profile")
        default_profile = cnf['PROFILE'] if 'PROFILE' in cnf else "NA"
        self.profile = QLineEdit(default_profile)  
        
        vboxform.addRow(l1,self.sandBox)
        vboxform.addRow(l2,self.scenario)
        vboxform.addRow(l3,self.profile)
        
        vboxmain.addLayout(vboxform)

        ''' logging console '''
        vboxconsole = QVBoxLayout()
        self.dbgwidg = QDbgConsole()
        vboxconsole.addWidget(self.dbgwidg)
        
        vboxmain.addLayout(vboxconsole)
        
        ''' Quit Button '''
        quit_buttn = quit_button("QUIT")
        vboxmain.addWidget(quit_buttn)
        ''' put the progress bar on the botttom '''
        vboxmain.addWidget(self.progress)
        ''' Set the Layout '''
        widgmain.setLayout(vboxmain)
        self.setCentralWidget(widgmain)


class option_button(QtWidgets.QPushButton):
    def __init__(self, blabel, optiondict, cnf, parent = None):
        super(option_button, self).__init__()
        self.message = optiondict['MESSAGE']
        self.setText("{}".format(self.message))
        self.clicked.connect(self.option_button_clicked)
        self.optiondict = optiondict
        self.blabel = blabel
        self.cnf = cnf
        
    def option_button_clicked(self):
        # console("Option selected: {}".format(self.message))
        kwargs = {key: False for key in win.cb_option_buttons.keys() }
        kwargs.update(self.getFieldInfo())
        kwargs[self.blabel] = True
        kwargs['win'] = win
        kwargs['cnf'] = self.cnf
        job_execute(kwargs)
    def getFieldInfo(self):
        retdict = {}
        try:
            retdict = {
                "interference": win.cb_option_buttons['interference'].state,
                "lbo": win.cb_option_buttons['lbo'].state,
                "sandbox":str(win.sandBox.text()),
                "scenario":str(win.scenario.text()),
                "profile":str(win.profile.text()),
            }
        except Exception as e:
            console(f"Error: {e}")
        console(f"Option selected: {self.message} with\n\tinterference={retdict['interference']}, edge computing={retdict['lbo']}")
        return retdict

class option_checkbox(QtWidgets.QCheckBox):
    def __init__(self, blabel, optiondict, cnf, parent = None):
        super(option_checkbox, self).__init__()
        self.setText(f"{optiondict['MESSAGE']}")
        self.stateChanged.connect(self.option_checkbox_clicked)
        self.optiondict = optiondict
        self.blabel = blabel
        self.cnf = cnf
        self.state = False
        
    def option_checkbox_clicked(self,state):
        self.state = True if state == Qt.Checked else False
        return self.state

class update_button(QtWidgets.QPushButton):
    def __init__(self, key, updatedict, devicelst = [],parent = None):
        super(update_button, self).__init__()
        self.msg = updatedict['MESSAGE']
        self.blabel = updatedict['LABEL']
        self.devicelst = devicelst
        self.key = key
        self.setText("{}".format(self.blabel))
        self.clicked.connect(self.update_button_clicked)

    def update_button_clicked(self):
        console("Update button pushed: {}".format(self.blabel))
        msgbx = update_message(self.key,self.devicelst,self.blabel,self.msg,win)
        msgbx.exec_() # Show
        pass
        # return retdict

class update_message(QtWidgets.QDialog):
    def __init__(self, key, devicelst, blabel, msg, swin, parent = None):
        super(update_message, self).__init__()
        self.setWindowTitle("Update Playlists on Device")
        self.win = swin
        self.blabel = blabel
        self.msg = msg
        self.key = key
        ''' Configure the Layout '''
        ''' Basics '''
        self.vboxLayout = QVBoxLayout()
        self.label = QLabel(msg)
        self.vboxLayout.addWidget(self.label)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_clicked)
        self.resize(300, 150)
        imglabel = QLabel(self)
        pixmap = QPixmap(ICONFN)
        imglabel.setPixmap(pixmap)
        self.vboxLayout.addWidget(imglabel)
        
        ''' Content '''
        self.radios = {}
        for radio in devicelst:
            self.radios[radio] = QRadioButton("{}".format(radio))
            if len(self.radios) == 1: # Select the first by default
                self.radios[radio].setChecked(True)
            self.vboxLayout.addWidget(self.radios[radio])
        
        ''' Set it '''
        self.vboxLayout.addWidget(self.ok_button)
        self.vboxLayout.addWidget(self.cancel_button)
        self.setLayout(self.vboxLayout)
        
    def ok_clicked(self):
        console("Update button pushed")
        kwargs = self.getFieldInfo()
        kwargs.update({key: False for key in win.cb_update_buttons.keys() })
        kwargs.update({key: False for key in win.cb_option_buttons.keys() })
        for key in self.radios.keys():
            if self.radios[key].isChecked():
                console("Updating {} playlists".format(key))
                kwargs['devicename'] = key
        kwargs[self.key] = True
        kwargs['win'] = win
        kwargs[self.key] = True
        self.close()
        job_execute(kwargs)
        pass

    def cancel_clicked(self):
        console("Cancel button pushed")
        self.close()
   
    def getFieldInfo(self):
        retdict = {
            "SRCPATH":str(win.sandBox.text()),
            "DSTPATH":str(win.scenario.text()),
            "DEVSTOREDIR":str(win.plylstPref.text()),
        }
        return retdict


class quit_button(QtWidgets.QPushButton):
    def __init__(self, blabel, parent = None):
        super(quit_button, self).__init__()
        self.setText(blabel)
        self.clicked.connect(self.quit_button_clicked)
    def quit_button_clicked(self,cb_fix):
        console("Quit button pushed")
        sys.exit(0)
        
def initial_message():
    initf = "./initmsg.txt"
    if os.path.isfile(initf):
        with open(initf,"r") as f:
            initmsg = [line.rstrip() for line in f.readlines()]
    initmsg = initmsg + formatConfig() + ["Ready!"]
    [console(line) for line in initmsg]

def console(msg):
    print(msg)
# TODO fix dbgwidg
    if win is not None:
        win.dbgwidg.write(str(msg + "\n"))
        win.statusbar.showMessage(msg)

if __name__ == '__main__': window()

