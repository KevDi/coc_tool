from app.models import War
from app.tools.updater import Updater
from app import db


class WarUpdater(Updater):
    def __init__(self, config, app):
        super().__init__(config, app)
        self.war_uri = "clans/{}/"
