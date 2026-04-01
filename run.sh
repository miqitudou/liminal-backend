#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
PID_FILE="$PROJECT_DIR/backend.pid"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/backend.log"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "未找到虚拟环境 Python: $VENV_PYTHON"
  exit 1
fi

if [ -f "$PID_FILE" ]; then
  EXISTING_PID="$(cat "$PID_FILE")"
  if [ -n "$EXISTING_PID" ] && kill -0 "$EXISTING_PID" 2>/dev/null; then
    echo "backend 已在运行，PID: $EXISTING_PID"
    exit 0
  fi

  echo "发现失效的 PID 文件，已自动清理"
  rm -f "$PID_FILE"
fi

mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"

echo "开始拉取最新代码..."
git pull

nohup "$VENV_PYTHON" -m uvicorn app.main:app --host "$HOST" --port "$PORT" >> "$LOG_FILE" 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"

sleep 1

if kill -0 "$PID" 2>/dev/null; then
  echo "backend 启动成功"
  echo "PID: $PID"
  echo "日志: $LOG_FILE"
  echo "地址: http://$HOST:$PORT"
  exit 0
fi

echo "backend 启动失败，请查看日志: $LOG_FILE"
rm -f "$PID_FILE"
exit 1
