from flask import Blueprint
from app.service.heatmap_service import HeatmapService

bp = Blueprint('test', __name__)

@bp.route('/a')
def home():
    heatmapService = HeatmapService()
    return 'aaaaaaa, World!'