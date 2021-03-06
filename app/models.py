from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Member(db.Model):
    id = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    th_level = db.Column(db.Integer)
    king_level = db.Column(db.Integer)
    queen_level = db.Column(db.Integer)
    warden_level = db.Column(db.Integer)
    royal_level = db.Column(db.Integer)

    def __repr__(self):
        return "<Member {}:{}:TH:{}:KL:{}:QL:{}:WL:{}:RL:{}>".format(
            self.id,
            self.name,
            self.th_level,
            self.king_level,
            self.queen_level,
            self.warden_level,
            self.royal_level,
        )

    def read_from_json(self, data):
        setattr(self, "id", data["tag"])
        setattr(self, "name", data["name"])
        setattr(self, "th_level", data["townHallLevel"])
        for hero in data["heroes"]:
            if hero["name"] == "Barbarian King":
                setattr(self, "king_level", hero["level"])
            elif hero["name"] == "Archer Queen":
                setattr(self, "queen_level", hero["level"])
            elif hero["name"] == "Grand Warden":
                setattr(self, "warden_level", hero["level"])
            elif hero["name"] == "Royal Champion":
                setattr(self, "royal_level", hero["level"])

    def __eq__(self, other):
        if not isinstance(other, Member):
            return NotImplemented
        return (
            self.id == other.id
            and self.name == other.name
            and self.th_level == other.th_level
            and self.queen_level == other.queen_level
            and self.king_level == other.king_level
            and self.warden_level == other.warden_level
            and self.royal_level == other.royal_level
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def update(self, other):
        self.th_level = other.th_level
        self.king_level = other.king_level
        self.queen_level = other.queen_level
        self.warden_level = other.warden_level
        self.royal_level = other.royal_level
