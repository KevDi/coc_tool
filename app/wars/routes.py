from flask import render_template
from flask_login.utils import login_required
from app.wars import bp
from app.models import War


@bp.route("/wars")
@login_required
def wars():
    wars = War.query.all()
    return render_template("wars/wars.html", title="Wars", wars=wars)


@bp.route("/wars/<war_id>")
@login_required
def war(war_id):
    war = War.query.filter_by(id=war_id).first_or_404()
    return render_template("wars/war.html", war=war)
