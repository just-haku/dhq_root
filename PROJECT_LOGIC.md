# Project Logic & Functions

## Core Architecture
The system employs a client-server architecture with Vue3 on the frontend communicating via REST APIs and WebSockets to the Python/FastAPI backend.

### 1. Stealth Mode & Routing Logic
- **Unauthenticated State**: Visitors to the root domain (`/`) see a benign interface like an advanced clock or decoy blog.
- **Secret Portal**: Authorized users must navigate to a hidden route (e.g., `/shadow-garden/login`) to access the real login portal.
- **Route Guards**: `vue-router` intercepts all navigation in `router/index.js`. Routes with `meta: { requiresAuth: true }` redirect unauthenticated users to `/`. Routes with `requiresAdmin: true` check the user's role (AD/OP) before allowing access.

### 2. User & Role Management
- Users have distinct roles: Admin (`AD`), Operator (`OP`), Member/User.
- Authentication relies on short-lived JWTs stored locally.
- Appearance preferences (themes like `dark`/`light`) are saved both in `localStorage` and synced with the backend via `apiPatch('/user/appearance')`.

### 3. Application Modules

#### Order Center & Economy
- Facilitates creating, browsing, and managing internal or external orders. Features bulk checkout, order status assignment, and cart functionalities.
- The backend processes these through asynchronous workers (`order_center_worker`) and integrates with KPI tracking and bonus distributions (`kpi-bonus`).

#### Arcade Subsystem
- **Games Module**: Includes distinct endpoints (`/api/games/*`) mapping to dedicated game engines (Blackjack, Bovo, Wordle, etc.).
- **Socket.IO Integration**: Used for real-time multiplayer coordination (e.g., TicTacToe) or pushing game events securely.
- **Economy Tie-in**: Features a daily gift/login reward system acting as retention mechanics, tracking streaks in the database.

#### G-Code Generator
- Converts image or SVG inputs to machine-readable G-code.
- Backend logic orchestrates OpenCV for image processing, Potrace for vectorization, and SVG path parsing (`svgpathtools`) to construct optimal CNC pen movements. Includes path optimization logic to reduce unnecessary movements.

#### Administrative & Monitoring Tools
- **Background Tasks**: Celery and Redis manage intensive tasks like file conversion or broadcasting emails (`email_watcher`).
- **Data Maintenance**: Includes endpoints for database backups, audit logging, and cache management. Large file uploads are protected by a `LargeFileUploadMiddleware` restricting payloads based on memory limits.
