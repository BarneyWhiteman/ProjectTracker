import Database as DB
import GUI
import Exclusion

import win32gui as w
import win32process


import threading
import sys
import time
import psutil

class Controller:

    def __init__(self):
        
        DB.setUpDatabase()
        DB.setUpTables()

        self.currentProject = DB.getActiveProjectName();    
        
        self.gui = GUI.createApp(self)

    def addProgramPopupClicked(button):
        print(button)
        if(button == "Yes"):
            print("Adding " + currentWindow + " to " + currentProject)
            DB.addProgram(currentWindow, currentProject)
            window.populateProgramTable()
        else:
            print("Excluding " + currentWindow + " from " + currentProject)
            DB.excludeProgram(currentWindow, currentProject)
            window.populateExcludedTable()

    @staticmethod
    def getProjects():
        return DB.getProjectNames()
    
    @staticmethod
    def getActiveProjectName():
        return DB.getActiveProjectName()

    @staticmethod
    def getActiveProjectIndex():
        index = 0
        try:
            index = DB.getProjectNames().index(DB.getActiveProjectName()) + 1
        except ValueError as e:
            print(e)
        return index
    
    def newProject(self):
        print("Make a new project")
    
    def exportFile(self):
        print("Export a project")
    
    def importFile(self):
        print("Import a project")
    
    def exitProgram(self):
        print("Exiting")
    
    def showLicense(self):
        print("Show license")


    def projectSelectionChange(i):
        print("Current selection: (", i, ")", Controller.getProjects()[i])



#Globals
running = True
prevWindow = ""
currentWindow = ""
currentProject = ""
currentWindowTimer = 0


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
                    showAddProgramPopup(currentWindow, currentProject)
            time.sleep(1)
            currentWindowTimer += 1
            if(currentWindowTimer >= 60):
                DB.updateProgram(currentProject, currentWindow, 1)
                currentWindowTimer = 1

def main():
    controller = Controller()

if(__name__ == "__main__"):
    main()