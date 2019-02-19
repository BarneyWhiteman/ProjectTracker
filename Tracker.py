#----ProjectTracker----#

#Imports
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

import win32gui as w
import win32process

import Database as DB

import threading
import time
import psutil

#Globals
running = True
prevWindow = ""
currentWindow = ""
currentProject = ""
currentWindowTimer = 0

#App
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(720, 480)
        self.setWindowTitle("Project Tracker")
        #self.setWindowIcon(QIcon("icon.png"))
        layout = QHBoxLayout()

        #PROJECT SELECT BOX
        self.projectSelect = QComboBox()
        self.projectSelect.addItem("Select One")
        self.projectSelect.addItems(DB.getProjectNames())
        
        index = 0
        try:
            index = DB.getProjectNames().index(DB.getActiveProjectName()) + 1
        except ValueError as e:
            print(e)

        self.projectSelect.setCurrentIndex(index)
        
        self.projectSelect.currentIndexChanged.connect(self.selectionChange)
        
        layout.addWidget(self.projectSelect)


        #PROGRAM VIEW TABLE
        self.programTable = QTableWidget()
        self.populateProgramTable()

        layout.addWidget(self.programTable)

        self.setLayout(layout)

    def selectionChange(self, i):
        global currentProject
        print("Current selection: (", i, ") ", self.projectSelect.currentText())
        if(i == 0):
            currentProject = None
        else:
            currentProject = self.projectSelect.currentText()
            DB.changeActiveProject(currentProject)
            self.populateProgramTable()
    
    def populateProgramTable(self):
        programs = DB.getProgramNames(DB.getActiveProjectName())

        self.programTable.setRowCount(len(programs))
        self.programTable.setColumnCount(2)

        for i in range(len(programs)):
            self.programTable.setItem(0, i, QTableWidgetItem(programs[i]))
            self.programTable.setItem(1, i, QTableWidgetItem(4))




#Database Setup
DB.setUpDatabase()
DB.setUpTables()



def getActiveWindowName():
    #Gets and returns the name of the currently active window
    return w.GetWindowText(w.GetForegroundWindow())

def getActiveWindowType():
    #Clips the active window name into a usable program name
    name = getActiveWindowName()
    idx = name.rfind("- ")
    if(idx == -1):
        idx = 0
    else:
        idx += 2
    return name[idx:]

def getActiveWindow():
    pid = win32process.GetWindowThreadProcessId(w.GetForegroundWindow())
    name = psutil.Process(pid[-1]).name()

    name = name.replace(".exe", "")

    print(name)

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
    window = MainWindow()
    window.show()
    app.exec_()
    while running:
        window.show()
    

def programUpdate():
    #Function runs on a thread, constantly updates the number of seconds in the current project
    global running
    global prevWindow
    global currentWindow
    global currentProject
    global currentWindowTimer
    while running:
        if(not(currentProject == None) and not(currentProject == "")):
            prevWindow = currentWindow
            currentWindow = getActiveWindowType()
            getActiveWindow()
            if(not(currentWindow == prevWindow)):
                DB.updateProgram(currentProject, prevWindow, currentWindowTimer/60)
                currentWindowTimer = 0
                if(not DB.checkProgamInProject(currentWindow, currentProject)):
                    #Current program being used is not in the current project
                    #draw pop-up to add it
                    print("Would you like to add " + currentWindow + " to your " + currentProject + " project?")
            print(currentProject, currentWindow)
            time.sleep(1)
            currentWindowTimer += 1
            if(currentWindowTimer >= 60):
                DB.updateProgram(currentProject, currentWindow, 1)
                currentWindowTimer = 1
            

if(__name__ == "__main__"):

    main()
