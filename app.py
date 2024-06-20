import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from routes import players, teams

load_dotenv()

time = datetime.now()
started = time.strftime("%d/%m/%Y %H:%M:%S")

app = Flask(__name__, static_url_path="", static_folder="static/")
app.url_map.strict_slashes = False


CORS(app, resources={r"/*": {"origins": os.environ.get("CORS")}})


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.route("/")
def home():
    return jsonify(
        {
            "title": "NBA Players API",
            "message": f"API is up and running since {started}",
            "version": "1.0.0",
        }
    )


app.register_blueprint(players.app)
app.register_blueprint(teams.app)

if __name__ == "__main__":
    print(os.environ.get("HOST"))
    app.run()
