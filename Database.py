#----Database----#

#Imports
import os
import sqlite3
from sqlite3 import Error

#Database set up

DATABASE = "data/Projects.db"

PROJECT_SQL =   """CREATE TABLE IF NOT EXISTS Projects (
                    id Integer PRIMARY KEY NOT NULL,
                    name text NOT NULL
                );"""

PROGRAM_SQL =   """CREATE TABLE IF NOT EXISTS Programs (
                    id Integer PRIMARY KEY NOT NULL,
                    name text NOT NULL,
                    mins Integer,
                    projectID Integer NOT NULL,
                    FOREIGN KEY (projectID) REFERENCES Projects(id)
                );"""

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
        print(e)

def setUpDatabase():
    #Connect to DB (create if it doesn't exist)
    conn = createConnection()
    if(conn is not None):
        #create Project DB
        createTable(conn, PROJECT_SQL)
        #create Program DB
        createTable(conn, PROGRAM_SQL)
    return conn

def addProject(db, projectName):
    try:
        sql = "INSERT INTO Projects(name) VALUES(?)"

        cursor = db.cursor()

        cursor.execute("SELECT * FROM Projects WHERE name=?", (projectName, ))
        if(len(cursor.fetchall()) == 0):
            cursor.execute(sql, (projectName,))
        else:
            print("Project already exists")
        
    except Error as e:
        print(e)
    return cursor.lastrowid

def addProgram(db, programName, projectName):
    try:
        sql = "INSERT INTO Programs(name, mins, projectID) VALUES(?, ?, ?)"

        cursor = db.cursor()

        cursor.execute("SELECT * FROM Programs WHERE name=? AND projectID=?", (programName, getProjectID(projectName)))
        if(len(cursor.fetchall()) == 0):
            cursor.execute(sql, (programName, 0, getProjectID(projectName)))
        else:
            print("Program already exists in Project")

    except Error as e:
        print(e)
    return cursor.lastrowid


def getProjectID(projectName):
    db = createConnection()
    with db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM Projects WHERE name=?", (projectName,))

        row = cursor.fetchone()
        return row[0]

def updateProgram(projectName, programName, mins):
    db = createConnection()
    with db:
        
        sql = "UPDATE Programs SET mins = mins + ? WHERE name = ? AND projectID = ?"

        cursor = db.cursor()
        cursor.execute(sql, (mins, programName, getProjectID(projectName)))

def setUpTables():
    db = setUpDatabase()
    with db:
        addProject(db, "ProjectTracker")
        addProgram(db, "VSCode", "ProjectTracker")

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

def tupleToArray(tup):
    arr = []
    for t in tup:
        arr.append(t[0])
    return arr