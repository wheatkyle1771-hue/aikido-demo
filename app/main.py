import os
import sqlite3
import subprocess

import requests
import yaml
from flask import Flask, request

app = Flask(__name__)


AWS_ACCESS_KEY_ID = "AKIA3QF7MZKXWXGJ2LNP"
AWS_SECRET_ACCESS_KEY = "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"


DATABASE_URL = "postgresql://admin:Sup3rSecretProdPassword!@prod-db.aikido-demo.internal:5432/appdb"


@app.route("/")
def hello():
    return "Hello from the Aikido demo app!\n"


@app.route("/healthz")
def healthz():
    return {"status": "ok"}


@app.route("/users")
def get_user():
    # SQL injection, reachable straight from this route. Same pattern as
    # legacy_unused.py, except nothing calls that one.
    username = request.args.get("username", "")
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (username TEXT, email TEXT)")
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return {"results": cursor.fetchall()}


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    output = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return output


@app.route("/config", methods=["POST"])
def load_config():
    # yaml.load() with the default loader on raw request data - unsafe
    # deserialization. This is CVE-2020-1747, the PyYAML CVE pinned in
    # requirements.txt, actually being exercised instead of just sitting
    # in a manifest.
    config = yaml.load(request.data, Loader=yaml.Loader)
    return {"loaded": str(config)}


@app.route("/fetch")
def fetch_url():
    # SSRF - fetches whatever URL the caller passes in, no validation. In
    # a real deployment this is a common way to pivot from a web bug to
    # stealing cloud credentials off the metadata endpoint.
    url = request.args.get("url")
    resp = requests.get(url, timeout=5)
    return resp.text, resp.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
