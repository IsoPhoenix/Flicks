BEGIN TRANSACTION;
DROP TABLE IF EXISTS "attributes";
CREATE TABLE IF NOT EXISTS "attributes" (
	"user_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"groups"	TEXT,
	"director"	TEXT,
	"genre"	TEXT,
	"year"	TEXT,
	"movies_seen"	TEXT,
	"movies_swiped"	TEXT
);
DROP TABLE IF EXISTS "users";
;
DROP TABLE IF EXISTS "groups";
CREATE TABLE IF NOT EXISTS "groups" (
	"group_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"code"	TEXT NOT NULL UNIQUE,
	"users"	TEXT
);
DROP TABLE IF EXISTS "title_basics";
CREATE TABLE IF NOT EXISTS "title_basics" (
	"title_id"	text,
	"title_type"	text,
	"primary_title"	text,
	"original_title"	text,
	"is_adult"	boolean,
	"start_year"	int,
	"end_year"	int,
	"runtime_minutes"	int,
	"genres"	text
);
DROP TABLE IF EXISTS "title_ratings";
CREATE TABLE IF NOT EXISTS "title_ratings" (
	"title_id"	text,
	"average_rating"	numeric,
	"num_votes"	int
);
COMMIT;
