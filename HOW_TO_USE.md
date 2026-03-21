# 🚀 DHQ Digital Headquarters - How to Use Guide

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Service Management](#service-management)
4. [Testing & Validation](#testing--validation)
5. [Security Features](#security-features)
6. [API Documentation](#api-documentation)
7. [Troubleshooting](#troubleshooting)
8. [Development Guide](#development-guide)

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **MongoDB** (running on localhost:27017)
- **Redis** (running on localhost:6379)
- **Virtual Environment** for Python

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd DHQ_Root
   ```

2. **Setup Python Virtual Environment**
   ```bash
   python -m venv /home/haku/projects/venv/DHQ_Root
   source /home/haku/projects/venv/DHQ_Root/bin/activate
   cd backend
   pip install -r requirements.txt
   ```

3. **Setup Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

4. **Start All Services**
   ```bash
   ./dhq_manager.sh start
   ```

5. **Access the System**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

---

## 🏗️ System Overview

### Architecture
- **Frontend**: Vue.js 3 with Vite
- **Backend**: FastAPI with Python
- **Database**: MongoDB
- **Cache**: Redis
- **Real-time**: Socket.IO

### Key Features
- **🎯 KPI Bonus System**: Daily rewards with 30-day tracking
- **💾 Memory Allocation**: User storage management
- **📦 Stock Management**: Product inventory system
- **🤝 Collaboration**: Partner management system
- **🌱 Organic Growth**: Growth plan management
- **🔐 Security**: Hidden routes and OP authentication

---

## 🔧 Service Management

### Using the Unified Manager

The `dhq_manager.sh` script provides all-in-one management:

```bash
# Start all services
./dhq_manager.sh start

# Stop all services
./dhq_manager.sh stop

# Restart services
./dhq_manager.sh restart

# Check service status
./dhq_manager.sh status

# View logs
./dhq_manager.sh logs backend
./dhq_manager.sh logs frontend
./dhq_manager.sh logs all

# Health check
./dhq_manager.sh health

# Initialize OP user
./dhq_manager.sh init-op
```

### Service Ports
- **Frontend (Vue.js)**: Port 3000
- **Backend (FastAPI)**: Port 8000
- **Socket.IO Server**: Port 8001
- **MongoDB**: Port 27017
- **Redis**: Port 6379

---

## 🧪 Testing & Validation

### Comprehensive Testing Suite

```bash
# Run complete system test
./dhq_manager.sh test-complete

# Test login functionality
./dhq_manager.sh test-login

# Test dashboard loading
./dhq_manager.sh test-dashboard

# Run all tests
./dhq_manager.sh test-all
```

### Test Categories

1. **Service Health Check**
   - Frontend accessibility
   - Backend API health
   - Database connectivity

2. **Authentication Testing**
   - OP user login
   - Token verification
   - Session management

3. **API Functionality**
   - KPI Bonus system
   - Memory allocation
   - Stock management
   - Collaboration features

4. **Frontend Validation**
   - Component loading
   - Route accessibility
   - Asset compilation

---

## 🔒 Security Features

### Hidden Routes
- **Decoy Clock**: http://localhost:3000 (root route)
- **Hidden Login**: http://localhost:3000/shadow-garden/login
- **Hidden Register**: http://localhost:3000/shadow-garden/apply

### OP Authentication
- **Direct Login**: OP users bypass OTP
- **Secure Credentials**: Stored in `.env` file
- **Role-Based Access**: Different permissions for different user types

### Security Best Practices
1. **Keep OP credentials secure**
2. **Use HTTPS in production**
3. **Regular security audits**
4. **Monitor access logs**

---

## 📚 API Documentation

### Authentication Endpoints

#### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "kuro",
  "password": "your_secure_password"
}
```

#### Get Current User
```bash
GET /api/auth/me
Authorization: Bearer <token>
```

### KPI Bonus System

#### Get Daily Bonus
```bash
GET /api/kpi-bonus/daily-bonus
Authorization: Bearer <token>
```

#### Claim Daily Bonus
```bash
POST /api/kpi-bonus/claim-daily-bonus
Authorization: Bearer <token>
```

#### Get Bonus History
```bash
GET /api/kpi-bonus/bonus-history
Authorization: Bearer <token>
```

### Memory Management

#### Get Memory Allocations
```bash
GET /api/user/memory-allocations
Authorization: Bearer <token>
```

#### Allocate Memory
```bash
POST /api/user/memory-allocate
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "user",
  "memory_mb": 1024,
  "permissions": ["read", "write"]
}
```

### Stock Management

#### Get Shop Items
```bash
GET /api/vault-drive/shop/items-list
Authorization: Bearer <token>
```

#### Create Shop Item
```bash
POST /api/vault-drive/shop/create-item
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Product Name",
  "description": "Product Description",
  "price": 99.99,
  "quantity": 100
}
```

---

## 🔍 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check port availability
./dhq_manager.sh status

# Check logs for errors
./dhq_manager.sh logs backend
./dhq_manager.sh logs frontend

# Restart services
./dhq_manager.sh restart
```

#### Database Connection Issues
```bash
# Check MongoDB
mongosh --eval "db.adminCommand('ping')"

# Check Redis
redis-cli ping

# Restart database services
sudo systemctl restart mongod
sudo systemctl restart redis
```

#### Frontend Build Issues
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

#### Backend Import Issues
```bash
# Recreate virtual environment
rm -rf /home/haku/projects/venv/DHQ_Root
python -m venv /home/haku/projects/venv/DHQ_Root
source /home/haku/projects/venv/DHQ_Root/bin/activate
cd backend
pip install -r requirements.txt
```

### Log Locations
- **Backend Logs**: `logs/backend.log`
- **Frontend Logs**: `logs/frontend.log`
- **Socket.IO Logs**: `logs/socketio.log`

### Debug Mode
For detailed debugging, check the logs:
```bash
# Real-time log monitoring
./dhq_manager.sh logs backend
./dhq_manager.sh logs frontend
```

---

## 👨‍💻 Development Guide

### Project Structure
```
DHQ_Root/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── core/         # Core configuration
│   │   └── services/     # Business logic
│   ├── .env              # Environment variables
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # Vue components
│   │   ├── views/        # Page views
│   │   ├── router/       # Vue Router
│   │   ├── stores/       # Pinia stores
│   │   └── styles/       # CSS styles
│   ├── package.json      # Node dependencies
│   └── vite.config.js    # Vite configuration
├── logs/                 # Application logs
├── dhq_manager.sh       # Unified management script
└── HOW_TO_USE.md        # This guide
```

### Adding New Features

1. **Backend API**
   - Create new endpoint in `backend/app/api/`
   - Define models in `backend/app/models/`
   - Add business logic in `backend/app/services/`

2. **Frontend Component**
   - Create component in `frontend/src/components/`
   - Add route in `frontend/src/router/`
   - Create store in `frontend/src/stores/`

3. **Testing**
   - Add tests to the testing suite
   - Update API documentation
   - Test with `./dhq_manager.sh test-all`

### Environment Configuration

#### Backend (.env)
```env
SECRET_KEY=your_secret_key
AES_KEY=your_aes_key
MONGODB_URI=mongodb://localhost:27017/dhq
REDIS_URL=redis://localhost:6379
OP_INIT_USER=kuro
OP_INIT_PASS=your_secure_password
```

#### Frontend (vite.config.js)
```javascript
export default {
  server: {
    port: 3000
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
}
```

---

## 📞 Support & Contact

### Getting Help
1. **Check this guide first**
2. **Run diagnostic tests**: `./dhq_manager.sh test-all`
3. **Check logs**: `./dhq_manager.sh logs all`
4. **Review troubleshooting section**

### Contributing
1. **Fork the repository**
2. **Create feature branch**
3. **Test thoroughly**: `./dhq_manager.sh test-all`
4. **Submit pull request**

---

## 🎉 Conclusion

The DHQ Digital Headquarters is a comprehensive management system with:

- ✅ **Unified Management**: Single script for all operations
- ✅ **Comprehensive Testing**: Full test suite included
- ✅ **Security Features**: Hidden routes and OP authentication
- ✅ **Modern Stack**: Vue.js, FastAPI, MongoDB, Redis
- ✅ **Scalable Architecture**: Ready for production deployment

For any issues or questions, refer to this guide or run the diagnostic tools included in the system.

**🚀 Your DHQ system is ready to use!**
