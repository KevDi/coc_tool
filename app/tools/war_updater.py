from app.models import War, Member, Mode, Battle
from app.tools.updater import Updater
from app import db
from datetime import datetime


class War_Updater(Updater):
    def __init__(self, config, app):
        super().__init__(config, app)
        self.war_uri = "clans/{}/currentwar".format(self.clan_tag)
        self.date_format = "%Y%m%dT%H%M%S.%fZ"

    def get_war_status(self, data):
        return data["state"]

    def war_in_preperation(self, data):
        return data["state"] == "preperation"

    def war_running(self, data):
        return data["state"] == "inWar"

    def war_ended(self, data):
        return data["state"] == "warEnded"

    def war_in_db(self, data):
        return self.load_war(data) != None

    def store_war(self, data):
        start_time = datetime.strptime(data["startTime"], self.date_format)
        end_time = datetime.strptime(data["endTime"], self.date_format)
        clan_data = self.get_clan_data(data)
        opponent_data = self.get_opponent_data(data)
        victory = (
            self.is_victory(clan_data, opponent_data) if self.war_ended(data) else None
        )
        war = War(
            size=data["teamSize"],
            clan_stars=clan_data["stars"],
            enemy=opponent_data["name"],
            enemy_tag=opponent_data["tag"],
            enemy_stars=opponent_data["stars"],
            start_time=start_time,
            end_time=end_time,
            victory=victory,
            enemy_clan_level=opponent_data["clanLevel"],
        )
        self.app.logger.info("Created War {}".format(war))
        self.load_members(clan_data, war)
        db.session.add(war)
        db.session.commit()
        return war

    def load_members(self, clan_data, war):
        for member in clan_data["members"]:
            current_member = Member.query.filter_by(id=member["tag"]).first()
            if current_member:
                self.app.logger.info(
                    "Added Member {} to War".format(current_member.name)
                )
                war.members.append(current_member)

    def is_victory(self, clan_data, opponent_data):
        clan_stars = clan_data["stars"]
        opponent_stars = opponent_data["stars"]
        if clan_stars > opponent_stars:
            return True
        elif clan_stars < opponent_stars:
            return False
        else:
            clan_percentage = clan_data["destructionPercentage"]
            opponent_percentage = opponent_data["destructionPercentage"]
            return clan_percentage > opponent_percentage

    def get_clan_data(self, data):
        return (
            data["clan"]
            if data["clan"]["tag"] == self.clan_tag_unescaped
            else data["opponent"]
        )

    def get_opponent_data(self, data):
        return (
            data["opponent"]
            if data["opponent"]["tag"] != self.clan_tag_unescaped
            else data["clan"]
        )

    def store_war_battles(self, war, data):
        self.app.logger.info("Load Battles for War against {}".format(war.enemy))
        clan_data = self.get_clan_data(data)
        opponent_data = self.get_opponent_data(data)
        for member in clan_data["members"]:
            current_member = Member.query.filter_by(id=member["tag"]).first()
            if current_member and "attacks" in member:
                attack_data = member["attacks"]
                member_th = member["townhallLevel"]
                position = member["mapPosition"]
                self.load_member_attack(
                    member=current_member,
                    member_th_level=member_th,
                    member_position=position,
                    attack_data=attack_data,
                    opponent_data=opponent_data,
                    war=war,
                )
                self.load_member_defense(
                    member=current_member,
                    member_th_level=member_th,
                    member_position=position,
                    opponent_data=opponent_data,
                    war=war,
                )
        db.session.commit()

    def load_member_defense(
        self, member, member_th_level, member_position, opponent_data, war
    ):
        self.app.logger.info("Store Defenses for Member {}".format(member.name))
        defenses = []
        for opponent in opponent_data["members"]:
            if "attacks" in opponent:
                for attack in opponent["attacks"]:
                    if attack["defenderTag"] == member.id:
                        attack["th_level"] = opponent["townhallLevel"]
                        attack["name"] = opponent["name"]
                        attack["position"] = opponent["mapPosition"]
                        defenses.append(attack)
        mode = self.load_or_create_mode("Defense")
        for defense in defenses:
            battle = self.load_battle(
                member, defense["attackerTag"], war=war, mode=mode
            )
            if not battle:
                battle = Battle(
                    enemy_tag=defense["attackerTag"],
                    enemy_name=defense["name"],
                    enemy_th_level=defense["th_level"],
                    # enemy_position=defense["position"],
                    member=member,
                    member_th_level=member_th_level,
                    # member_position=member_position,
                    stars=defense["stars"],
                    percentage=defense["destructionPercentage"],
                    war=war,
                    mode=mode,
                )
                self.app.logger.info("Store Battle {}".format(battle))
                db.session.add(battle)

    def load_member_attack(
        self, member, member_th_level, member_position, attack_data, opponent_data, war
    ):
        self.app.logger.info("Load Attacks for Member {}".format(member.name))
        for attack in attack_data:
            opponent = next(
                (
                    opp
                    for opp in opponent_data["members"]
                    if opp["tag"] == attack["defenderTag"]
                )
            )
            mode = self.load_or_create_mode("Attack")
            battle = self.load_battle(member, attack["defenderTag"], war, mode)
            if not battle:
                battle = Battle(
                    enemy_tag=attack["defenderTag"],
                    enemy_name=opponent["name"],
                    enemy_th_level=opponent["townhallLevel"],
                    enemy_position=opponent["mapPosition"],
                    member_th_level=member_th_level,
                    member_position=member_position,
                    stars=attack["stars"],
                    percentage=attack["destructionPercentage"],
                    mode=mode,
                    member=member,
                    war=war,
                )
                self.app.logger.info("Store Battle {}".format(battle))
                db.session.add(battle)

    def load_or_create_mode(self, mode):
        mode_entry = Mode.query.filter_by(mode=mode).first()
        if not mode_entry:
            mode_entry = Mode(mode=mode)
            db.session.add(mode_entry)
            db.session.commit()
        return mode_entry

    def load_battle(self, member, enemy_tag, war, mode):
        return Battle.query.filter_by(
            member=member, enemy_tag=enemy_tag, war=war, mode=mode
        ).first()

    def load_war(self, data):
        start_time = datetime.strptime(data["startTime"], self.date_format)
        end_time = datetime.strptime(data["endTime"], self.date_format)
        return War.query.filter_by(start_time=start_time, end_time=end_time).first()

    def update_victory(self, war, data):
        clan_data = self.get_clan_data(data)
        opponent_data = self.get_opponent_data(data)
        war.victory = self.is_victory(clan_data, opponent_data)

    def update(self):
        response = self.send_request(self.war_uri)
        if response.status_code != 200:
            self.app.logger.info("Error {}".format(response.status_code))
            self.app.logger.info("Message {}".format(response.json()))
            return
        data = response.json()
        if self.war_in_preperation(data) and not self.war_in_db(data):
            self.store_war(data)
        elif (self.war_running or self.war_ended) and not self.war_in_db(data):
            war = self.store_war(data)
            self.store_war_battles(war, data)
        elif (self.war_running or self.war_ended) and self.war_in_db(data):
            war = self.load_war(data)
            if self.war_ended(data):
                self.update_victory(war, data)
                db.session.commit()
            self.store_war_battles(war, data)
