#!/bin/bash
# DHQ Backend Restart Script
echo "Stopping stale backend process (PID 1425006)..."
kill -9 1425006 2>/dev/null
sleep 2

# Find any other process on port 8000
OTHER_PID=$(lsof -t -i :8000)
if [ ! -z "$OTHER_PID" ]; then
  echo "Killing other process on port 8000 (PID $OTHER_PID)..."
  kill -9 $OTHER_PID
fi

echo "Starting updated backend..."
cd /home/haku/projects/DHQ_Root/backend
nohup env PYTHONPATH=. /home/haku/projects/venv/DHQ_Root/bin/python -m app.main > backend.log 2>&1 &
echo "Backend started in background. Logs available in backend.log"
ps -fp $!
