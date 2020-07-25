from flask import Blueprint

bp = Blueprint("wars", __name__)

from app.wars import routes
