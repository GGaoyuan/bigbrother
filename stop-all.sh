#!/bin/bash

echo "🛑 停止所有服务..."

# 停止 FastAPI 后端
echo "📦 停止 FastAPI 后端..."
pkill -f "uvicorn main:app"
if [ $? -eq 0 ]; then
    echo "✅ FastAPI 已停止"
else
    echo "⚠️  未找到运行中的 FastAPI 进程"
fi

# 停止 webfront 前端
echo "🌐 停止 webfront 前端..."
pkill -f "vite"
if [ $? -eq 0 ]; then
    echo "✅ webfront 已停止"
else
    echo "⚠️  未找到运行中的 webfront 进程"
fi

echo ""
echo "✨ 所有服务已停止！"
