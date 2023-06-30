import sqlite3
import os
import datetime
from typing import Callable, Any, ParamSpec, TypeVar
dirPath = os.path.dirname(os.path.realpath(__file__))
databaseFile = dirPath+"/tol_cache.db"

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
def cacheLeaderboard(db: sqlite3.Cursor, category: str, leaderboard: list[int|str|float]) -> None:
    """
    Store the position of every run on the leaderboard in the cache

    Arguments:
        category - The ID of the category for which you want to cache the leaderboard

        leaderboard - the output of databaseManager.generateLeaderboard()
    """
    
    # First delete all entries for this category's leaderboard to prevent accidental placement of obsoleted runs
    db.execute("""
    DELETE FROM LeaderboardPlacements
    WHERE category = ?
    """, (category,))

    newValues = [(run["place"], run["id"], category) for run in leaderboard]

    # Insert the new leaderboard's placements
    db.executemany("""
    INSERT INTO LeaderboardPlacements (placement, runID, category)
    VALUES (?, ?, ?)
    """, newValues)

@needsDatabaseConnection
def getLeaderboardPlacement(db: sqlite3.Cursor, runID: int, category: str) -> int:
    """
    Fetch the leaderboard placement of a given run for a given category

    Arguments:
        runID - the id of the run

        category - the category to check

    Returns:
        The integer placement
    """
    db.execute("""
        SELECT placement
        FROM LeaderboardPlacements
        WHERE (runID = ? AND category = ?)
    """, (runID, category))
    result = db.fetchone()
    return result[0] if result else None
