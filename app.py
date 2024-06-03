import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from modules.players import Players
from modules.teams import Teams

load_dotenv()

app = Flask(__name__, static_url_path="", static_folder="static/")
url = os.environ.get("DB_URL")

app.url_map.strict_slashes = False

time = datetime.now()
started = time.strftime("%d/%m/%Y %H:%M:%S")

CORS(app, resources={r"/*": {"origins": "same-origin, https://sbx.pongstr.io"}})


def db():
    connection = psycopg2.connect(url)
    return connection


@app.errorhandler(404)
def page_not_found():
    message = "The page you are looking for does not exist."
    message += "Please check the URL and try again."

    response = jsonify({"code": 404, "error": "Page not found", "message": message})

    response.status_code = 404
    return response


@app.route("/")
def home():
    return jsonify(
        {
            "title": "NBA Players API",
            "message": "API is up and running since " + started,
            "version": "1.0.0",
        }
    )


@app.get("/players")
def players():
    players = Players(db())
    args = request.args if not None else None
    return players.get_players(args)


@app.get("/players/<player_slug>")
def player(player_slug):
    players = Players(db())
    return players.get_player(player_slug)


@app.post("/players/find/<keyword>")
def find_player(keyword):
    players = Players(db())
    return players.find_player(keyword)


@app.get("/teams")
def teams():
    teams = Teams(db())
    return teams.get_teams()


@app.get("/teams/<name>")
def team(name):
    teams = Teams(db())
    return teams.get_team_info(name)


@app.get("/teams/<name>/games")
def games(name: str):
    games = Teams(db())
    return games.get_team_games(name, 2022)


@app.get("/teams/<name>/games/<season>")
def season(name: str, season: int):
    games = Teams(db())
    return games.get_team_games(name, season)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST"),
        port=os.environ.get("PORT") or 8080,
        debug=True,
    )
