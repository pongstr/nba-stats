from flask import Blueprint, jsonify, request

from modules.db import database
from modules.players import Players

app = Blueprint("players", __name__, url_prefix="/players")
players_db = Players(database)


def error_handler(code: int, msg: str):
    return jsonify({"status": str(code), "message": msg}, code)


@app.get("/")
def players():
    args = request.args if not None else None
    return players_db.get_players(args)


@app.post("/")
def find_player():
    return players_db.find_player(request)


@app.get("/<player_slug>")
def player(player_slug):
    return players_db.get_player(player_slug)
