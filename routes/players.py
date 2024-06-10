from flask import Blueprint, request

from modules.db import database
from modules.players import Players

app = Blueprint("players", __name__, url_prefix="/players")
players_db = Players(database)


@app.get("/")
def players():
    args = request.args if not None else None
    return players_db.get_players(args)


@app.get("/<player_slug>")
def player(player_slug):
    return players_db.get_player(player_slug)


@app.post("/find")
def find_player(keyword):
    return players_db.find_player(keyword)
