import os
import click
from app.tools.member_updater import Member_Updater
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
