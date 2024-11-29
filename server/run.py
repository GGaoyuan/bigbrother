from app import create_app
from flask_cors import CORS

app = create_app()
# 允许所有源访问，前端报错has been blocked by CORS policy: No 'Access-Control-Allow-Origin
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == '__main__':
    app.run(debug=True)