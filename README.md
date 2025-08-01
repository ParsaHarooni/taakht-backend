# Taakht Backend - Item-to-Item Trading Platform

A FastAPI-based backend service for the Taakht Item-to-Item Trading Platform.

## 🚀 Development Task List

### ✅ **Completed Tasks**
- **Phase 1.1**: Project Setup & Foundation ✅
  - Environment configuration with Pydantic Settings
  - Database configuration for SQLite/PostgreSQL
  - Comprehensive logging system
  - CORS middleware setup
  - Environment file templates
  - Docker and Docker Compose setup

- **Phase 1.2**: Database Models & Migrations ✅
  - User model with authentication fields, profile data, and statistics
  - Item model for trading items with comprehensive details and location
  - Trade model for item exchanges with multi-item support and counter offers
  - Category model for hierarchical item organization
  - ItemImage model for media storage with metadata and processing
  - TradeItem model for managing items within trades
  - Tortoise ORM integration with proper relationships and indexes

- **Phase 1.3**: Authentication & Authorization ✅
  - JWT token authentication with access and refresh tokens
  - User registration and login endpoints
  - Password hashing with bcrypt
  - Password reset functionality (placeholder for email)
  - Authentication middleware and dependencies
  - Role-based access control (RBAC) with comprehensive permission system

- **Phase 2.1**: User Management API ✅
  - User registration and authentication endpoints
  - Profile management (get, update, preferences)
  - User statistics and activity tracking
  - User search and filtering with pagination
  - Public user profiles and items
  - Account management (deactivate, delete)

### 🔄 **Current Progress**
- **Phase 1.3**: Authentication & Authorization ✅
- **Phase 2.1**: User Management API ✅
- **Phase 2.2**: Item Management API ✅
  - Item CRUD operations with comprehensive validation
  - Advanced search and filtering with location-based search
  - Item statistics and analytics
  - Bulk operations for admin/moderators
  - Item duplication and status management
  - Category-based item browsing
  - Location-based nearby item search
  - View tracking and engagement metrics
- **Phase 2.3**: Category Management API (Pending)
- **Phase 2.4**: RBAC Management API ✅
- **Phase 3**: Trading System (Pending)

### **Phase 1: Project Setup & Foundation**
- [x] **1.1** Set up proper project structure and configuration
  - [x] Create `src/config/settings.py` with environment variables
  - [x] Set up database configuration (PostgreSQL/SQLite for development)
  - [x] Configure logging system
  - [x] Set up CORS middleware
  - [x] Create `.env.example` file

- [x] **1.2** Database Models & Migrations
  - [x] Create User model (id, username, email, password_hash, created_at, updated_at)
  - [x] Create Item model (id, title, description, condition, category, images, owner_id, created_at, updated_at)
  - [x] Create Trade model (id, initiator_id, recipient_id, initiator_items, recipient_items, status, created_at, updated_at)
  - [x] Create Category model (id, name, description, parent_id)
  - [x] Create ItemImage model (id, item_id, image_url, is_primary)
  - [x] Set up Tortoise ORM migrations

- [x] **1.3** Authentication & Authorization
  - [x] Implement JWT token authentication
  - [x] Create user registration endpoint
  - [x] Create user login endpoint
  - [x] Create password reset functionality
  - [x] Set up authentication middleware
  - [x] Implement role-based access control

### **Phase 2: Core API Endpoints**
- [x] **2.1** User Management
  - [x] GET `/api/users/me` - Get current user profile
  - [x] PUT `/api/users/me` - Update user profile
  - [x] GET `/api/users/{user_id}` - Get public user profile
  - [x] GET `/api/users/{user_id}/items` - Get user's items

- [ ] **2.2** Item Management
  - [ ] POST `/api/items` - Create new item listing
  - [ ] GET `/api/items` - List all items (with filters)
  - [ ] GET `/api/items/{item_id}` - Get item details
  - [ ] PUT `/api/items/{item_id}` - Update item
  - [ ] DELETE `/api/items/{item_id}` - Delete item
  - [ ] POST `/api/items/{item_id}/images` - Upload item images
  - [ ] DELETE `/api/items/{item_id}/images/{image_id}` - Delete item image

- [ ] **2.3** Category Management
  - [ ] GET `/api/categories` - List all categories
  - [ ] GET `/api/categories/{category_id}` - Get category details
  - [ ] GET `/api/categories/{category_id}/items` - Get items in category

### **Phase 3: Trading System**
- [ ] **3.1** Trade Management
  - [ ] POST `/api/trades` - Initiate a trade
  - [ ] GET `/api/trades` - List user's trades (sent/received)
  - [ ] GET `/api/trades/{trade_id}` - Get trade details
  - [ ] PUT `/api/trades/{trade_id}/accept` - Accept trade
  - [ ] PUT `/api/trades/{trade_id}/reject` - Reject trade
  - [ ] PUT `/api/trades/{trade_id}/cancel` - Cancel trade
  - [ ] PUT `/api/trades/{trade_id}/counter` - Counter offer

