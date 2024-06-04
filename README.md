nba stats api
---

```bash
$ python -m venv .venv
$ source .venv/bin/activate

$ pip install pipenv
$ pipenv install 


# Production
waitress-serve --port=8080 --host=0.0.0.0 app:app

# Development 
flask --app app run -p 8080 -h 0.0.0.0 
```
