import math
import os
from typing import Dict, Union

from flask import jsonify, request
from psycopg2 import extras

from modules.teams_query import (
    GetTeamArgs,
    get_conference,
    get_team_query,
    get_teams_count,
    get_teams_query,
    team_args,
)


def set_player_url(player: Dict[str, str]):
    player["player_slug"] = "/players/" + player["player_slug"]
    return player


def query_teams():
    return """
        SELECT * from team
        ORDER BY year_founded ASC
    """


def query_team(team_name: str):
    return (
        (
            """
        SELECT * from team
            JOIN team_details on team.id = team_details.team_id
                WHERE LOWER(team.nickname) = '%s'
    """
        )
        % (team_name)
    )


def query_team_roster(team_name: str):
    return (
        (
            """
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
    """
        )
        % (team_name)
    )


def query_team_games(team_name: str, season: str):
    return (
        (
            """
        SELECT * from team
            JOIN game_summary on team.id = game_summary.home_team_id
            JOIN game on game_summary.game_id = game.game_id
                WHERE LOWER(team.nickname) = '%s'
                AND season = '%s'
    """
        )
        % (team_name, season)
    )


def extract_columns(model: Dict[str, int]):
    items = list(model.keys())
    return sorted(items)


class Teams:
    def __init__(self, db):
        self.db = db

    def db_query(self, query: str):
        db = self.db.cursor(cursor_factory=extras.RealDictCursor)
        db.execute(query)
        return db

    def error_handler(self, code: int, msg: str):
        return jsonify({"status": str(code), "message": msg}), code

    def set_team_url(self, team):
        p = request.environ["HTTP_X_FORWARDED_SCHEME"]
        h = request.environ["HTTP_HOST"]
        team["url"] = f"{p}://{h}/teams/{team["nickname"].lower()}"
        return team

    def validate(self, params) -> Union[GetTeamArgs, Exception]:
        allowed = ["page", "count", "sort_field", "sort_order"]

        def validate_num():
            return

        if len(params) == 0:
            return team_args

        output = params.copy()

        try:

            for key, value in params.items():
                if key not in allowed:
                    return {**team_args, **output}

                if key == "page" or key == "count":
                    print("isdigit", value.isdigit())

                    if not value.isdigit():
                        msg = f"{key} value must be a number."
                        return ValueError(msg)
                    output.update({key: int(value)})

                if key == "sort_field" or key == "sort_order":
                    print(key, value)
                    if value.isdigit():
                        msg = f"{key} value must be a string."
                        return ValueError(msg)
                    output.update({key: str(value)})

                return {**team_args, **output}
        except Exception as err:
            return err

        return {**team_args, **params}

    def get_teams(self, params):
        a = self.validate(params)
        print(a)
        # if isinstance(a, Exception):
        #     print("errs")
        #
        # args = self.validate(params) if not None else team_args
        args = team_args
        if isinstance(args, Exception):
            return self.error_handler(400, str(args))

        teams_query = self.db_query(get_teams_query(**args))
        teams = teams_query.fetchall()

        total_query = self.db_query(get_teams_count())
        total_team = total_query.fetchall()[0]
        total_pages = math.floor(total_team["count"] / args["count"])

        return (
            jsonify(
                {
                    "results": list(map(self.set_team_url, teams)),
                    "info": {
                        "count": len(teams),
                        "current_page": 1,
                        "first": None,
                        "last": None,
                        "next_page": None,
                        "last_page": None,
                        "total_pages": total_pages,
                    },
                }
            ),
            200,
        )

    def get_team(self, name: str):
        print(name)
        team_query = self.db_query(get_team_query(name))
        team = team_query.fetchall()

        if len(team) == 0:
            msg = f"{name} does not exist."
            return self.error_handler(404, msg)

        result = self.set_team_url(team[0])
        return jsonify(result), 200

    def get_conference(self):
        query = self.db_query(get_conference())
        teams = query.fetchall()[0]["jsonb_object_agg"]

        if teams is None:
            msg = "Something went wrong. Please try again."
            return self.error_handler(500, msg)

        return jsonify(teams), 200

    #
    # def get_team_info(self, team_name: str):
    #     team_query = self.db_query(query_team(team_name))
    #     team = team_query.fetchall()
    #
    #     team_query.close()
    #
    #     if len(team) < 1:
    #         message = "The team you're looking for doesn't seem to exist"
    #         message += "Please check the name and try again."
    #
    #         response = {"message": message, "status_code": 404}
    #
    #         return jsonify(response), 404
    #
    #     team_roster = self.db_query(query_team_roster(team_name))
    #     roster = team_roster.fetchall()
    #
    #     team_roster.close()
    #     self.db.close()
    #
    #     return jsonify({**team[0], "roster": list(map(set_player_url, roster))})
    #
    # def get_team_games(self, team_name: str, season: int):
    #     if team_name is None or season is None:
    #         message = "Please pass <team_name> or <season_year>"
    #         response = {
    #             "code": "One or both required parameters are missing",
    #             "message": message,
    #             "status_code": 400,
    #         }
    #         return jsonify(response)
    #
    #     games_list = self.db_query(query_team_games(team_name, str(season)))
    #     games = games_list.fetchall()
    #
    #     games_list.close()
    #     self.db.close()
    #
    #     columns = extract_columns(games[0]) if len(games) > 0 else []
    #
    #     return jsonify({"columns": columns, "results": games})
