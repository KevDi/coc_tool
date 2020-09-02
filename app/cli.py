from app.tools.clan_war_updater import Clan_War_Updater
from app.tools.member_updater import Member_Updater
from app.tools.war_updater import War_Updater
from app.models import Mode
from app import db
from config import COC_Config


def register(app):
    @app.cli.group()
    def member():
        """ Updating Members."""
        pass

    @member.command()
    def update():
        config = COC_Config()
        updater = Member_Updater(config, app)
        updater.update()

    @app.cli.group()
    def war():
        """ Updating Wars."""
        pass

    @war.command()
    def update():
        config = COC_Config()
        updater = War_Updater(config, app)
        updater.update()

    @app.cli.group()
    def cwl():
        """ Updating Clan War League."""
        pass

    @cwl.command()
    def update():
        config = COC_Config()
        updater = Clan_War_Updater(config, app)
        updater.update()

    @app.cli.group()
    def initdb():
        """ Initialize Part of the Database """
        pass

    @initdb.command()
    def mode():
        Mode.query.delete()
        attack = Mode(mode="Attack")
        defense = Mode(mode="Defense")
        db.session.add(attack)
        db.session.add(defense)
        db.session.commit()

