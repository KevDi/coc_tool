from app import create_app, db, cli
from app.models import User, Member, War, Battle, Mode, ClanWarLeague

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Member": Member,
        "Cwl": ClanWarLeague,
        "War": War,
        "Battle": Battle,
        "Mode": Mode,
    }

