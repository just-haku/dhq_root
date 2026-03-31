# DHQ Settings & Configuration

## Environment Variables

### Backend (`backend/.env`)
The backend requires several configuration parameters supplied via environment variables. Create a `.env` in the `backend/` directory if missing:

```env
# Database
MONGO_URI=mongodb://localhost:27017/dhq_db
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_cryptographic_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Server Binding
HOST=0.0.0.0
PORT=8000

# Stealth Mode Routes
REAL_LOGIN_ROUTE=/shadow-garden/login
REAL_REGISTER_ROUTE=/shadow-garden/apply
```

### Frontend (`frontend/.env`)
The frontend leverages Vite environment variables:
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

## System Dependencies
- **Docker**: Optional, for containerizing the backend and Redis/Mongo services.
- **Node.js**: >= 18.0.0 required to build and serve the Vue application.
- **Python**: >= 3.10.x to leverage recent FastAPI features and type hinting syntax.

## Application Settings

### Theming and UI Modes
- Users can customize the application's appearance (e.g., `dark`, `light` themes) via the UI button (`.theme-toggle-btn`) in `App.vue`. These cascade via CSS custom variables (`data-theme`) and update both `localStorage` and the database.

### Role-Based Features
Administrators can tweak system settings inside the application using the `OperatorSettings` and various Admin dashboards. These allow on-the-fly toggling of certain services without tearing down the server:
- System Task Scheduler (`AdminTasks.vue`)
- Users Management (`AdminUsers.vue`)
- Access Control to logs, monitoring, caching, and database (`AdminSystem.vue`)

### File Management
The backend creates `uploads/avatars` and `uploads/banners` implicitly mapped to `/api/uploads` static dir. Ensure the application has read/write permissions to this subdirectory to support user image uploads.
