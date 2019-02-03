#----ProjectTracker----#

#Imports
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

from subprocess import Popen

import Database as DB
import threading
import time
import win32gui as w
import os
import sys

#Globals
running = True
currentWindow = ""
currentProject = ""

#App
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(720, 480)
        self.setWindowTitle("Project Tracker")
        #self.setWindowIcon(QIcon("icon.png"))
        layout = QHBoxLayout()

        self.projectSelect = QComboBox()
        self.projectSelect.addItem("Select One")
        self.projectSelect.addItems(DB.getProjectNames())
        self.projectSelect.currentIndexChanged.connect(self.selectionChange)

        self.projectSelect.setCurrentIndex(DB.getProjectNames().index(DB.getActiveProjectName()) + 1)

        layout.addWidget(self.projectSelect)

        self.setLayout(layout)        

    def selectionChange(self, i):
        global currentProject
        print("Current selection: (", i, ") ", self.projectSelect.currentText())
        if(i == 0):
            currentProject = None
        else:
            currentProject = self.projectSelect.currentText()
            DB.changeActiveProject(currentProject)



#Database Setup
DB.setUpDatabase()
DB.setUpTables()

def getActiveWindowName():
    return w.GetWindowText(w.GetForegroundWindow())

def getActiveWindowType():
    name = getActiveWindowName()
    idx = name.rfind("- ")
    if(idx == -1):
        idx = 0
    else:
        idx += 2
    return name[idx:]

def main():
    global running

    currentProject = DB.getActiveProjectName()

    print("Database:")
    for project in DB.getProjectNames():
        print("Project: " + project)
        for program in DB.getProgramNames(project):
            print("\tProgram: " + program)

    pUpdate = threading.Thread(name="programUpdate", target=programUpdate)
    pUpdate.start()

    app = QApplication([])
    window = Window()
    window.show()
    app.exec_()
    while running:
        window.show()
    

def programUpdate():
    global running
    global currentWindow
    global currentProject
    while running:
        currentWindow = getActiveWindowType()
        print(currentProject, currentWindow)
        time.sleep(1)

if(__name__ == "__main__"):

    main()
