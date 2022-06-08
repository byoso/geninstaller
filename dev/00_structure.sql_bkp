BEGIN TRANSACTION;
CREATE TABLE "application" (
	"id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"exec"	TEXT,
    "comment" TEXT,
    "terminal" TEXT,
    "icon" TEXT,
    "categories" TEXT,
    "applications_files" TEXT,
    "applications" TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE INDEX index_application
ON application ( id COLLATE NOCASE );
COMMIT;
