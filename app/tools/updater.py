import urllib.parse


class Updater:
    def __init__(self, config, app):
        self.app = app
        self.apikey = config.API_KEY
        self.clan_tag = self.encode_tag(config.CLAN_TAG)
        self.baseurl = config.BASE_URL

    def encode_tag(self, tag):
        return urllib.parse.quote(tag)
