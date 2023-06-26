import sqlite3
import os
import datetime
import functools
from typing import Callable, Any, ParamSpec, TypeVar
dirPath = os.path.dirname(os.path.realpath(__file__))
databaseFile = dirPath+"/tol_test.db"

P = ParamSpec("P")
T = TypeVar("T")

def needsDatabaseConnection(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator that provides a function with a connection to the database

    Arguments:
        func - The function, first argument should take a sqlite3.Cursor object
    
    Returns:
        The wrapped function.
    
    """
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(databaseFile)
        db = conn.cursor()
        result = func(db, *args, **kwargs)
        conn.commit()
        conn.close()
        return result
    
    return wrapper


def getOutputDict(keys: list[Any], rows: list[list[Any]]) -> list[dict[Any, Any]]:
    """
    Converts the output of a db.fetchall() to a list of dictionaries by matching the values in each row with a provided list of keys

        i.e. rows = [[column1Value, column2Value], [column1Value, column2Value]], keys = ["Column 1 Name", "Column 2 Name"]

        Becomes [{"Column 1 Name": column1Value, "Column 2 Name": column2Value}, {"Column 1 Name": column1Value, "Column 2 Name": column2Value}]
    
    Arguments:
        keys - A list of keys, with the order of the keys corresponding to the order the columns were selected in

    Returns:
        A list of dicts 
    """

    output = []
    for row in rows:
        rowDict = {}
        for index, item in enumerate(row):
            rowDict[keys[index]] = item

        output.append(rowDict)
        
    return output


@needsDatabaseConnection
def insertPerson(db: sqlite3.Cursor, name: str, srcAccountID:str = None, srcName: str = None, discordID: str = None, joinDate: str = datetime.datetime.utcnow().strftime("%Y-%m-%d")) -> None:
    """
    Inserts a new person into the database

    Arguments:
        name - the person's chosen name

        srcAccountID - the person's speedrun.com account

        srcName - the person's speedrun.com name

        discordID - the person's discord ID

        joinDate - the date the person joined. Defaults to current UTC date.
    """
    db.execute("""
        INSERT INTO Persons (name, srcAccountID, srcName, discordID, tolJoinDate)
        VALUES (?, ?, ?, ?, ?)
    """, (name, srcAccountID, srcName, discordID, joinDate))

@needsDatabaseConnection
def insertRun(db: sqlite3.Cursor, category: str, time: float, date: str, runner: int, srcRunID: str = None) -> None:
    """
    Inserts a run into the database

    Arguments:
        category - the category of the run

        time - the duration of the run

        date - the date the run was submitted

        runner - the ID of the person responsible for playing the run

        srcRunID - the ID of the run on speedrun.com
    """
    db.execute("""
        INSERT INTO Runs (category, time, date, runner, srcRunID)
        VALUES (?, ?, ?, ?, ?)
    """, (category, time, date, runner, srcRunID))

@needsDatabaseConnection
def updateSetup(db: sqlite3.Cursor, person: int, setupElement: str, setupValue: str) -> None:
    """
    Inserts, or replaces, a given setup element in a person's setup

    Arguments:
        person - the id of the person

        setupElement - the element of their setup to change

        setupValue - the new value
    """
    db.execute("""
        INSERT OR REPLACE INTO Setup (person, element, value)
        VALUES (?, ?, ?)
    """, (person, setupElement, setupValue))

@needsDatabaseConnection
def insertILRun(db: sqlite3.Cursor, map: str, category: str, time: float, date: str, runner: int, srcRunID: str = None) -> int:
    """
    Inserts an individual level run into the database

    Arguments:
        map - the filename (excluding .bsp) of the map the run is of

        category - the category the run is of

        time - the duration of the run

        date - the date the run was submitted

        runner - the id of the person who performed the run

        srcRunID - the speedrun.com id of the run

    Returns:
        runID - The ID of the IL run, as it appears in the database
    """
    db.execute("""
        INSERT INTO IndividualLevelRuns (map, category, time, date, runner, srcRunID)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (map, category, time, date, runner, srcRunID))
    runID = db.lastrowid
    return runID


@needsDatabaseConnection
def checkDiscordAccountRegistered(db: sqlite3.Cursor, discordID: str) -> bool:
    """
    Checks if a discord account is already attached to a person in the database

    Arguments:
        discordID - discord account ID to test

    Returns:
        True if the account is already attached to a person, False otherwise
    """
    db.execute("""
        SELECT COUNT(discordID)
        FROM Persons
        WHERE discordID = ?
    """, (discordID,))
    return db.fetchone()[0] > 0


@needsDatabaseConnection
def getSRCAccountIDFromDiscordID(db: sqlite3.Cursor, discordID: str) -> str | None:
    """
    Find the speedrun.com account id of a person, given their discord id

    Arguments:
        discordID - the discord id of the person

    Returns:
        result - The speedrun.com account id if it is found in the database, None otherwise
    """
    db.execute("""
        SELECT srcAccountID
        FROM Persons
        WHERE discordID = ?
    """, (discordID,))
    result = db.fetchone()
    return result[0] if result else result


