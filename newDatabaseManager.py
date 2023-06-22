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


@needsDatabaseConnection
def insertPerson(db: sqlite3.Cursor, name: str, srcAccountID:str = None, srcName: str = None, discordID:str = None, joinDate = datetime.datetime.utcnow().strftime("%Y-%m-%d")) -> None:
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

if __name__ == "__main__":
    insertPerson("alatreph", "8lp3qz4j", "alatreph", "836238555482816542")