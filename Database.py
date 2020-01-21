#----Database----#

#Imports
import os
import sqlite3
from sqlite3 import Error

#Database set up

DATABASE = "data/Projects.db"

PROJECT_SQL =   """CREATE TABLE IF NOT EXISTS Projects (
                    id Integer PRIMARY KEY NOT NULL,
                    name text NOT NULL,
                    active bit NOT NULL
                );"""

PROGRAM_SQL =   """CREATE TABLE IF NOT EXISTS Programs (
                    id Integer PRIMARY KEY NOT NULL,
                    name text NOT NULL,
                    mins Decimal,
                    projectID Integer NOT NULL,
                    FOREIGN KEY (projectID) REFERENCES Projects(id)
                );"""

EXCULDED_SQL =  """CREATE TABLE IF NOT EXISTS Excluded (
                    id Integer PRIMARY KEY NOT NULL,
                    name text NOT NULL,
                    projectID Integer NOT NULL,
                    FOREIGN KEY (projectID) REFERENCES Projects(id)
                )"""

def createConnection():
    """ create a database connection to a SQLite database """
    try:
        return sqlite3.connect(os.path.abspath(DATABASE))
    except Error as e:
        print(e)
    
    return None
 
def createTable(db, tableSQL):
    try:
        cursor = db.cursor()
        cursor.execute(tableSQL)
    except Error as e:
        print("table creation error: " + e)

def setUpDatabase():
    #Connect to DB (create if it doesn't exist)
    conn = createConnection()
    if(conn is not None):
        #create Project DB
        createTable(conn, PROJECT_SQL)
        #create Program DB
        createTable(conn, PROGRAM_SQL)
        #create Excluded DB
        createTable(conn, EXCULDED_SQL)
    return conn

def addProject(projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        try:
            sql = "INSERT INTO Projects(name, active) VALUES(?, 0)"
            cursor.execute("SELECT * FROM Projects WHERE name=?", (projectName, ))
            if(len(cursor.fetchall()) == 0):
                cursor.execute(sql, (projectName,))
            else:
                print("Project already exists")
            
        except Error as e:
            print("Project addition error: " + e)
        return cursor.lastrowid

def addProgram(programName, projectName):
    includeProgram(programName, projectName)
    db = createConnection()
    with db:
        cursor = db.cursor()
        try:
            sql = "INSERT INTO Programs(name, mins, projectID) VALUES(?, ?, ?)"

            cursor.execute("SELECT * FROM Programs WHERE name=? AND projectID=?", (programName, getProjectID(projectName)))
            if(len(cursor.fetchall()) == 0):
                cursor.execute(sql, (programName, 0, getProjectID(projectName)))
            else:
                print("Program already exists in Project")

        except Error as e:
            print("Program addition error: " + e)
        return cursor.lastrowid

def removeProgram(programName, projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        try:
            sql = "DELETE FROM Programs WHERE name=? AND projectID=?"

            cursor.execute(sql, (programName, getProjectID(projectName)))
            
        except Error as e:
            print("Program deletion error: " + e)
        return cursor.lastrowid

def excludeProgram(programName, projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        try:
            sql = "INSERT INTO Excluded(name, projectID) VALUES(?, ?)"

            cursor.execute("SELECT * FROM Excluded WHERE name=? AND projectID=?", (programName, getProjectID(projectName)))
            if(len(cursor.fetchall()) == 0):
                cursor.execute(sql, (programName, getProjectID(projectName)))
            else:
                print("Program already exists in Excluded")

        except Error as e:
            print(e)
        return cursor.lastrowid

def includeProgram(programName, projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        try:
            sql = "DELETE FROM Excluded WHERE name=? AND projectID=?"

            cursor.execute("SELECT * FROM Excluded WHERE name=? AND projectID=?", (programName, getProjectID(projectName)))
            if(len(cursor.fetchall()) != 0):
                cursor.execute(sql, (programName, getProjectID(projectName)))
            else:
                print("Program does not exist in Excluded")

        except Error as e:
            print("Program inclusion error: " + e)

def changeActiveProject(projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        cursor.execute("UPDATE Projects SET active=0 WHERE active=1")
        cursor.execute("UPDATE Projects SET active=1 WHERE name=?", (projectName,))

def getActiveProjectName():
    db = createConnection()
    with db:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM Projects WHERE active=1")
        row = cursor.fetchone()
        if(row == None):
            return None
        else:
            return row[0]

def getProjectID(projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM Projects WHERE name=?", (projectName,))

        row = cursor.fetchone()
        if(row == None):
            return row
        return row[0]

def updateProgram(projectName, programName, mins):
    db = createConnection()
    with db:
        cursor = db.cursor()
        
        sql = "SELECT id FROM Programs WHERE name = ? AND projectID = ?"
        cursor.execute(sql, (programName, getProjectID(projectName)))
        row = cursor.fetchone()
        if(row != None):
            sql = "UPDATE Programs SET mins = mins + ? WHERE name = ? AND projectID = ?"
            cursor.execute(sql, (mins, programName, getProjectID(projectName)))

def setUpTables():
    addProject("ProjectTracker")
    addProgram("Visual Studio Code", "ProjectTracker")
    
    addProject("Unexpected Orcs")
    addProgram("IntelliJ IDEA", "Unexpected Orcs")

def getProjectNames():
    db = createConnection()
    with db:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM Projects")
        return tupleToArray(cursor.fetchall())

def getProgramNames(projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM Programs WHERE projectID=?", (getProjectID(projectName), ))
        return tupleToArray(cursor.fetchall())

def getProgramMinutes(projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        cursor.execute("SELECT mins FROM Programs WHERE projectID=?", (getProjectID(projectName), ))
        return tupleToArray(cursor.fetchall())

def checkProgamInProject(programName, projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM Programs WHERE name=? AND projectID=?", (programName, getProjectID(projectName)))
        row = cursor.fetchall()
        return len(row) > 0 

def getExcludedList(projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM Excluded WHERE projectID=?", (getProjectID(projectName),))
        return tupleToArray(cursor.fetchall())

def isExcluded(programName, projectName):
    return programName in getExcludedList(projectName)

def createExportData(projectName):
    '''Creates a CSV string of the data for the Project Name to be exported as a file

    projectName -> Name of the project to create export data of

    return -> CSV string descrining data
    '''
    db = createConnection()
    with db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Programs WHERE projectID=?", (getProjectID(projectName),))
        print(cursor.fetchall)


def tupleToArray(tup):
    arr = []
    for t in tup:
        arr.append(t[0])
    return arr