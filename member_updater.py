from app.models import Member
from app import db
from app import create_app
import requests
import urllib.parse


class Member_Updater:
    def __init__(self, config) -> None:
        self.app = create_app()
        self.app.app_context().push()
        self.apikey = config.API_KEY
        self.clan_tag = self.encode_tag(config.CLAN_TAG)
        self.members = Member.query.all()
        self.baseurl = config.BASE_URL
        self.clan_uri = "clans/{}/members".format(self.clan_tag)

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

    def get_member_tags(self, data):
        return [member["tag"] for member in data["items"]]

    def delete_left_members(self, current_member_tags):
        [
            db.session.delete(member)
            for member in self.members
            if member.id not in current_member_tags
        ]
        db.session.commit()

    def get_member_information(self, new_member):
        return self.send_request("players/{}".format(self.encode_tag(new_member)))

    def add_new_member(self, member_tags):
        new_member = member_tags
        [
            new_member.remove(member.id)
            for member in self.members
            if member.id in new_member
        ]
        for tag in new_member:
            response = self.get_member_information(tag)
            if response.status_code != 200:
                continue
            member = self.create_member(response.json())
            if member:
                self.app.logger.info("Add new Member {}".format(member))
                db.session.add(member)

    def create_member(self, data):
        member = Member()
        member.read_from_json(data)
        return member

    def update_member(self):
        for member in self.members:
            response = self.get_member_information(member.id)
            if response.status_code != 200:
                continue
            new_member_data = self.create_member(response.json())
            if new_member_data != member:
                self.app.logger.info("Updated Member {}".format(member))
                member.update(new_member_data)

    def update(self):
        response = self.send_request(self.clan_uri)
        if response.status_code != 200:
            print("error")
            print(response.json())
            return
        member_tags = self.get_member_tags(response.json())
        self.delete_left_members(member_tags)
        self.update_member()
        self.add_new_member(member_tags)
        db.session.commit()
