from flask import Flask
from flask_cors import CORS
from app.routes import main_route, test_route

app = Flask(__name__)
app.register_blueprint(main_route.bp)
app.register_blueprint(test_route.bp)
# 允许所有源访问，前端报错has been blocked by CORS policy: No 'Access-Control-Allow-Origin
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == '__main__':
    app.run(debug=True)