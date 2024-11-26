from flask import Blueprint

bp = Blueprint('test', __name__)

@bp.route('/a')
def home():
    return 'aaaaaaa, World!'