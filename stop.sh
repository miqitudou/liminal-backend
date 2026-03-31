#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$PROJECT_DIR/backend.pid"
WAIT_SECONDS="${WAIT_SECONDS:-10}"

if [ ! -f "$PID_FILE" ]; then
  echo "未找到 PID 文件，backend 可能没有运行"
  exit 0
fi

PID="$(cat "$PID_FILE")"

if [ -z "$PID" ]; then
  echo "PID 文件为空，已清理"
  rm -f "$PID_FILE"
  exit 0
fi

if ! kill -0 "$PID" 2>/dev/null; then
  echo "进程不存在，已清理 PID 文件"
  rm -f "$PID_FILE"
  exit 0
fi

kill "$PID"

for _ in $(seq "$WAIT_SECONDS"); do
  if ! kill -0 "$PID" 2>/dev/null; then
    rm -f "$PID_FILE"
    echo "backend 已停止"
    exit 0
  fi

  sleep 1
done

echo "等待超时，执行强制停止"
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"
echo "backend 已强制停止"
