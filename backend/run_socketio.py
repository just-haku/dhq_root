#!/usr/bin/env python3
import os
import sys
sys.path.append('/home/haku/projects/DHQ_Root/backend')

from app.socketio_server import socket_app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8001)
