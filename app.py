from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Home page!"

app.run("0.0.0.0", 5000, True)