#----ProjectTracker----#

#Imports
import PyQt5
from PyQt5.QtWidgets import *

import Database as DB


#App Setup
app = QApplication([])

window = QWidget()
window.resize(720, 480)
window.setWindowTitle("Project Tracker")
layout = QVBoxLayout()
layout.addWidget(QPushButton('Top'))
layout.addWidget(QPushButton('Bottom'))
window.setLayout(layout)
window.show()


#Database Setup
DB.setUpDatabase()
DB.setUpTables()

def main():
    print("Database:")
    for project in DB.getProjectNames():
        print("Project: " + project)
        for program in DB.getProgramNames(project):
            print("\tProgram: " + program)

    return

if(__name__ == "__main__"):
    main()
    app.exec_()