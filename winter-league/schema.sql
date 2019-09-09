-- Clear all tables
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS team;
DROP TABLE IF EXISTS teamMembers;
DROP TABLE IF EXISTS competitions;
DROP TABLE IF EXISTS compTeam;
DROP TABLE IF EXISTS scores;

-- Recreate the Tables
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  surname TEXT NOT NULL,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT NOT NULL,
    team_size INTEGER NULL,
    season TEXT NOT NULL
);

CREATE TABLE teamMembers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL
);

CREATE TABLE competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competion_name TEXT NOT NULL,
    season TEXT NULL,
    rounds INTEGER NULL,
    round1_due DATE NULL,
    round2_due DATE NULL,
    round3_due DATE NULL,
    round4_due DATE NULL,
    round5_due DATE NULL,
    round6_due DATE NULL,
    round7_due DATE NULL,
    round8_due DATE NULL,
    round9_due DATE NULL,
    round10_due DATE NULL,
    round11_due DATE NULL,
    round12_due DATE NULL,
    round13_due DATE NULL,
    round14_due DATE NULL,
    round15_due DATE NULL,
    round16_due DATE NULL,
    round17_due DATE NULL,
    round18_due DATE NULL
);

CREATE TABLE compTeam (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NULL,
    competion_id INTEGER NULL
);

CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competion_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    round INTEGER NOT NULL,
    estimated INTEGER NULL,
    result INTEGER NULL,
    completed DATE NOT NULL
);