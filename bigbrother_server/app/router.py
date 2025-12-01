from flask import Blueprint, request, jsonify
bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    return 'asdasdasda, World!'

@bp.route('/test')
def test():
    return '111111111, World!'


# GET 请求示例（默认就是 GET，可以不写 methods）
@bp.route('/api/get-example', methods=['GET'])
def get_example():
    # 获取 GET 请求的查询参数
    name = request.args.get('name', 'World')
    return jsonify({'message': f'Hello, {name}!', 'method': 'GET'})


# POST 请求示例
@bp.route('/api/post-example', methods=['POST'])
def post_example():
    # 获取 POST 请求的 JSON 数据
    data = request.get_json()
    if data:
        name = data.get('name', 'World')
        return jsonify({'message': f'Hello, {name}!', 'method': 'POST', 'received_data': data})
    else:
        # 获取表单数据
        name = request.form.get('name', 'World')
        return jsonify({'message': f'Hello, {name}!', 'method': 'POST'})


# 同时支持 GET 和 POST 请求
@bp.route('/api/both', methods=['GET', 'POST'])
def both_methods():
    if request.method == 'GET':
        # 处理 GET 请求
        name = request.args.get('name', 'World')
        return jsonify({'message': f'GET: Hello, {name}!', 'method': 'GET'})
    elif request.method == 'POST':
        # 处理 POST 请求
        data = request.get_json() or {}
        name = data.get('name', 'World')
        return jsonify({'message': f'POST: Hello, {name}!', 'method': 'POST', 'received_data': data})


