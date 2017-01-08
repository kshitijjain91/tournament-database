-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-------------------------------defining tournament database schema---------------

-- connect to the tournament database
\c tournament;

-- create players table
create table if not exists players (player_id serial,
player_name text);


-- create matches table
create table if not exists matches (match_id serial,
player1_id int,
player2_id int,
winner_id int,
loser_id int);



