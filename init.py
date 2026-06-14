import json
from api import permission, config
from pathlib import Path
DIR = Path(__file__).resolve().parent

permission.create("log_admin", "Log Admin")
with open(f"{DIR}/actions.json", "r") as file:
    unlogged_actions = json.load(file)

config.create_field("logs", dict)
config.create_field("logged_actions", dict)
config.create_field("unlogged_actions", unlogged_actions)