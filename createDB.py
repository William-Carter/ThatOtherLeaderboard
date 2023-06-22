import sqlite3
import os
import depthFirstSearch
dirPath = os.path.dirname(os.path.realpath(__file__))
conn = sqlite3.connect(dirPath+"/tol_test.db")
cur = conn.cursor()


cur.execute("""
CREATE TABLE "Categories" (
	"ID"	TEXT NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"shortName"	TEXT NOT NULL,
	"extension"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("ID")
)
""")

cur.execute("""
CREATE TABLE "CategoryPropagation" (
	"BaseCategory"	TEXT NOT NULL,
	"ForeignCategory"	TEXT NOT NULL,
	"BasePropagatesToForeign"	INTEGER NOT NULL DEFAULT 0,
	FOREIGN KEY("ForeignCategory") REFERENCES "Categories"("ID"),
	FOREIGN KEY("BaseCategory") REFERENCES "Categories"("ID"),
	PRIMARY KEY("BaseCategory","ForeignCategory")
)	
""")

cur.execute("""
CREATE TABLE "Golds" (
	"Person"	INTEGER NOT NULL,
	"category"	TEXT NOT NULL,
	"map"	TEXT NOT NULL,
	"time"	REAL NOT NULL,
	"eligibleForComgold"	INTEGER NOT NULL DEFAULT 1,
	FOREIGN KEY("Person") REFERENCES "Persons"("ID"),
	FOREIGN KEY("category") REFERENCES "Categories"("ID"),
	FOREIGN KEY("map") REFERENCES "Maps"("name"),
	PRIMARY KEY("Person","category","map")
)
""")

cur.execute("""
	CREATE TABLE "IndividualLevelRuns" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"map"	TEXT NOT NULL,
	"category"	TEXT NOT NULL,
	"time"	REAL NOT NULL,
	"date"	TEXT,
	"runner"	INTEGER NOT NULL,
	"srcRunID"	TEXT,
	PRIMARY KEY("ID" AUTOINCREMENT)
)
""")

cur.execute("""
CREATE TABLE "Maps" (
	"name"	TEXT NOT NULL UNIQUE,
	"levelName"	TEXT NOT NULL UNIQUE,
	"vanilla"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("name")
)
""")

cur.execute("""
CREATE TABLE "Persons" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"trusted"	INTEGER NOT NULL DEFAULT 0,
	"name"	TEXT NOT NULL,
	"srcAccountID"	TEXT UNIQUE,
	"srcName"	TEXT,
	"discordID"	TEXT UNIQUE,
	"tolJoinDate"	TEXT,
	PRIMARY KEY("ID" AUTOINCREMENT)
)
""")

cur.execute("""
CREATE TABLE "Runs" (
	"ID"	INTEGER NOT NULL UNIQUE,
	"category"	TEXT NOT NULL,
	"time"	REAL NOT NULL,
	"date"	TEXT,
	"runner"	INTEGER NOT NULL,
	"srcRunID"	TEXT UNIQUE,
	PRIMARY KEY("ID" AUTOINCREMENT),
	FOREIGN KEY("runner") REFERENCES "Persons"("ID")
)
""")

cur.execute("""
CREATE TABLE "Setup" (
	"person"	INTEGER NOT NULL,
	"element"	TEXT NOT NULL,
	"value"	TEXT,
	PRIMARY KEY("person","element"),
	FOREIGN KEY("person") REFERENCES "Persons"("ID")
)
""")
# Table creation done, filling in constant values
# ------------------------------------------- #

categories = [
    {
        "id": "oob",
        "name": "Out of Bounds",
        "shortname": "OoB",
        "extension": 0
    },
    {
        "id": "inbounds",
        "name": "Inbounds",
        "shortname": "Inbounds",
        "extension": 0
	},
    {
        "id": "unrestricted",
        "name": "Inbounds No SLA Unrestricted",
        "shortname": "NoSLA Unr.",
        "extension": 0
	},
    {
        "id": "legacy",
        "name": "Inbounds No SLA Legacy",
        "shortname": "NoSLA Leg.",
        "extension": 0
	},
    {
        "id": "glitchless",
        "name": "Glitchless",
        "shortname": "Gless",
        "extension": 0
	}
]
for category in categories:
	cur.execute("""
	INSERT INTO Categories (ID, name, shortName, extension)
	VALUES (?, ?, ?, ?)
	""", (
		category["id"],
		category["name"],
		category["shortname"],
		category["extension"]
	))


propagations = {
	"glitchless": ["legacy"],
	"legacy": ["unrestricted"],
	"unrestricted": ["inbounds"],
	"inbounds": ["oob"],
	"oob": []
}

for baseCategory in categories:
	for foreignCategory in categories:
		if depthFirstSearch.search(propagations, baseCategory["id"], foreignCategory["id"]):
			value = 1
		else:
			value = 0
		cur.execute("""
		INSERT INTO CategoryPropagation (BaseCategory, ForeignCategory, BasePropagatesToForeign)
		VALUES (?, ?, ?)

		""", (baseCategory["id"], foreignCategory["id"], value))




maps = {
        "testchmb_a_00": "00/01",
        "testchmb_a_01": "02/03",
        "testchmb_a_02": "04/05",
        "testchmb_a_03": "06/07",
        "testchmb_a_04": "08",
        "testchmb_a_05": "09",
        "testchmb_a_06": "10",
        "testchmb_a_07": "11/12",
        "testchmb_a_08": "13",
        "testchmb_a_09": "14",
        "testchmb_a_10": "15",
        "testchmb_a_11": "16",
        "testchmb_a_13": "17",
        "testchmb_a_14": "18",
        "testchmb_a_15": "19",
        "escape_00": "e00",
        "escape_01": "e01",
        "escape_02": "e02",
        "testchmb_a_08_advanced": "a13",
        "testchmb_a_09_advanced": "a14",
        "testchmb_a_10_advanced": "a15",
        "testchmb_a_11_advanced": "a16",
        "testchmb_a_13_advanced": "a17",
        "testchmb_a_14_advanced": "a18"
    }


for name, levelName in maps.items():
	cur.execute("""
		INSERT INTO Maps (name, levelName, vanilla)
		VALUES (?, ?, ?)

		""", (name, levelName, 1))



conn.commit()