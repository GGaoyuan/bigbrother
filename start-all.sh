#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 启动所有服务..."

# 启动 FastAPI 后端
echo "📦 启动 FastAPI 后端..."
cd "$SCRIPT_DIR/FastAPI"
nohup uvicorn main:app --reload --host 127.0.0.1 --port 8000 > fastapi.log 2>&1 &
FASTAPI_PID=$!
echo "✅ FastAPI 已启动 (PID: $FASTAPI_PID, 端口: 8000)"

# 启动 webfront 前端
echo "🌐 启动 webfront 前端..."
cd "$SCRIPT_DIR/webfront"
nohup npm run dev > webfront.log 2>&1 &
WEBFRONT_PID=$!
echo "✅ webfront 已启动 (PID: $WEBFRONT_PID)"

echo ""
echo "✨ 所有服务已启动完成！"
echo "   - FastAPI: http://127.0.0.1:8000"
echo "   - webfront: 查看 webfront/webfront.log 获取端口信息"
echo ""
echo "💡 使用 ./stop-all.sh 停止所有服务"
