--INSERT INTO user (first_name, surname, username) VALUES ('Mike', 'Lemon', 'mlemon');
--INSERT INTO user (first_name, surname, username) VALUES ('Dave', 'Lemon', 'dlemon');
--INSERT INTO user (first_name, surname, username) VALUES ('Ian', 'Bisson', 'ibisson');
--INSERT INTO user (first_name, surname, username) VALUES ('Simon', 'Teed', 'steed');
--
--INSERT INTO competitions (competition_name, rounds, season) VALUES ('DUMMY_WinterLeague', 18, '2019/20');
--
--INSERT INTO team (season, team_name, team_size) VALUES ('2019/20', 'Dummy_TEAM_1', 2);
--INSERT INTO team (season, team_name, team_size) VALUES ('2019/20', 'Dummy_TEAM_2', 2);
--
--
--INSERT INTO compTeam(competition_id, team_id) VALUES (1, 1);
--INSERT INTO compTeam(competition_id, team_id) VALUES (2, 2);
--
--INSERT INTO teamMembers (team_id, user_id) VALUES (1, 1),(1, 2);
--INSERT INTO teamMembers (team_id, user_id) VALUES (2, 3),(2, 4);
--
--INSERT INTO scores (competition_id, user_id, round, estimated, result, completed) VALUES (1, 1, 1, 100, 100, '2019-10-22'), (1, 1, 2, 99, 99, '2019-10-22')
--
--INSERT INTO user (first_name, surname, username) VALUES ('Trevor', 'Teed', 'tteed'), ('Steve', 'Pearcey', 'spearcey'), ('Tony', 'Crownhurst', 'tcrownhurst'), ('Rob', 'Sampson', 'rsampson'), ('Jonathon', 'Pratt', 'jpratt'), ('Margery', 'Teed', 'mteed')
--INSERT INTO user (first_name, surname, username) VALUES ('Mike', 'Lemon', 'mlemon'), ('Dave', 'Lemon', 'dlemon'), ('Ian', 'Bisson', 'ibisson'), ('Simon', 'Teed', 'steed')

--======================================
-- UPDATE 001 :: 05 Dec 2019 - Add new table and insert Data for competition 1
--======================================
--drop table if exists rounds;
--create table rounds (
--  id integer primary key autoincrement,
--  comp_id integer not null,
--  num integer not null,
--  due_date date NULL
--);

--insert into rounds (comp_id, num, due_date)
--values
--(1,	1,	'2019-09-23'),
--(1,	2,	'2019-09-30'),
--(1,	3,	'2019-10-07'),
--(1,	4,	'2019-10-14'),
--(1,	5,	'2019-10-21'),
--(1,	6,	'2019-10-28'),
--(1,	7,	'2019-11-4'),
--(1,	8,	'2019-11-11'),
--(1,	9,	'2019-11-18'),
--(1,	10,	'2019-12-2'),
--(1,	11,	'2019-12-9'),
--(1,	12,	'2020-01-13'),
--(1,	13,	'2020-01-20'),
--(1,	14,	'2020-01-27'),
--(1,	15,	'2020-02-03'),
--(1,	16,	'2020-02-10'),
--(1,	17,	'2020-02-17'),
--(1,	18,	'2020-02-24')
--======================================
-- END OF UPDATE 001
--======================================

--======================================
-- START OF UPDATE 002
--======================================

--ALTER TABLE scores
--ADD compTeam_id INTEGER;
--
--UPDATE scores set compTeam_id=1 where user_id in (3, 2, 1, 4, 5);
--UPDATE scores set compTeam_id=2 where user_id in (7, 8, 10, 11, 12, 9);

--======================================
-- END OF UPDATE 002
--======================================

--======================================
-- START OF UPDATE 003
--======================================
-- ALTER TABLE teamMembers ADD submitted_avg DECIMAL;
--======================================
-- START OF UPDATE 004
--======================================
CREATE TABLE booking (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  range TEXT NOT NULL,
  title TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  allDay BOOLEAN NOT NULL,
  armory_access BOOLEAN NOT NULL
);

DROP TABLE IF EXISTS ranges ;
CREATE TABLE ranges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    distance TEXT NOT NULL,
    firing_points INTEGER NULL,
    active BOOLEAN NOT NUll
)