#----ProjectTracker----#

#Imports
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

import win32gui as w
import win32process

import Database as DB
import Exclusion

import threading
import sys
import time
import psutil

#Globals
running = True
prevWindow = ""
currentWindow = ""
currentProject = ""
currentWindowTimer = 0

trayIcon = None
window = None
app = None

#App
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(720, 480)
        self.setWindowTitle("Project Tracker")
        self.setWindowIcon(QIcon("./assets/icon.png"))
        layout = QGridLayout()

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
        
        layout.addWidget(self.projectSelect, 0, 0)

        #TABLE REFRESH BUTTON
        self.refresh = QPushButton("Refresh")
        self.refresh.pressed.connect(self.refreshGUI)

        layout.addWidget(self.refresh, 1, 0)

        #PROGRAM VIEW TABLE
        self.programTable = QTableWidget()
        self.populateProgramTable()

        layout.addWidget(QLabel("Currently Tracked Programs"), 0, 1)
        layout.addWidget(self.programTable, 1, 1)

        #REMOVE PROGRAM BUTTON
        self.removeProgramButton = QPushButton("Remove Program")
        self.removeProgramButton.pressed.connect(self.removeProgram)
        
        layout.addWidget(self.removeProgramButton, 2, 1)

        #EXCLUSION VIEW TABLE
        self.excludedTable = QTableWidget()
        self.populateExcludedTable()

        layout.addWidget(QLabel("Currently Excluded Programs"), 0, 2)
        layout.addWidget(self.excludedTable, 1, 2)

        #REMOVE EXCLUSION BUTTON
        self.removeExclusionButton = QPushButton("Remove Exclusion")
        self.removeExclusionButton.pressed.connect(self.removeExclusion)
        
        layout.addWidget(self.removeExclusionButton, 2, 2)

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
            self.populateExcludedTable()
    
    def refreshGUI(self):
        self.populateExcludedTable()
        self.populateProgramTable()

    def populateProgramTable(self):
        programs = DB.getProgramNames(DB.getActiveProjectName())
        mins = DB.getProgramMinutes(DB.getActiveProjectName())

        self.programTable.setRowCount(len(programs))
        self.programTable.setColumnCount(2)

        for i in range(len(programs)):
            self.programTable.setItem(i, 0, QTableWidgetItem(programs[i]))
            self.programTable.setItem(i, 1, QTableWidgetItem(str(mins[i])))

    def populateExcludedTable(self):
        programs = DB.getExcludedList(DB.getActiveProjectName())

        self.excludedTable.setRowCount(len(programs))
        self.excludedTable.setColumnCount(1)

        for i in range(len(programs)):
            self.excludedTable.setItem(i, 0, QTableWidgetItem(programs[i]))

    def removeExclusion(self):
        row = self.excludedTable.currentRow()
        print(row)

        program = self.excludedTable.item(row, 0).text()

        print(program)
        DB.includeProgram(program, currentProject)

        self.refreshGUI()
    
    def removeProgram(self):
        row = self.programTable.currentRow()
        program = self.programTable.item(row, 0).text()

        msg = "Are you sure you want to stop tracking " + program + "\n\n This will remove all data associated with this program."
        reply = QMessageBox.question(self, 'Are you sure?', msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            DB.removeProgram(program, currentProject)
            self.refreshGUI()

    def closeEvent(self, event):
        msg = "Are you sure you want to exit Project Tracker?\n\n No projects can be tracked if you continue."
        reply = QMessageBox.question(self, 'Are you sure?', msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            #sys.exit()
            global running
            running = False
        else:
            event.ignore()

#Database Setup
DB.setUpDatabase()
DB.setUpTables()



def initSystemTray(app):
    global trayIcon
    trayIcon = QSystemTrayIcon(QIcon("./assets/icon.png"), app)
    trayIcon.messageClicked.connect(trayMessageClicked)
    trayIcon.show()

def getActiveWindowName():
    #Gets and returns the name of the currently active window
    return w.GetWindowText(w.GetForegroundWindow())

def getActiveWindowType():
    #Clips the active window name into a usable program name
    return getWindowType(getActiveWindowName())

def getWindowType(name):
    #Clips the active window name into a usable program name
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
    global trayIcon
    global window
    global app
    global currentProject

    currentProject = DB.getActiveProjectName()

    if(currentProject != None):
        print("Current Project: " + currentProject)

    #print("Database:")
    #for project in DB.getProjectNames():
    #    print("Project: " + project)
    #    for program in DB.getProgramNames(project):
    #        print("\tProgram: " + program)

    pUpdate = threading.Thread(name="programUpdate", target=programUpdate)
    pUpdate.start()

    app = QApplication([])
    window = MainWindow()
    window.show()

    initSystemTray(app)
    
    app.exec_()


    while running:
        window.show()

def displayNotification(title, message):
    global trayIcon
    trayIcon.showMessage(title, message, QIcon("./assets/icon.png"))

def trayMessageClicked():
    print("Adding " + currentWindow + " to " + currentProject)
    DB.addProgram(currentWindow, currentProject)
    window.populateProgramTable()

def programUpdate():
    #Function runs on a thread, constantly updates the number of seconds in the current project
    global running
    global prevWindow
    global currentWindow
    global currentProject
    global currentWindowTimer

    while running:
        if(currentProject != None and currentProject != ""):
            prevWindow = currentWindow
            currentWindow = getActiveWindowType()
            #getActiveWindow()
            if(not(currentWindow == prevWindow)):
                DB.updateProgram(currentProject, prevWindow, currentWindowTimer/60)
                currentWindowTimer = 0
                if(not DB.checkProgamInProject(currentWindow, currentProject) and currentWindow not in Exclusion.excludedPrograms and not DB.isExcluded(currentWindow, currentProject)):
                    #Current program being used is not in the current project
                    #draw pop-up to add it
                    DB.excludeProgram(currentWindow, currentProject)
                    displayNotification("Add " + currentWindow + " to " + currentProject + "?", "Would you like to start tracking " + currentWindow + " in your \"" + currentProject + "\" project?")
            print(currentProject, currentWindow)
            time.sleep(1)
            currentWindowTimer += 1
            if(currentWindowTimer >= 60):
                DB.updateProgram(currentProject, currentWindow, 1)
                currentWindowTimer = 1
            

if(__name__ == "__main__"):

    main()
