#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("delete from matches;")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE from players;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT player_id, count(*) as num FROM players GROUP BY player_id;")
    num_players = len(c.fetchall())
    conn.close()
    return num_players




def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players (player_name) VALUES (%s)", (name, ))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    c.execute('''
        create or replace view wins as select players.player_id, players.player_name, count(matches.winner_id) as num_wins from players left join matches
        on players.player_id = matches.winner_id
        group by players.player_id, players.player_name order by count(matches.winner_id) desc;
        ''')

    # counting number of wins
    #select players.player_id, players.player_name, count(matches.winner_id) as num_wins from players left join matches
    #on players.player_id = matches.winner_id group by players.player_id, players.player_name order by count(matches.winner_id) desc;


    # player 1 matches p1
    c.execute('''
        create or replace view p1 as select players.player_id, players.player_name, count(matches.player1_id) as num_p1 from players left join matches
    on players.player_id = matches.player1_id
    group by players.player_id, players.player_name
    order by count(matches.player1_id) desc;
        ''')

    # player 2 matches p2
    c.execute('''
        create or replace view p2 as select players.player_id, players.player_name, count(matches.player2_id) as num_p2 from players left join matches
    on players.player_id = matches.player2_id
    group by players.player_id, players.player_name
    order by count(matches.player2_id) desc;
    ''')

    # merge p1 and p2
    c.execute('''
        create or replace view p1p2 as select p1.player_id, p1.player_name, p1.num_p1, p2.num_p2
        from p1 join p2
        on p1.player_id = p2.player_id''')


    # total matches
    c.execute('''
        create or replace view num_matches as select player_id, sum(num_p1 + num_p2) as num_matches from p1p2 group by player_id order by sum(num_p1 + num_p2) desc;
        ''')

    # final table to be returned
    c.execute('''
        select wins.player_id, player_name, num_wins, num_matches
        from wins join num_matches on wins.player_id = num_matches.player_id
        order by wins.num_wins desc;''')

    standings = c.fetchall()
    conn.commit()
    conn.close()
    return standings





def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    c.execute("insert into matches (player1_id, player2_id, winner_id, loser_id) values ({0}, {1}, {2}, {3})".format(winner, loser, winner, loser))
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    c = conn.cursor()
    c.execute('''
        select wins.player_id, player_name, num_wins, num_matches
        from wins join num_matches on wins.player_id = num_matches.player_id
        order by wins.num_wins desc;''')
    standings = c.fetchall()
    next_rounds = []
    p = 0
    while p in range(len(standings)):
        if p+2 >= len(standings):
            next_rounds.append((standings[p][0], standings[p][1], standings[p+1][0], standings[p+1][1]))
            break
        next_rounds.append((standings[p][0], standings[p][1], standings[p+2][0], standings[p+2][1]))
        next_rounds.append((standings[p+1][0], standings[p+1][1], standings[p+3][0], standings[p+3][1]))
        p += 4
    conn.commit()
    conn.close()
    return next_rounds