- [ ] **3.2** Trade Notifications
  - [ ] Implement real-time notifications for trade updates
  - [ ] Create notification model and endpoints
  - [ ] Set up WebSocket connections for live updates

### **Phase 4: Search & Discovery**
- [ ] **4.1** Search Functionality
  - [ ] Implement full-text search for items
  - [ ] Add filters (category, condition, location, price range)
  - [ ] Implement pagination for search results
  - [ ] Add sorting options (newest, oldest, most relevant)

- [ ] **4.2** Recommendation System
  - [ ] Implement basic item recommendations
  - [ ] Suggest similar items
  - [ ] Recommend potential trade matches

### **Phase 5: Advanced Features**
- [ ] **5.1** Messaging System
  - [ ] Create Message model
  - [ ] Implement direct messaging between users
  - [ ] Add message notifications
  - [ ] Create conversation management

- [ ] **5.2** Rating & Reviews
  - [ ] Create Rating model
  - [ ] Implement user rating system
  - [ ] Add review functionality for completed trades
  - [ ] Calculate user reputation scores

- [ ] **5.3** Location Services
  - [ ] Add location-based search
  - [ ] Implement distance calculation
  - [ ] Add location preferences for users

### **Phase 6: Security & Performance**
- [ ] **6.1** Security Enhancements
  - [ ] Implement rate limiting
  - [ ] Add input validation and sanitization
  - [ ] Set up API key management
  - [ ] Implement request logging
  - [ ] Add security headers

- [ ] **6.2** Performance Optimization
  - [ ] Implement caching (Redis)
  - [ ] Add database query optimization
  - [ ] Implement image compression and CDN
  - [ ] Add API response compression

### **Phase 7: Testing & Documentation**
- [ ] **7.1** Testing
  - [ ] Write unit tests for all models
  - [ ] Write integration tests for API endpoints
  - [ ] Set up test database
  - [ ] Implement CI/CD pipeline

- [ ] **7.2** Documentation
  - [ ] Create comprehensive API documentation
  - [ ] Add OpenAPI/Swagger documentation
  - [ ] Create deployment guide
  - [ ] Write user guide for API consumers

### **Phase 8: Deployment & DevOps**
- [ ] **8.1** Deployment Setup
  - [ ] Create Docker configuration
  - [ ] Set up production database
  - [ ] Configure environment variables
  - [ ] Set up monitoring and logging

- [ ] **8.2** Infrastructure
  - [ ] Set up load balancer
  - [ ] Configure SSL certificates
  - [ ] Set up backup systems
  - [ ] Implement health checks

## 📋 Priority Order for MVP:
1. **Phase 1** - Foundation ✅ (Essential for everything else)
   - ✅ 1.1 Project Setup & Configuration
   - ✅ 1.2 Database Models & Migrations
   - 🔄 1.3 Authentication & Authorization (Next)
2. **Phase 2** - Core API (Basic functionality)
3. **Phase 3** - Trading System (Core business logic)
4. **Phase 4** - Search (User experience)
5. **Phase 5** - Advanced Features (Enhancement)
6. **Phase 6-8** - Production readiness

## ⏱️ Estimated Timeline:
- **MVP (Phases 1-4)**: 4-6 weeks
- **Full Platform (All Phases)**: 8-12 weeks

## 🛠️ Tech Stack
- **Framework**: FastAPI
- **ORM**: Tortoise ORM
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: JWT
- **Python Version**: >=3.11

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- uv (package manager)
- Docker & Docker Compose (optional, for containerized setup)

### Quick Start (Development)

#### Option 1: Local Development
```bash
# Clone the repository
git clone <repository-url>
cd taakht-backend

# Setup environment
python scripts/setup_env.py

# Install dependencies
uv sync

# Run the development server
uv run python main.py
```

#### Option 2: Docker Development
```bash
# Clone the repository
git clone <repository-url>
cd taakht-backend

# Start all services (including PostgreSQL and Redis)
docker-compose up -d

# View logs
docker-compose logs -f taakht-backend
```

### Environment Configuration

The application supports three environments:

#### Development
- Uses SQLite database
- Debug mode enabled
- Detailed logging
- CORS allows localhost origins

#### Production
- Uses PostgreSQL database
- Debug mode disabled
- Minimal logging
- Strict CORS settings
- Rate limiting enabled

#### Test
- Uses SQLite test database
- Debug mode enabled
- Error-level logging only

### Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Core settings
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=sqlite://./taakht_dev.db  # Development
# DATABASE_URL=postgresql://user:pass@localhost:5432/taakht_db  # Production

# Security
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379/0

# Optional: Email settings
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Database Setup

#### Development (SQLite)
- Automatically created on first run
- No additional setup required

#### Production (PostgreSQL)
```bash
# Using Docker
docker-compose up postgres -d

# Or install PostgreSQL locally
# Create database and user
createdb taakht_db
createuser taakht_user
```

### API Documentation

Once the server is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 📝 License
This project is licensed under the MIT License.
