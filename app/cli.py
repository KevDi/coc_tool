from json import load
import os
import click
from app.tools.member_updater import Member_Updater
from app.models import Mode
from app import db
from config import COC_Config
from app.tools.load_wars_from_file import load_from_file


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
        load_from_file()

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

