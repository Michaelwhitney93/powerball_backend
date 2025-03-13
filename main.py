from flask import Flask
from db.engine import init_db, tear_down_db

app = Flask(__name__)
init_db()

@app.route("/")
def default():
    return "<p>Hello World!</p>"

@app.teardown_appcontext
def remove_session(exception=None):
    tear_down_db()


if __name__ == "__main__":
    app.run(debug=True)