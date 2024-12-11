from flask import Blueprint
import app.routes.response as rsp
from ..service.heatmap_service import HeatmapService
bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return 'asdasdasda, World!'


@bp.route('/industry/heatmap')
def industry_heatmap():
    industries = HeatmapService.get_industry_history_data()
    x_axis = []
    y_axis = []
    data = []
    for y, industry in enumerate(industries):
        y_axis.append(industry['板块名称'] + '\n' + industry['板块代码'])
        history_list = industry['history_list']
        if len(x_axis) == 0:
            x_axis = [d['日期'] for d in history_list]
        for x, history in enumerate(history_list):
            price_change: list = [x, y, history['涨跌幅']]
            data.append(price_change)

    rsp_value = dict()
    rsp_value['title'] = 'im title'
    rsp_value['minMapValue'] = 'minMapValue'
    rsp_value['maxMapValue'] = 'maxMapValue'
    rsp_value['xAxis'] = x_axis
    rsp_value['yAxis'] = y_axis
    rsp_value['data'] = data
    json = rsp.to_json(data = rsp_value)
    return json

@bp.route('/industry/heatmap2')
def industry_heatmap2():
    industries = HeatmapService.get_industry_history_data()

@bp.route('/heatmap/concept')
def heatmap_concept():
    concept = HeatmapService.get_concept_history_data()
    print(concept)