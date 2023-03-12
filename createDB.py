import sqlite3
import os
dirPath = os.path.dirname(os.path.realpath(__file__))
conn = sqlite3.connect(dirPath+"/tol.db")
cur = conn.cursor()


cur.execute("""
CREATE TABLE tolAccounts(
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    discordID TEXT UNIQUE,
    srcomID TEXT UNIQUE
    )
""")

cur.execute("""
CREATE TABLE srcomAccounts(
    ID TEXT PRIMARY KEY,
    Name TEXT NOT NULL
    )
""")

cur.execute("""
CREATE TABLE runs(
    ID INTEGER PRIMARY KEY,
    category TEXT NOT NULL,
    time REAL NOT NULL,
    date TEXT NOT NULL,
    tolAccount INT,
    srcomAccount TEXT,
    srcomID TEXT UNIQUE,
    FOREIGN KEY (tolAccount) REFERENCES tolAccounts(ID)
    FOREIGN KEY (srcomAccount) REFERENCES srcomAccounts(ID)
)
""")

cur.execute("""
CREATE TABLE "categoryHierarchy" (
	"categoryName"	TEXT,
	"hierarchy"	INTEGER NOT NULL,
	PRIMARY KEY("categoryName")
)  
)
""")

categoryHierarchy = {"oob": 1, "inbounds": 2, "unrestricted": 3, "legacy": 4, "glitchless": 5}
for item in categoryHierarchy.keys():
    cur.execute("""
    INSERT INTO categoryHierarchy VALUES (?, ?)
    """, (item, categoryHierarchy[item]))



conn.commit()