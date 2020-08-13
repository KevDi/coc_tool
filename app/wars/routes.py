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
    attacks = [battle for battle in war.battles if battle.mode.mode == "Attack"]
    clan_attack_size = len(attacks)
    clan_stars = sum(attack.stars for attack in attacks)
    clan_percentage = sum(attack.percentage for attack in attacks) / war.size
    clan_three_stars = sum(attack.stars == 3 for attack in attacks)
    clan_two_stars = sum(attack.stars == 2 for attack in attacks)
    clan_one_stars = sum(attack.stars == 1 for attack in attacks)
    clan_zero_stars = sum(attack.stars == 0 for attack in attacks)

    clan_war_result = {
        "stars": clan_stars,
        "percentage": clan_percentage,
        "three_stars": clan_three_stars,
        "two_stars": clan_two_stars,
        "one_stars": clan_one_stars,
        "zero_stars": clan_zero_stars,
        "attacks": clan_attack_size,
    }

    defenses = [battle for battle in war.battles if battle.mode.mode == "Defense"]
    opponent_attack_size = len(defenses)
    opponent_stars = sum(defense.stars for defense in defenses)
    opponent_percentage = sum(defense.percentage for defense in defenses) / war.size
    opponent_three_stars = sum(defense.stars == 3 for defense in defenses)
    opponent_two_stars = sum(defense.stars == 2 for defense in defenses)
    opponent_one_stars = sum(defense.stars == 1 for defense in defenses)
    opponent_zero_stars = sum(defense.stars == 0 for defense in defenses)

    opponent_war_result = {
        "attacks": opponent_attack_size,
        "stars": opponent_stars,
        "percentage": opponent_percentage,
        "three_stars": opponent_three_stars,
        "two_stars": opponent_two_stars,
        "one_stars": opponent_one_stars,
        "zero_stars": opponent_zero_stars,
    }

    return render_template(
        "wars/war.html",
        war=war,
        clan_war_result=clan_war_result,
        opponent_war_result=opponent_war_result,
    )
