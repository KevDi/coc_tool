from flask import render_template
from flask_login.utils import login_required
from app.member import bp
from app.models import Member


@bp.route("/")
@bp.route("/index")
@login_required
def index():
    members = Member.query.all()
    return render_template("member/index.html", title="Home", members=members)


@bp.route("/member/<membername>")
@login_required
def member(membername):
    member = Member.query.filter_by(name=membername).first_or_404()
    return render_template("member/member.html", member=member)

