import math
from typing import Dict, Union
from urllib.parse import urlencode

from flask import jsonify
from psycopg2 import extras

from modules.players_query import (
    GetPlayerArgs,
    find_player,
    get_player,
    get_players,
    get_players_args,
    get_players_count,
)


def set_player_url(player: Dict[str, str]):
    player["url"] = "/players/" + player["player_slug"]
    return player


class Players:
    def __init__(self, db):
        self.db = db

    def db_query(self, query: str):
        db = self.db.cursor(cursor_factory=extras.RealDictCursor)
        db.execute(query)
        return db

    def validate_get_players_args(self, input) -> GetPlayerArgs:
        allowed = ["active", "page", "show"]
        output = input.copy()

        if len(input) == 0:
            return get_players_args

        for key, value in input.items():
            if key not in allowed:
                return {**get_players_args, **output}

            if not value.isdigit():
                return {**get_players_args, **output}

            if value.isdigit():
                output.update({key: int(value)})

        return {**get_players_args, **output}

    def build_url(
        self,
        dir: str,
        args: GetPlayerArgs,
        params: Dict[str, Union[str, int]],
        total_pages: int,
    ):
        keys = list(params.keys())
        npath: Dict[str, Union[str, int, object]] = {**args}

        active = int(args["active"])
        count = int(args["count"])

        if len(keys) == 0:
            del npath["orderby"]
            del npath["field"]

        if dir == "last":
            if total_pages == args["page"]:
                return None
            pages = total_pages
            npath.update({"active": active, "count": count, "page": pages})
            return "".join(["/players?", urlencode(npath)])

        if dir == "first":
            if args["page"] == 1:
                return None

            npath.update({"active": active, "count": count, "page": 1})
            return "".join(["/players?", urlencode(npath)])

        if dir == "prev" and int(args["page"]) <= 1:
            return None

        if dir == "next" and int(args["page"]) >= total_pages:
            return None

        current = int(args["page"])
        page = int(args["page"]) + 1 if dir == "next" else current - 1
        active = int(args["active"])
        count = int(args["count"])
        npath.update({"active": active, "count": count, "page": page})

        return "".join(["/players?", urlencode(npath)])

    """
    get players
    - lists all active or inactive players
    - returns pagination info

    @param active: indicates whether to return inactive players
    @param page:   indicates the current page of the list
    @param show:   indicates how many records should be returned
    """

    def get_players(self, params):
        args = self.validate_get_players_args(params)
        players_list = self.db_query(get_players(**args))
        players = players_list.fetchall()

        players_count = self.db_query(get_players_count(args["active"]))
        total_players = players_count.fetchall()[0]

        total_pages = math.floor(total_players["count"] / int(args["count"]))

        if int(args["active"]) > 1:
            results = list(map(set_player_url, players))
            return jsonify({"count": len(players), "results": results})

        if int(args["page"]) > total_pages:
            msg = "You might have reached the end of the list. "
            msg += "Please check the URL and try again."
            res = jsonify({"error": "404 Page not found", "message": msg})
            res.status_code = 404
            return res

        print(args)

        info = {
            "count": len(players),
            "current_page": args["page"],
            "first": self.build_url("first", args, params, total_pages),
            "last": self.build_url("last", args, params, total_pages),
            "next_page": self.build_url("next", args, params, total_pages),
            "prev_page": self.build_url("prev", args, params, total_pages),
            "total_pages": total_pages,
        }
        #

        players_list.close()
        players_count.close()

        results = list(map(set_player_url, players))
        return jsonify({"results": results, "info": info})

    """
    get player
    """

    def get_player(self, player_slug: str):
        players_list = self.db_query(get_player(player_slug))
        player = players_list.fetchall()

        if len(player) < 1:
            message = "The player you are looking for does not exist. "
            message += "Please check the URL and try again."

            response = jsonify({"error": "404 Not found", "message": message})
            response.status_code = 404
            return response

        players_list.close()
        return jsonify(player[0])

    """
    find player
    """

    def find_player(self, search_keyword: str):
        players_list = self.db_query(find_player(search_keyword))
        players = players_list.fetchall()

        players_list.close()

        return jsonify(
            {
                "count": len(players),
                "results": list(map(set_player_url, players)),
            }
        )
