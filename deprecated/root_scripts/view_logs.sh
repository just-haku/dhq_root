#!/bin/bash

# Script to view different log files
echo "=== Log Viewer ==="
echo "1. Backend logs (including auto-order)"
echo "2. Frontend logs"
echo "3. History logs (sub-order actions)"
echo "4. SocketIO logs"
echo "5. Live tail backend logs"
echo "6. Live tail history logs"
echo ""
read -p "Choose an option (1-6): " choice

case $choice in
    1)
        echo "=== Backend Logs ==="
        tail -100 /home/haku/projects/DHQ_Root/logs/backend.log
        ;;
    2)
        echo "=== Frontend Logs ==="
        tail -100 /home/haku/projects/DHQ_Root/logs/frontend.log
        ;;
    3)
        echo "=== History Logs ==="
        if [ -f "/home/haku/projects/DHQ_Root/logs/history.log" ]; then
            tail -100 /home/haku/projects/DHQ_Root/logs/history.log
        else
            echo "History log file not found. It will be created when sub-orders are placed/deleted."
        fi
        ;;
    4)
        echo "=== SocketIO Logs ==="
        tail -100 /home/haku/projects/DHQ_Root/logs/socketio.log
        ;;
    5)
        echo "=== Live Backend Logs (Press Ctrl+C to stop) ==="
        tail -f /home/haku/projects/DHQ_Root/logs/backend.log | grep -E "(auto.*order|AUTO_ORDER|Processing order|Sub-order)"
        ;;
    6)
        echo "=== Live History Logs (Press Ctrl+C to stop) ==="
        if [ -f "/home/haku/projects/DHQ_Root/logs/history.log" ]; then
            tail -f /home/haku/projects/DHQ_Root/logs/history.log
        else
            echo "History log file not found. It will be created when sub-orders are placed/deleted."
        fi
        ;;
    *)
        echo "Invalid option"
        ;;
esac
