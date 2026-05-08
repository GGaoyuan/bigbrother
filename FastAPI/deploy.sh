#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/app.pid"
LOG_FILE="$SCRIPT_DIR/app.log"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "服务已在运行中 (PID: $PID)"
        exit 0
    fi
fi

if command -v uvicorn &>/dev/null; then
    UVICORN="uvicorn"
elif [ -f "$SCRIPT_DIR/venv/bin/uvicorn" ]; then
    UVICORN="$SCRIPT_DIR/venv/bin/uvicorn"
else
    echo "未找到 uvicorn，请先执行: pip install -r requirements.txt"
    exit 1
fi

cd "$SCRIPT_DIR"
nohup $UVICORN main:app --host 0.0.0.0 --port 8000 >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "服务已启动 (PID: $!, 日志: $LOG_FILE)"
