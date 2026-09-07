# Dead code. Nothing in this app imports or calls anything in this file -
# each function below is the same vulnerability class as one of the live
# routes in main.py, just with no path that reaches it. Good set to point
# at if reachability analysis comes up: same four CWEs, reachable in
# main.py, unreachable here.

import sqlite3
import subprocess

import requests
import yaml


def get_user_legacy(username):
    # Same SQL injection as /users.
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (username TEXT, email TEXT)")
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()


def ping_legacy(host):
    # Same command injection as /ping.
    return subprocess.check_output(f"ping -c 1 {host}", shell=True)


def load_config_legacy(raw_yaml):
    # Same unsafe deserialization as /config.
    return yaml.load(raw_yaml, Loader=yaml.Loader)


def fetch_url_legacy(url):
    # Same SSRF as /fetch.
    return requests.get(url, timeout=5)
