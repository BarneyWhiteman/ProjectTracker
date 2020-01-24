import tkinter as tk
from tkinter import *
import tkinter.ttk as ttk

def createApp(controller):
    root = Tk()
    app = MainWindow(root, controller)
    root.mainloop()
    return app


class MainWindow(ttk.Frame):
    def __init__(self, root, controller):
        ttk.Frame.__init__(self, root)

        self.root = root
        self.controller = controller

        self.createView()

    def createView(self):
        self.root.title("Project Tracker")
        self.root.geometry("720x480")
        self.pack(fill = BOTH, expand = 1)
        
        #menu
        menu = Menu(self.root)
        self.root.config(menu = menu)

        file = Menu(menu)
        file.add_command(label = "New", command = self.controller.newProject)
        file.add_command(label = "Export", command = self.controller.exportFile)
        file.add_command(label = "Import", command = self.controller.importFile)
        file.add_command(label = "Exit", command = self.controller.exitProgram)

        menu.add_cascade(label = "File", menu = file)

        help = Menu(menu)
        help.add_command(label = "License", command = self.controller.showLicense)

        menu.add_cascade(label = "Help", menu = help)

        #project select
        projectSelect = ProjectSelect(self)
        projectSelect.grid(row = 0, column = 0)
        #project tabs
        projectTabs = ProjectTabs(self)
        projectTabs.grid(row = 0, column = 1, columnspan = 4)

    @staticmethod
    def showAddProgramPopup(currentWindow, currentProject):
        title = "Add " + currentWindow + " to " + currentProject + "?"
        message = "Would you like to start tracking " + currentWindow + " in your \"" + currentProject + "\" project?"

    def closeEvent(self, event):
        msg = "Are you sure you want to exit Project Tracker?\n\n No projects can be tracked if you exit."


class ProjectSelect(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        Frame.__init__(self, parent)

        label = Label(self, text = "Current Project:")
        label.pack()

        select = ttk.Combobox(self, values = self.parent.controller.getProjects())
        select.pack()

class ProjectTabs(ttk.Frame):
    def __init__(self, parent):
        self.parent = parent
        Frame.__init__(self, parent)
        
        self.tabs = ttk.Notebook(self)

        self.overview = Frame(self.tabs)
        self.graphs = Frame(self.tabs)
        self.programs = Frame(self.tabs)

        self.tabs.add(self.overview, text = "Overview")
        self.tabs.add(self.graphs, text = "Graphs")
        self.tabs.add(self.programs, text = "Tabs")

        self.tabs.pack(fill = BOTH, expand = 1)