from api import permission, config
from utils import jsonIO
from pathlib import Path
DIR = Path(__file__).resolve().parent

permission.create("log_admin", "Log Admin")
unlogged_actions = jsonIO.load(f"{DIR}/actions.json")

config.create_field("logs", dict)
config.create_field("logged_actions", dict)
config.create_field("unlogged_actions", unlogged_actions)