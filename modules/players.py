import math
from typing import Dict, Optional

from flask import jsonify
from players_query import (find_player, get_player, get_players,
                           get_players_count)
from psycopg2 import extras

get_players_args = {
    "active": 1,
    "page": 1,
    "show": 20,
}

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

    def validate_get_players_args(input: Optional[Dict[str, str]]):
        allowed = ["active", "page", "show"]
        output = get_players_args

        if input is None:
            return output

        for key, value in input.items():
            if key not in allowed:
                return output

            if not value.isdigit():
                return output

            if value.isdigit():
                output[key] = int(value)

        return output


    def build_url(dir: str, args: Dict[str, int], total_pages: int):
        pathname = "/players?active=%s&page=%s&show=%s"

        if dir == "last":
            if total_pages == args["page"]:
                return None
            return pathname % (args["active"], total_pages, args["show"])

        if dir == "first":
            if args["page"] == 1:
                return None
            return pathname % (args["active"], 1, args["show"])

        if dir == "prev" and args["page"] <= 1:
            return None

        if dir == "next" and args["page"] >= total_pages:
            return None

        page = args["page"] + 1 if dir == "next" else args["page"] - 1
        return pathname % (args["active"], page, args["show"])


    """
    get players
    - lists all active or inactive players
    - returns pagination info

    @param active: indicates whether to return inactive players
    @param page:   indicates the current page of the list
    @param show:   indicates how many records should be returned
    """

    def get_players(self, args: Dict[str, str] = None):
        args = self.validate_get_players_args(args)

        offset = (args["page"] - 1) * args["show"]

        players_list = self.db_query(get_players(args, offset))
        players = players_list.fetchall()

        active = args["active"]
        players_count = self.db_query(get_players_count(active))
        count = players_count.fetchall()

        players_list.close()
        players_count.close()

        total_pages = math.floor((int(count[0]["count"])) / args["show"])

        if args["active"] > 1:
            results = list(map(set_player_url, players))
            return jsonify({"count": len(players), "results": results})

        if args["page"] > total_pages:
            msg = "You might have reached the end of the list. "
            msg += "Please check the URL and try again."
            res = jsonify({"error": "404 Page not found", "message": msg})
            res.status_code = 404
            return res

        info = {
            "count": len(players),
            "current_page": args["page"],
            "first": self.build_url("first", args, total_pages),
            "last": self.build_url("last", args, total_pages),
            "next_page": self.build_url("next", args, total_pages),
            "prev_page": self.build_url("prev", args, total_pages),
            "total_pages": total_pages,
        }

        results = list(map(set_player_url, players))
        return jsonify({"results": results, "info": info})

    """
    get player
    """

    def get_player(self, player_slug: str):
        players_list = self.db_query(get_player(player_slug))
        player = players_list.fetchall()

        players_list.close()

        if len(player) < 1:
            message = "The player you are looking for does not exist. "
            message += "Please check the URL and try again."

            response = jsonify({"error": "404 Not found", "message": message})
            response.status_code = 404
            return response

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
