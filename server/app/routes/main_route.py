from flask import Blueprint
import app.routes.response as rsp
from ..service.heatmap_service import HeatmapService
from pandas import DataFrame
bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return 'asdasdasda, World!'


@bp.route('/industry/heatmap')
def industry_heatmap():
    hm = HeatmapService()
    results = hm.get_industry_history_data()
    print(results)
    x_axis = []
    y_axis = []
    data = []
    for y, result in enumerate(results):

        industry = result['industry']
        histories: DataFrame = result['history'].iloc[::-1].copy()
        print()
        if len(x_axis) == 0:
            x_axis = histories['日期'].tolist()

        y_axis.append(industry['板块名称'] + '\n' + industry['板块代码'])

        for x, history in histories.iterrows():
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