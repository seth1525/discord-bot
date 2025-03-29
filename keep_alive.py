from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route('/')
def home():
    return "I'm alive!"  # Simple response to show server is working


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()