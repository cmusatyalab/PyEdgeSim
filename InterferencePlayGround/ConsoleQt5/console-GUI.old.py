#!/usr/bin/env python
# Tested on Windows with Python 3.6
import os
import sys
print(sys.path)
# conda install pyqt
# Windows Install DLLs: https://www.qt.io/download-qt-installer

import PyQt5
from PyQt5 import QtGui,QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from config import initConfig,formatConfig
from qtdbg import QDbgConsole

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
        self.initUI()
        self.CreateUI()
        self.show()
    
    def initUI(self): # Tabs not working
        self.setWindowIcon(QtGui.QIcon(ICONFN))
        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Ready')
        self.setGeometry(80, 80, 1000, 700)
        self.setWindowTitle('Copy To Device')
        ''' Progress Bar '''
        self.progress = QtWidgets.QProgressBar(self)
        #self.progress.setGeometry(80, 80, 600, 5)

    def CreateUI(self):
        self.CreateMenus()
        self.CreateMain()

    def CreateMenus(self):
        bar = self.menuBar()
        file = bar.addMenu("File")

        quit = QAction("Quit",self) 
        quit.setShortcut("Ctrl+Q")
        quit.triggered.connect(QtWidgets.qApp.quit)   
        file.addAction(quit)

    def CreateMain(self):
        widgmain = QWidget()
        vboxmain = QVBoxLayout()
        basecnf = initConfig()
        ''' Configure UI '''
        
        ''' options '''
        vboxoptions = QVBoxLayout()
        hboxoptions = QHBoxLayout()
        vboxcheck = QVBoxLayout()
#         hboxupdate =  QHBoxLayout()
        
        cbox1=QLabel()
        cbox1.setText("Options:")
        cbox1.setAlignment(Qt.AlignLeft)
        
        ''' Check Boxes '''
        self.option_list = {
            "check":{"MESSAGE":"Check Device Music Files","type":"button"},
            "genplaylist":{"MESSAGE":"Generate All Device Playlists","type":"button"},
            "plexdelete":{"MESSAGE":"Delete All Plex Playlists","type":"button"},
            "plex":{"MESSAGE":"Update All Plex Playlists","type":"button"},
            "randplaylist":{"MESSAGE":"Create Random Playlists","type":"button"},
            "updatetags":{"MESSAGE":"Update Tag Database (slow)","type":"checkbox"},
            "reverse":{"MESSAGE":"Check in reverse -- identify difference on destination","type":"button"},
            "badfiles":{"MESSAGE":"Fix non-ascii file and directory names","type":"button"}
        }
        
        self.update_list = {
            "fix":{"LABEL":"Update Device Music Files","MESSAGE":"Which Device's music files should be updated?"},
            "updateplaylists":{"LABEL":"Update Device Playlists","MESSAGE":"Which Device's playlists should be updated?"}
        }

        ''' Option Buttons '''
        self.cb_option_buttons = {}
        for key in self.option_list.keys():
            if self.option_list[key]['type'] == "button":
                self.cb_option_buttons[key] = option_button(key,self.option_list[key],self)
            elif self.option_list[key]['type'] == "checkbox":
                self.cb_option_buttons[key] = option_checkbox(key,self.option_list[key],self)
                
        
        self.cb_update_buttons = {}
        devicelst = [key for key in basecnf['DEVICES'].keys()] + [key for key in basecnf['PLEXSERVERS'].keys()]
        for key in self.update_list.keys():
            self.cb_update_buttons[key] = update_button(key,self.update_list[key],devicelst)
        
        ''' Add Boxes and Buttons to UI '''
        vboxoptions.addWidget(cbox1)
        [vboxcheck.addWidget(self.cb_update_buttons[key]) \
            for key in self.cb_update_buttons.keys()]
        
        [vboxcheck.addWidget(self.cb_option_buttons[key]) \
            for key in self.cb_option_buttons.keys()]

        hboxoptions.addLayout(vboxcheck)
        vboxoptions.addLayout(hboxoptions)

        ''' add options to main layout '''
        vboxmain.addLayout(vboxoptions)
        
        ''' Form '''
        vboxform = QFormLayout()
        l1 = QLabel("Source")
        default_srcDir = "TODO"
        self.srcDir = QLineEdit(default_srcDir)

        l2 = QLabel("Destination")
        default_dstDir = "TODO"
        self.dstDir = QLineEdit(default_dstDir)

        l3 = QLabel("Device playlist prefix")
        try:
            plylstprefdef = basecnf['DEVICES'][next(iter(basecnf['DEVICES']))]['PREFIX'] # Get first
        except:
            plylstprefdef = "/storage/6664-3166"
        self.plylstPref = QLineEdit(plylstprefdef)        
        
        vboxform.addRow(l1,self.srcDir)
        vboxform.addRow(l2,self.dstDir)
        vboxform.addRow(l3,self.plylstPref)
        hboxoptions.addLayout(vboxform)

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
    def __init__(self, blabel, optiondict, parent = None):
        super(option_button, self).__init__()
        self.setText("{}".format(optiondict['MESSAGE']))
        self.clicked.connect(self.option_button_clicked)
        self.optiondict = optiondict
        self.blabel = blabel
    def option_button_clicked(self):
        console("Option button pushed: {}".format(self.blabel))
        kwargs = {key: False for key in win.cb_option_buttons.keys() }
        kwargs.update({key: False for key in win.cb_update_buttons.keys() })
        kwargs.update(self.getFieldInfo())
        kwargs[self.blabel] = True
        if self.blabel == 'badfiles': kwargs['fix'] = True # No option for just checking
        kwargs['win'] = win
        job_execute(kwargs)
    def getFieldInfo(self):
        retdict = {
            "SRCPATH":str(win.srcDir.text()),
            "DSTPATH":str(win.dstDir.text()),
            "DEVSTOREDIR":str(win.plylstPref.text()),
            "plex":False,
            "batchFile":None,
            "devicename":None,
            "updatetags": win.cb_option_buttons['updatetags'].state,
            "badfiles": False # TODO
        }
        return retdict

class option_checkbox(QtWidgets.QCheckBox):
    def __init__(self, blabel, optiondict, parent = None):
        super(option_checkbox, self).__init__()
        self.setText("{}".format(optiondict['MESSAGE']))
        self.stateChanged.connect(self.option_checkbox_clicked)
        self.optiondict = optiondict
        self.blabel = blabel
        self.state = False
    def option_checkbox_clicked(self,state):
        self.state = True if state == Qt.Checked else False

    def getFieldInfo(self):
        retdict = {
            "SRCPATH":str(win.srcDir.text()),
            "DSTPATH":str(win.dstDir.text()),
            "DEVSTOREDIR":str(win.plylstPref.text()),
            "plex":False,
            "batchFile":None,
            "devicename":None,
            "badfiles": False # TODO
        }
        return retdict

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
            "SRCPATH":str(win.srcDir.text()),
            "DSTPATH":str(win.dstDir.text()),
            "DEVSTOREDIR":str(win.plylstPref.text()),
            "plex":False,
            "batchFile":None,
            "devicename":None
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

