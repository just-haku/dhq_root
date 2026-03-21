Luckfox Pico Ultra: Collaboration & Task Server

Project Status: Alpha / Development

1. Project Overview

We have built a Modular Flask-based Web Server designed to run on an embedded Linux device (Luckfox Pico Ultra). It serves as a Collaboration & Task Management System with a covert "Clock" landing page to mask its true purpose.

Core Purpose: Manage collaboration orders (social media services), media sharing, and team tasks.

Target Hardware: Luckfox Pico Ultra (Rockchip RV1106).

OS Environment: Embedded Linux (Ubuntu/Debian based).

Network Context: LAN accessible (e.g., 192.168.1.x).

2. Technical Architecture

Backend Framework: Python (Flask)

Database: SQLite (Persistent storage at /home/haku/usb/db/server.db)

Web Server: Nginx (Reverse Proxy) + Gunicorn (WSGI)

Frontend: HTML5, Bootstrap 5, JavaScript (Fetch API), Chart.js

Storage: USB Drive (/home/haku/usb)

Key System Features:

Modular Blueprints: Code is split into auth, dashboard, media, orders, admin, clock.

External Venv: Python environment stored at ../kuro.

Zero-Copy Streaming: Large media files served directly by Nginx.

3. Features Implemented

A. Security & Access Control

Covert Entry: Homepage is a functional Clock (app/blueprints/clock.py).

Secret Login: Located at /secret-kuro-grp.

RBAC (Role-Based Access Control):

Operator (kuro): Hardcoded God-mode (Cannot be banned).

Admin: Manage users/groups.

User: Standard access.

Permissions: JSON-based permission matrix (e.g., media_delete, user_ban).

B. Order Management System

Order Entry: Inputs for Link, Service ID, Quantity, Duration, Tolerance, Step.

"Crooked" Algorithm: app/utils.py generates non-linear growth curves.

Preview: Chart.js visualization of the growth curve before submission.

Management: Table view of active vs. deleted orders.

API: Integration structure for tangtuongtacre.com.

C. Media Gallery

Storage: /home/haku/usb/images & /videos.

UI: Grid view, lazy loading.

Uploads: Floating widget, supports large files (chunked by Nginx).

Lightbox: detailed view with Zoom, Comments, and Reactions.

Privacy: Visibility toggles (Public/Private/Shared with specific Users).

D. Admin & User Tools

Navigation: Offcanvas sidebar.

Tasks: Assign tasks to users, toggle status.

Groups: Create user groups with inherited permissions.

Settings: Profile management (Avatar, Bio, Password).

Theme: Dark/Light mode toggle.

4. Current Gaps (Next Steps)

Chat Module:

Current State: ChatMessage model exists in database. Dashboard fetches "recent chat".

Missing: Frontend UI and Polling/WebSocket logic.

Bug Reporting: Menu link exists, but no route/template implemented.

API Error Handling: Network timeouts and specific API error codes need robust catching in orders.py.

Mobile Optimization: Touch targets need verification on the actual Luckfox device.

5. Operational Checklist

Database Reset (Critical)
If models.py changes, the DB must be flushed because we are not using Alembic migrations yet.

rm /home/haku/usb/db/server.db
# Restart server to trigger db.create_all()


Permissions Fix
If you encounter "500 Error" on upload or "403" on view:

sudo chown -R haku:haku /home/haku/usb
sudo chmod 755 /home/haku/usb


Nginx Config
Static paths for media streaming:

location /stream/ {
    alias /home/haku/usb/;
    autoindex off;
}
