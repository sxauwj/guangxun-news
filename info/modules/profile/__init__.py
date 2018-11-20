from flask import Blueprint

profile_blue = Blueprint('profile_blue',__name__,url_prefix='/user')

from . import views