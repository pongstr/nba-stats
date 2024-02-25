import math
from psycopg2 import extras
from typing import Dict, Optional
from flask import jsonify

get_players_args = {
    "active": 1,
    "page": 1,
    "show": 20,
}


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

    if (dir == "last"):
        if total_pages == args["page"]:
            return None
        return pathname % (args["active"], total_pages, args["show"])

    if (dir == "first"):
        if args["page"] == 1:
            return None
        return pathname % (args["active"], 1, args["show"])

    if dir == "prev" and args["page"] <= 1:
        return None

    if dir == "next" and args["page"] >= total_pages:
        return None

    page = args["page"] + 1 if dir == "next" else args["page"] - 1
    return pathname % (args["active"], page, args["show"])


def set_player_url(player: Dict[str, str]):
    player["url"] = "/players/" + player["player_slug"]
    return player


def get_players_query(args: Dict[str, int], offset: int):
    base_query = """
    SELECT * FROM common_player_info
        JOIN player ON common_player_info.person_id = player.id
    """

    print(args['active'])

    active_query = """
    WHERE is_active = %s
    """ % (args["active"])

    offset_limit_query = """
    LIMIT %s
    OFFSET %s
    """ % (args["show"], offset)

    if args["active"] > 1:
        return ' '.join([base_query, offset_limit_query])

    return ' '.join([base_query, active_query, offset_limit_query])


def get_players_count(active: int):
    return ("""
        SELECT COUNT(person_id) FROM common_player_info
            JOIN player ON common_player_info.person_id = player.id
            WHERE is_active = %s;
    """) % (active)


def get_player_query(player_slug: str):
    return ("""
    SELECT * FROM common_player_info
        JOIN player ON common_player_info.person_id = player.id
        WHERE player_slug = '%s'
        LIMIT 1;
    """) % (player_slug)


class Players():
    def __init__(self, db):
        self.db = db

    """
    """

    def db_query(self, query: str):
        db = self.db.cursor(cursor_factory=extras.RealDictCursor)
        db.execute(query)
        return db

    """
    get players
    - lists all active or inactive players
    - returns pagination info

    @param active: indicates whether to return inactive players
    @param page:   indicates the current page of the list
    @param show:   indicates how many records should be returned
    """

    def get_players(self, args: Dict[str, str] = None):
        args = validate_get_players_args(args)

        offset = (args["page"] - 1) * args["show"]

        players_list = self.db_query(get_players_query(args, offset))
        players = players_list.fetchall()

        players_list.close()

        players_count = self.db_query(get_players_count(args["active"]))
        count = players_count.fetchall()

        players_count.close()
        self.db.close()

        total_pages = math.floor((int(count[0]["count"])) / args["show"])

        if args['active'] > 1:
            return jsonify({
                "count": len(players),
                "results": list(map(set_player_url, players))
            })

        if args["page"] > total_pages:
            message = "You might have reached the end of the list."
            message += "Please check the URL and try again."
            response = jsonify({
                "error": "404 Page not found",
                "message": message
            })
            response.status_code = 404
            return response

        info = {
            "count": len(players),
            "current_page": args["page"],
            "first": build_url("first", args, total_pages),
            "last": build_url("last", args, total_pages),
            "next_page": build_url("next", args, total_pages),
            "prev_page": build_url("prev", args, total_pages),
            "total_pages": total_pages
        }

        return jsonify({
            "results": list(map(set_player_url, players)),
            "info": info
        })

    def get_player(self, player_slug: str):
        players_list = self.db_query(get_player_query(player_slug))
        player = players_list.fetchall()

        players_list.close()
        self.db.close()

        if len(player) < 1:
            message = "The player you are looking for does not exist."
            message += "Please check the URL and try again."

            response = jsonify({
                "error": "404 Not found",
                "message": message
            })
            response.status_code = 404
            return response

        return jsonify(player[0])
