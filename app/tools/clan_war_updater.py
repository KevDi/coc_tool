from app.models import ClanWarLeague, War, Member, Mode, Battle
from app.tools.updater import Updater
from app.tools.war_updater import War_Updater
from app import db


class Clan_War_Updater(Updater):
    def __init__(self, config, app):
        super().__init__(config, app)
        self.clan_war_uri = "clans/{}/currentwar/leaguegroup".format(self.clan_tag)
        self.war_updater = War_Updater(config, app)

    def clan_war_in_preperation(self, data):
        return data["state"] == "preperation"

    def clan_war_running(self, data):
        return data["state"] == "inWar"

    def clan_war_ended(self, data):
        return data["state"] == "warEnded"

    def clan_war_in_db(self, data):
        return self.load_clan_war(data) != None

    def load_clan_war(self, data):
        season = data["season"]
        return ClanWarLeague.query.filter_by(season=season).first()

    def load_members(self, cwl, data):
        clan_data = next(
            clan for clan in data["clans"] if clan["tag"] == self.clan_tag_unescaped
        )
        for member in clan_data["members"]:
            current_member = Member.query.filter_by(id=member["tag"]).first()
            if current_member:
                self.app.logger.info(
                    "Added Member {} to CWL".format(current_member.name)
                )
                cwl.members.append(current_member)

    def store_clan_war(self, data):
        season = data["season"]
        cwl = ClanWarLeague(season=season)
        self.app.logger.info("Created CWL {}".format(season))
        self.load_members(cwl, data)
        db.session.add(cwl)
        db.session.commit()
        return cwl

    def contains_clan_round(self, data):
        return (
            data["clan"]["tag"] == self.clan_tag_unescaped
            or data["opponent"]["tag"] == self.clan_tag_unescaped
        )

    def load_war(self, data, cwl):
        war = self.war_updater.process_war(data)
        cwl.wars.append(war)
        db.session.commit()

    def load_wars(self, data, cwl):
        rounds = data["rounds"]
        for round in rounds:
            for tag in round["warTags"]:
                if tag == "#0":
                    continue
                uri = "clanwarleagues/wars/{}".format(self.encode_tag(tag))
                response = self.send_request(uri)
                if response.status_code != 200:
                    self.app.logger.info("Error {}".format(response.status_code))
                    self.app.logger.info("Message {}".format(response.json()))
                    return
                data = response.json()
                if self.contains_clan_round(data):
                    self.load_war(data, cwl)

    def update(self):
        response = self.send_request(self.clan_war_uri)
        if response.status_code != 200:
            self.app.logger.info("Error {}".format(response.status_code))
            self.app.logger.info("Message {}".format(response.json()))
            return
        data = response.json()

        if self.clan_war_in_preperation(data) and not self.clan_war_in_db(data):
            self.store_clan_war(data)
        elif (
            self.clan_war_running(data) or self.clan_war_ended
        ) and not self.clan_war_in_db(data):
            cwl = self.store_clan_war(data)
            self.load_wars(data, cwl)
        elif (
            self.clan_war_running(data) or self.clan_war_ended(data)
        ) and self.clan_war_in_db(data):
            cwl = self.load_clan_war(data)
            self.load_wars(data, cwl)
