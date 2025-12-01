from flask import Flask
from flask_cors import CORS
from app import router

app = Flask(__name__)
app.register_blueprint(router.bp)
# 允许所有源访问，前端报错has been blocked by CORS policy: No 'Access-Control-Allow-Origin'
CORS(app, resources={r"/*": {"origins": "*"}})
