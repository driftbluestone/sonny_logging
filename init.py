import json
from api import permission, config
from pathlib import Path
DIR = Path(__file__).resolve().parent

permission.create("log_admin", "Log Admin", "administrator")
with open(f"{DIR}/actions.json", "r") as file:
    unlogged_actions = json.load(file)
config.create_field(["logs", "logged_actions", "unlogged_actions"], [dict, dict, unlogged_actions])