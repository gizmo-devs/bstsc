INSERT INTO user (first_name, surname, username) VALUES ('Mike', 'Lemon', 'mlemon');
INSERT INTO user (first_name, surname, username) VALUES ('Dave', 'Lemon', 'dlemon');
INSERT INTO user (first_name, surname, username) VALUES ('Ian', 'Bisson', 'ibisson');
INSERT INTO user (first_name, surname, username) VALUES ('Simon', 'Teed', 'steed');

INSERT INTO competitions (competition_name, rounds, season) VALUES ('DUMMY_WinterLeague', 18, '2019/20');

INSERT INTO team (season, team_name, team_size) VALUES ('2019/20', 'Dummy_TEAM_1', 2);
INSERT INTO team (season, team_name, team_size) VALUES ('2019/20', 'Dummy_TEAM_2', 2);


INSERT INTO compTeam(competition_id, team_id) VALUES (1, 1);
INSERT INTO compTeam(competition_id, team_id) VALUES (2, 2);

INSERT INTO teamMembers (team_id, user_id) VALUES (1, 1),(1, 2);
INSERT INTO teamMembers (team_id, user_id) VALUES (2, 3),(2, 4);

INSERT INTO scores (competition_id, user_id, round, estimated, result, completed) VALUES (1, 1, 1, 100, 100, '2019-10-22'), (1, 1, 2, 99, 99, '2019-10-22')