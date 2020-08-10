from app.models import Member
from app.tools.updater import Updater
from app import db


class Member_Updater(Updater):
    def __init__(self, config, app) -> None:
        super().__init__(config, app)
        self.members = Member.query.all()
        self.clan_uri = "clans/{}/members".format(self.clan_tag)

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
                self.app.logger.info("New Member Data {}".format(new_member_data))
                self.app.logger.info("Updated Member {}".format(member))
                member.update(new_member_data)

    def update(self):
        response = self.send_request(self.clan_uri)
        if response.status_code != 200:
            self.app.logger.info("Error {}".format(response.status_code))
            self.app.logger.info("Message {}".format(response.json()))
            return
        member_tags = self.get_member_tags(response.json())
        self.delete_left_members(member_tags)
        self.update_member()
        self.add_new_member(member_tags)
        db.session.commit()