@needsDatabaseConnection
def checkSRCAccountIDAlreadyTaken(db: sqlite3.Cursor, srcAccountID: str) -> bool:
    """
    Checks if there is already a discord account linked to the Person with the provided srcAccountID

    Arguments:
        srcAccountID - the alphanumeric speedrun.com account ID to check

    Returns:
        True if there is already a discord account linked to that speedrun.com account, False if there isn't
    """
    db.execute("""
        SELECT COUNT(discordID)
        FROM Persons
        WHERE srcAccountID = ?
    """, (srcAccountID,))
    return db.fetchone()[0] > 0

@needsDatabaseConnection
def moveDiscordIDToPerson(db: sqlite3.Cursor, discordID: str, targetPerson: int) -> None:
    """
    Move a discord ID from one person to another. Removes the id from whatever person it was already attached to, if any.
    
    Arguments:
        discordID - the discord id to move

        targetPerson - the id of the person to attach the discord ID to
    """
    db.execute("""
    UPDATE Persons
    SET discordID = NULL
    WHERE discordID = ?
    """, (discordID,))

    db.execute("""
    UPDATE Persons
    SET discordID = ?
    WHERE ID = ?
    """, (discordID, targetPerson,))

@needsDatabaseConnection
def getPersonFromDiscordID(db: sqlite3.Cursor, discordID: str) -> int | None:
    """
    Find the ID of a person using their discord ID

    Arguments:
        discordID - the discord id of the person

    Returns:
        Integer ID of the person if a person with the specified discord ID is found, None otherwise
    """
    db.execute("""
    SELECT ID
    FROM Persons
    WHERE discordID = ?
    """, (discordID))
    result = db.fetchone()
    return result[0] if result else result

@needsDatabaseConnection
def getPersonFromSRCAccountID(db: sqlite3.Cursor, srcAccountID: str) -> int | None:
    """
    Find the ID of a person using their src account ID

    Arguments:
        srcAccountID - the speedrun.com account id of the person

    Returns:
        Integer ID of the person if a person with the specified srcAccountID is found, None otherwise
    """
    db.execute("""
    SELECT ID
    FROM Persons
    WHERE srcAccountID = ?
    """, (srcAccountID))
    result = db.fetchone()
    return result[0] if result else result

@needsDatabaseConnection
def getSRCAccountIDFromPerson(db: sqlite3.Cursor, personID: str) -> str | None:
    """
    Find the src account id of a person

    Arguments:
        personID - the id of the person

    Returns:
        Alphanumeric speedrun.com account ID of the person if they have one, None otherwise
    """
    db.execute("""
    SELECT srcAccountID
    FROM Persons
    WHERE ID = ?
    """, (personID))
    result = db.fetchone()
    return result[0] if result else result

@needsDatabaseConnection
def getPlayerRuns(db: sqlite3.Cursor, personID: str) -> list[dict[str, (int|str|float)]]:
    """
    Get all of the runs belonging to a player

    Arguments:
        personID - the id of the person whose runs you're trying to find

    Returns:
        A list of runs, formatted like [{"id": 1, "category": "glitchless", "time": 931.500, "date": "2023-06-04", "srcRunID": "7c26g4f"}]
    """
    db.execute("""
    SELECT ID, category, time, date, srcRunID
    FROM Runs
    WHERE runner = ?
    ORDER BY category, time
    """)
    return getOutputDict(["id", "category", "time", "data", "srcRunID"], db.fetchall())



@needsDatabaseConnection
def getCategories(db: sqlite3.Cursor, includeExtensions: bool = False) -> list[dict[str, (str|bool)]]:
    """
    Get all the tracked categories.

    Arguments:
        includeExtensions - Whether to include category extensions

    Returns:
        The details of all the categories, formatted as [{"id": "glitchless", "name": "Glitchless", "shortname": "gless", "extension": False}]
    """
    command = """
    SELECT ID, name, shortname, extension
    FROM Categories

    """
    if not includeExtensions:
        command += "WHERE extension = 0"

    db.execute(command)
    categories = []
    for row in db.fetchall():
        categories.append({
            "id": row[0],
            "name": row[1],
            "shortname": row[2],
            "extension": (row[3]==1) # converts 1/0 to true/false
        })

    return categories

@needsDatabaseConnection
def getPlayerPBs(db: sqlite3.Cursor, personID: int) -> list[dict[str, (int|str|float)]]:
    """
    Get a player's personal bests in all categories
    Arguments:
        personID - the id of the player whose personal bests are to be fetched
    
    Returns:
        The same output as getPlayerRuns(), but with only a single run per category included
    """
    output = []
    seenCategories = []
    runs = getPlayerRuns(personID)
    for run in runs:
        # the output of getPlayerRuns is grouped by category (in alphabetical order) and then sorted by time
        # so by just taking the first run in the list for each category, we will get the fastest run for each
        if not run["category"] in seenCategories:
            output.append(run)
            seenCategories.append(run["category"])

    return output


@needsDatabaseConnection
def getPersonName(db: sqlite3.Cursor, personID: int) -> str | None:
    """
    Get the chosen name of a person

    Arguments:
        personID - the id of the person

    Returns:
        The name of the person
    """
    db.execute("""
        SELECT Name
        FROM Persons
        WHERE ID = ?
    """, (personID,))
    result = db.fetchone()
    return result[0] if result else result



if __name__ == "__main__":
    print(getPersonName(2))