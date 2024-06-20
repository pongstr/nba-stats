from flask import Blueprint, request

from modules.db import database
from modules.teams import Teams

app = Blueprint("teams", __name__, url_prefix="/teams")
teams = Teams(database)


@app.get("/")
def get_teams():
    args = request.args if not None else None
    return teams.get_teams(args)


@app.get("/conference")
def get_conference():
    return teams.get_conference()


@app.get("/<name>")
def get_team(name: str):
    print(name)
    return teams.get_team(name)
