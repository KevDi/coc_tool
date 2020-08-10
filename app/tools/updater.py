import urllib.parse
import requests


class Updater:
    def __init__(self, config, app):
        self.app = app
        self.apikey = config.API_KEY
        self.clan_tag_unescaped = config.CLAN_TAG
        self.clan_tag = self.encode_tag(config.CLAN_TAG)
        self.baseurl = config.BASE_URL

    def encode_tag(self, tag):
        return urllib.parse.quote(tag)

    def send_request(self, url):
        url = "{}/{}".format(self.baseurl, url)
        self.app.logger.info("Send Request to URL {}".format(url))
        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer {}".format(self.apikey),
            },
        )
        return response
