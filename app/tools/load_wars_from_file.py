import json
import os
from app.models import War


def load_from_file():
    basedir = os.path.abspath(os.path.dirname("app.db"))
    war_file = os.path.join(basedir, "data/20200714165847.json")
    print(war_file)
    print(os.path.exists(war_file))

    with open(war_file) as war_to_load:
        data = json.load(war_to_load)
        war = War()
        war.read_from_json(data)
        print(war)
