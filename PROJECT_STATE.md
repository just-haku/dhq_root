# DHQ Project State

## Overview
DHQ is a full-stack web application designed with a "stealth mode" interface. When unauthenticated users visit the root page, they are presented with a simple clock (or decoy landing page), while the real application is hidden behind secret routes (`/shadow-garden/login`). The system features a wide array of tools ranging from productivity and order management to games and utility applications.

## Technology Stack

### Frontend
- **Framework**: Vue.js 3 with Composition API
- **Build Tool**: Vite
- **State Management**: Pinia
- **Styling**: Tailwind CSS
- **Routing**: Vue Router
- **Additional Libraries**: Chart.js (Analytics), Socket.io-client (Real-time updates), Cropper.js (Image manipulation)

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB (via `mongoengine`)
- **Caching & Job Queue**: Redis & Celery
- **Real-time Communication**: python-socketio
- **Security**: JWT tokens (`python-jose`), `passlib` (bcrypt)
- **Utilities**: OpenCV, Pillow (Image Processing), `svgpathtools`, PyMuPDF (PDF handling), numpy, scipy

## Current System Capabilities
- **Authentication & Security**: JWT-based login, role-based access control (Admin, Operator, User), stealth routing.
- **Order Center / Marketplace**: E-commerce or internal resource ordering system including creating and managing orders, cart features.
- **Arcade & Gaming Hub**: Multiplayer and single-player games including Wordle, Typing Test, Memory, TicTacToe, Bovo, Blackjack, and BigTwo. Includes a Daily Gifts system.
- **Utility Tools**: G-Code generator for converting SVG/images to CNC machine instructions, Drive (file storage), Virus Scan endpoint.
- **Communication & Collaboration**: Email Hub, Convo Hub, Smart Collaboration, and Prompts management.
- **Admin & Monitoring**: Extensive admin dashboards for Users, Tasks, System stats, Analytics, Server Settings, Backups, and Audit logging.

## Architectural State
- The frontend uses a scalable layout system (`DashboardLayout.vue`), relying on distinct views mapped within `router/index.js`.
- The backend serves RESTful APIs built on FastAPI routers mapped in `main.py`, separated logically by domain (e.g., `auth.py`, `arcade.py`, `ordering.py`).
- Real-time updates utilize the integrated Socket.IO server within the FastAPI lifecycle.
- Large file uploads are managed via custom middleware ensuring scale limits. Async workers (Order Center, Cache, Email Watchers) are managed in the FastAPI lifespan.
