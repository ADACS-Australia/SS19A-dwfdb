CREATE TABLE dwf (
	"ID"	INTEGER NOT NULL,
	"field"	TEXT NOT NULL,
	"ccd"	INTEGER NOT NULL,
	"mary_run"	INTEGER NOT NULL,
	"date"	INTEGER NOT NULL,
	"cand_num"	INTEGER NOT NULL,
	"mag"	REAL NOT NULL,
	"emag"	REAL NOT NULL,
	"mjd"	REAL NOT NULL,
	"RA"	REAL NOT NULL,
	"DEC"	REAL NOT NULL,
	"maryID"	TEXT NOT NULL UNIQUE,
	"sci_path"	TEXT NOT NULL UNIQUE,
	"sub_path"	TEXT NOT NULL UNIQUE,
	"temp_path"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("maryID")
);

CREATE TABLE post (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "author" TEXT,
  "created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "maryID" TEXT NOT NULL,
  "body" TEXT NOT NULL
  FOREIGN KEY("maryID") REFERENCES "dwf"("maryID")
);

CREATE TABLE testdb (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "author" TEXT,
  "created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "ra" REAL NOT NULL,
  "dec" REAL NOT NULL,
  "dateplusone" INTEGER,
  "path" TEXT NOT NULL
);