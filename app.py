import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from routes import players

load_dotenv()

time = datetime.now()
started = time.strftime("%d/%m/%Y %H:%M:%S")

app = Flask(__name__, static_url_path="", static_folder="static/")
app.url_map.strict_slashes = False


CORS(app, resources={r"/*": {"origins": "same-origin, https://sbx.pongstr.io"}})


@app.errorhandler(404)
def page_not_found():
    msg = "The page you are looking for does not exist."
    msg += "Please check the URL and try again."

    res = jsonify({"code": 404, "error": "Page not found", "message": msg})
    res.status_code = 404
    return res


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

if __name__ == "__main__":
    print(os.environ.get("HOST"))
    app.run(
        host=os.environ.get("HOST"),
        port=os.environ.get("PORT") or 8080,
    )
