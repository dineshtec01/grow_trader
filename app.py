from flask import Flask, render_template, request, redirect, url_for, session, abort
import os, yaml, requests
from flask import render_template, session, redirect, url_for,Blueprint
from routes.api import api_bp

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.register_blueprint(api_bp)


users = {
    "admin": "admin",
    "dbehera": "password",
    "a": "a"
}

# Load strategy names from YAML
def load_strategies():
    with open("config/strategies.yaml", "r") as f:
        config = yaml.safe_load(f)
    return {
        "stocks": config.get("stocks", []),
        "etfs": config.get("etfs", [])
    }

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["user"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/index")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    strategies = load_strategies()
    return render_template("index.html", stocks=strategies["stocks"], etfs=strategies["etfs"])

@app.route("/strategy/<name>")
def strategy(name):
    if "user" not in session:
        return redirect(url_for("login"))
    
    try:
        # Local/internal API call
        print("***************** > ")
        response = requests.get("http://localhost:5000/api/etf_signals")  # NOTE: Use env/config later
        response.raise_for_status()
        signals = response.json()
    except Exception as e:
        signals = []
        print(f"Error fetching signals: {e}")  # Or log this

    template_name = f"{name}.html"
    template_path = os.path.join("templates", template_name)
    if os.path.exists(template_path):
        return render_template(template_name)
    else:
        return abort(404, f"Strategy template '{template_name}' not found.")

@app.route("/strategy/etf_daily1")
def etf_daily():
    if "user" not in session:
        return redirect(url_for("login"))

    try:
        # Local/internal API call
        response = requests.get("http://localhost:5000/api/etf_signals")  # NOTE: Use env/config later
        response.raise_for_status()
        signals = response.json()
    except Exception as e:
        signals = []
        print(f"Error fetching signals: {e}")  # Or log this

    return render_template("etf_daily.html", signals=signals)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
