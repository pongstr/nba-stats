from typing import Dict
from psycopg2 import extras
from flask import jsonify


def set_player_url(player: Dict[str, str]):
    player["player_slug"] = "/players/" + player["player_slug"]
    return player


def query_teams():
    return ("""
        SELECT * from team
        ORDER BY year_founded ASC
    """)


def query_team(team_name: str):
    return ("""
        SELECT * from team
            JOIN team_details on team.id = team_details.team_id
                WHERE LOWER(team.nickname) = '%s'
    """) % (team_name)


def query_team_roster(team_name: str):
    return ("""
        SELECT
            rosterstatus,
            team_name,
            display_first_last,
            position,
            player_slug,
            jersey
        FROM common_player_info
            WHERE LOWER(rosterstatus) = 'active'
            AND LOWER(team_name) = '%s'
            ORDER BY from_year ASC
    """) % (team_name)


def query_team_games(team_name: str, season: str):
    return ("""
        SELECT * from team
            JOIN game_summary on team.id = game_summary.home_team_id
            JOIN game on game_summary.game_id = game.game_id
                WHERE LOWER(team.nickname) = '%s'
                AND season = '%s'
    """) % (team_name, season)


def extract_columns(model: Dict[str, int]):
    items = list(model.keys())
    return sorted(items)


class Teams():
    def __init__(self, db):
        self.db = db

    def db_query(self, query: str):
        db = self.db.cursor(cursor_factory=extras.RealDictCursor)
        db.execute(query)
        return db

    def get_teams(self):
        teams_query = self.db_query(query_teams())
        teams = teams_query.fetchall()

        teams_query.close()
        self.db.close()

        return jsonify({"results": teams})

    def get_team_info(self, team_name: str):
        team_query = self.db_query(query_team(team_name))
        team = team_query.fetchall()

        team_query.close()

        if len(team) < 1:
            message = "The team you're looking for doesn't seem to exist"
            message += "Please check the name and try again."

            response = {
                "code": "Team not found",
                "message": message,
                "status_code": 404
            }

            return jsonify(response)

        team_roster = self.db_query(query_team_roster(team_name))
        roster = team_roster.fetchall()

        team_roster.close()
        self.db.close()

        return jsonify({
            **team[0],
            "roster": list(map(set_player_url, roster))
        })

    def get_team_games(self, team_name: str, season: int):
        if (team_name is None or season is None):
            message = "Please pass <team_name> or <season_year>"
            response = {
                "code": "One or both required parameters are missing",
                "message": message,
                "status_code": 400
            }
            return jsonify(response)

        games_list = self.db_query(query_team_games(team_name, str(season)))
        games = games_list.fetchall()

        games_list.close()
        self.db.close()

        columns = extract_columns(games[0]) if len(games) > 0 else []

        return jsonify({"columns": columns, "results": games})
