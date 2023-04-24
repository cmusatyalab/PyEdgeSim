#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
qtdbg.py

A simple PyQt output widget.
It's main use case is to serve as an output console, for debugging or 
other purposes.
It provides a file-like interface for ease of integration with other
python features such as the logging module, on top of a slightly 
pre-set QTextEdit widget.
Since it inherits QTextEdit directly, all of the widget's methods are
available directly for further customization or GUI integration.

Tested on:
    - Python 3.2, PyQt4, win7

Author:  raphi <r.gaziano@gmail.com>
Created: 08/01/2013
Version: 1.0
"""
from io import StringIO
from PyQt5 import QtGui,QtWidgets

def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    widget = QDbgConsole(400,20)
    widget.write("TestMessage, yay \o/")
    widget.seek(0)
    widget.read()
    
    widget.seek(0)
    
    s = widget.read(4)
    assert(len(s) == 4)
    print(s)

class QDbgConsole(QtWidgets.QTextEdit):
    '''
    A simple QTextEdit, with a few pre-set attributes and a file-like
    interface.
    '''
    # Feel free to adjust those
    WIDTH  = 480
    HEIGHT = 50
    
    def __init__(self, w=WIDTH, h=HEIGHT, parent=None):
        super(QDbgConsole, self).__init__(parent)
        
        self._buffer = StringIO()

        self.resize(w, h)
        self.setReadOnly(True)

    ### File-like interface ###
    ###########################

    def write(self, msg):
        '''Add msg to the console's output, on a new line.'''
        self.insertPlainText(msg)
        # Autoscroll
        self.moveCursor(QtGui.QTextCursor.End)
        self._buffer.write(str(msg))

    # Most of the file API is provided by the contained StringIO 
    # buffer.
    # You can redefine any of those methods here if needed.

    def __getattr__(self, attr):
        '''
        Fall back to the buffer object if an attribute can't be found.
        '''
        return getattr(self._buffer, attr)


# -- Testing
if __name__ == '__main__': main()
#     import doctest
#     doctest.testmod(verbose=True)