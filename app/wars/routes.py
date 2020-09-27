from flask import render_template
from flask_login.utils import login_required
from app.wars import bp
from app.models import War, ClanWarLeague


@bp.route("/wars")
@login_required
def wars():
    wars = War.query.order_by(War.start_time.desc()).all()
    return render_template("wars/wars.html", title="Wars", wars=wars)


@bp.route("/wars/<war_id>")
@login_required
def war(war_id):
    war = War.query.filter_by(id=war_id).first_or_404()
    attacks = [battle for battle in war.battles if battle.mode.mode == "Attack"]
    clan_attack_size = len(attacks)
    clan_stars = war.clan_stars
    clan_percentage = war.clan_percentage
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
    opponent_stars = war.enemy_stars
    opponent_percentage = war.enemy_percentage
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

    user_battles = []

    for member in war.members:
        attacks = [
            attack
            for attack in war.battles
            if attack.mode.mode == "Attack" and attack.member == member
        ]
        defense = [
            defense
            for defense in war.battles
            if defense.mode.mode == "Defense" and defense.member == member
        ]

        position = war.size + 1
        if attacks:
            position = attacks[0].member_position
        elif defense:
            position = defense[0].member_position

        user_battles.append(
            {
                "position": position,
                "member": member.name,
                "attacks": attacks,
                "defenses": defense,
            }
        )

    user_battles = sorted(user_battles, key=lambda k: k["position"])

    return render_template(
        "wars/war.html",
        war=war,
        clan_war_result=clan_war_result,
        opponent_war_result=opponent_war_result,
        user_battles=user_battles,
    )


@bp.route("/clan-wars")
@login_required
def clan_wars():
    cwl = ClanWarLeague.query.all()
    return render_template("wars/clan_wars.html", title="Clan War Leagues", cwl=cwl)


@bp.route("/clan_wars/<cwl_id>")
@login_required
def clan_war(cwl_id):
    cwl = ClanWarLeague.query.filter_by(id=cwl_id).first_or_404()

    cwl_data = []
    for member in cwl.members:
        member_dict = {
            member.id: member.id,
            "name": member.name,
            "th": member.th_level,
            "wars": [None] * 7,
        }
        cwl_data.append(member_dict)

    cwl_data = sorted(cwl_data, key=lambda k: k["th"], reverse=True)

    for i, war in enumerate(cwl.wars):
        attacks = [attack for attack in war.battles if attack.mode.mode == "Attack"]
        for attack in attacks:
            member_dict = [data for data in cwl_data if attack.member.id in data]
            if member_dict:
                member_dict[0]["wars"][i] = attack

    for member_data in cwl_data:
        three_star_attacks = sum(
            1
            for attack in member_data["wars"]
            if attack is not None and attack.stars == 3
        )
        battles_count = sum(1 for attack in member_data["wars"] if attack is not None)
        member_data["applications"] = battles_count
        member_data["three_stars"] = three_star_attacks

    return render_template("wars/clan_war.html", title="Clan War League", cwl=cwl_data)
