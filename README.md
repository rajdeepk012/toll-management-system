# Toll Management System API

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)
![License](https://img.shields.io/badge/license-Educational-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Contributions](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)

A comprehensive toll plaza management system built with FastAPI and MySQL, demonstrating clean architecture principles, design patterns, and database integration.

## 📋 Overview

This project is a full-featured RESTful API for managing toll plazas, toll passes, and vehicle processing. It implements industry-standard design patterns and demonstrates the progression from in-memory storage to persistent MySQL database integration.

### Key Features

- **Pass Management**: Purchase and manage different types of toll passes (Single, Return, 7-Day)
- **Vehicle Processing**: Process vehicles passing through toll booths with automatic pass validation
- **Dynamic Pricing**: Different pricing for two-wheelers and four-wheelers
- **Validity Management**: Smart pass validity that starts from FIRST USE, not purchase time
- **Transaction Logging**: Append-only audit trail of all transactions
- **Leaderboard**: Real-time booth performance tracking (vehicles processed, revenue collected)
- **Data Persistence**: All data stored in MySQL database

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                  │
│              HTTP Endpoints + Request Validation         │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   Controller Layer                       │
│           HTTP → Business Logic Translation              │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                    System Layer                          │
│          Business Logic Orchestration                    │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼────────┐
│   Services   │ │Repositories│ │    Models    │
│  (Business)  │ │   (Data)   │ │  (Entities)  │
└──────────────┘ └─────┬──────┘ └──────────────┘
                       │
                ┌──────▼────────┐
                │ MySQL Database│
                └───────────────┘
```

### Design Patterns Used

1. **Repository Pattern**: Abstracts data access logic from business logic
2. **Service Layer Pattern**: Encapsulates business rules (pricing, validation, lifecycle)
3. **Dependency Injection**: Database sessions injected per request
4. **Strategy Pattern**: Different pass pricing strategies
5. **DTO Pattern**: Pydantic models for request/response validation

## 🛠️ Tech Stack

- **Framework**: FastAPI (modern, high-performance Python web framework)
- **Database**: MySQL (relational database for data persistence)
- **ORM**: SQLAlchemy 2.0 (Python SQL toolkit and ORM)
- **Database Driver**: PyMySQL (pure Python MySQL client)
- **Validation**: Pydantic (data validation using Python type hints)
- **Server**: Uvicorn (ASGI server)

## 📊 Database Schema

### Tables

**tolls** - Toll plaza information
```sql
- id (PK, auto-increment)
- toll_id (unique business ID)
- name
- location
```

**toll_booths** - Individual toll gates at each plaza
```sql
- id (PK, auto-increment)
- booth_id (business ID)
- toll_id (FK → tolls)
- name
- vehicles_processed (counter)
- total_charges_collected (revenue)
```

**vehicles** - Registered vehicles
```sql
- id (PK, auto-increment)
- registration_number (unique)
- vehicle_type (two_wheeler/four_wheeler)
```

**toll_passes** - Purchased passes
```sql
- id (PK, auto-increment)
- pass_id (unique business ID)
- vehicle_reg (FK → vehicles)
- toll_id (FK → tolls)
- pass_type (single/return/seven_day)
- purchased_at
- first_used_at (nullable - set on first use!)
- valid_until (nullable - set on first use!)
- uses_remaining
- status (active/expired/exhausted)
```

**transactions** - Audit log (append-only)
```sql
- id (PK, auto-increment)
- transaction_id (unique business ID)
- booth_id
- toll_id
- vehicle_reg
- transaction_type (purchase/passage)
- pass_id
- amount
- timestamp
```

## 🚀 Installation

### Prerequisites

- Python 3.10+
- MySQL Server 8.0+
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/rajdeepk012/toll-management-system.git
cd toll-management-system
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up MySQL Database

1. Start MySQL server
2. Create database:

```sql
CREATE DATABASE toll_management;
```

3. Update database credentials in `database/config.py` if needed:

```python
DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/toll_management"
```

### Step 4: Create Database Tables

```bash
python3 database/create_tables.py
```

You should see output confirming table creation:
```
Creating tables in MySQL...
✓ Tables created successfully!
```

## ▶️ Running the Application

### Start the API Server

```bash
python3 main_api.py
```

You should see:
```
================================================================================
  Toll Management System API Starting...
================================================================================
  ✓ Found existing data in MySQL (2 tolls)
  ✓ Skipping test data initialization

  API is ready! Visit http://localhost:8000/docs for interactive documentation
================================================================================
```

### Access the API

- **Interactive Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

## 📡 API Endpoints

### 1. Get Pass Options

Get available pass types and pricing for a vehicle type.

**Request:**
```bash
GET /api/pass/options?vehicle_type=two_wheeler
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "vehicle_type": "two_wheeler",
    "options": [
      {
        "pass_type": "single",
        "price": 50,
        "duration": "1 hour",
        "uses": 1,
        "description": "Single journey pass, valid for 1 use"
      },
      {
        "pass_type": "return",
        "price": 80,
        "duration": "24 hours",
        "uses": 2,
        "description": "Return journey pass, valid for 2 uses"
      },
      {
        "pass_type": "seven_day",
        "price": 250,
        "duration": "7 days",
        "uses": 999999,
        "description": "Weekly pass, unlimited uses for 7 days"
      }
    ]
  }
}
```

### 2. Purchase Pass

Purchase a toll pass for a vehicle.

**Request:**
```bash
POST /api/pass/purchase
Content-Type: application/json

{
  "vehicle_reg": "MH-12-AB-1234",
  "toll_id": "T1",
  "booth_id": "B1",
  "pass_type": "return"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "pass_id": "PASS-0001",
    "vehicle_reg": "MH-12-AB-1234",
    "toll_id": "T1",
    "pass_type": "return",
    "price": 80,
    "purchased_at": "2025-12-25 10:49:39",
    "uses_remaining": 2,
    "status": "active"
  },
  "message": "Pass PASS-0001 purchased successfully"
}
```

### 3. Process Vehicle Passage

Process a vehicle passing through a toll booth.

**Request:**
```bash
POST /api/vehicle/process
Content-Type: application/json

{
  "vehicle_reg": "MH-12-AB-1234",
  "toll_id": "T1",
  "booth_id": "B1"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "allowed": true,
    "message": "Passage allowed",
    "pass_info": {
      "pass_id": "PASS-0001",
      "pass_type": "return",
      "status": "active",
      "valid_until": "2025-12-26 11:21:02",
      "uses_remaining": 1
    }
  }
}
```

**Response (Denied - No Pass):**
```json
{
  "status": "success",
  "data": {
    "allowed": false,
    "message": "No valid pass found for this toll",
    "pass_options": [...]
  }
}
```

### 4. Get Leaderboard

Get booth performance rankings.

**Request:**
```bash
GET /api/leaderboard?metric=total_charges_collected
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "metric": "total_charges_collected",
    "total_booths": 5,
    "leaderboard": [
      {
        "rank": 1,
        "toll_id": "T1",
        "toll_name": "Mumbai-Pune Expressway Toll",
        "booth_id": "B1",
        "vehicles_processed": 10,
        "total_charges_collected": 450
      }
    ]
  }
}
```

## 📁 Project Structure

```
toll_management_learning/
│
├── main_api.py                 # Application entry point
├── api.py                      # FastAPI routes and endpoints
├── system.py                   # Business logic orchestration
├── models.py                   # Domain models (entities)
├── requirements.txt            # Python dependencies
│
├── controllers/                # HTTP request handlers
│   ├── __init__.py
│   ├── pass_controller.py
│   ├── vehicle_controller.py
│   └── leaderboard_controller.py
│
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── pass_pricing_service.py
│   ├── pass_validation_service.py
│   └── pass_lifecycle_service.py
│
├── repositories/               # Data access layer
│   ├── __init__.py
│   ├── pass_repository_mysql.py
│   ├── vehicle_repository_mysql.py
│   ├── transaction_repository_mysql.py
│   └── toll_repository_mysql.py
│
└── database/                   # Database configuration
    ├── __init__.py
    ├── config.py              # Database connection setup
    ├── db_models.py           # SQLAlchemy ORM models
    ├── converters.py          # Domain ↔ Database model converters
    └── create_tables.py       # Database migration script
```

## 🎯 Key Concepts Demonstrated

### 1. **Pass Validity Bug Fix**

**Problem**: If a return pass is valid for 24 hours, should the timer start from purchase time or first use?

**Solution**: Validity starts from **FIRST USE**, not purchase time.

```python
# Purchase at 10:00 AM
pass = purchase_pass(vehicle, toll, "return")  # purchased_at = 10:00 AM
                                                # first_used_at = None
                                                # valid_until = None

# First use at 2:00 PM (4 hours later)
process_vehicle(vehicle, toll)  # first_used_at = 2:00 PM
                                # valid_until = 2:00 PM + 24 hours

# Pass valid until next day 2:00 PM, not 10:00 AM!
```

### 2. **Repository Pattern**

Separates data access from business logic:

```python
# System doesn't know about SQL - it just calls repository methods
toll_pass = self.pass_repo.get_pass(pass_id)

# Repository handles all MySQL queries
class PassRepository:
    def get_pass(self, pass_id):
        db_pass = self.db.query(TollPassDB).filter_by(pass_id=pass_id).first()
        return db_to_toll_pass(db_pass)  # Convert to domain model
```

### 3. **Dependency Injection**

Fresh database session per HTTP request:

```python
# FastAPI creates new session for each request
@app.post("/api/pass/purchase")
def purchase_pass(
    request: PurchasePassRequest,
    system: TollManagementSystem = Depends(get_system)  # ← Injected!
):
    # Each request gets its own system with fresh DB session
    result = system.purchase_pass(...)
```

### 4. **Domain vs Database Models**

Two types of models for separation of concerns:

```python
# Domain Model (business logic uses this)
@dataclass
class TollPass:
    pass_id: str
    vehicle_reg: str
    pass_type: PassType  # Enum
    # ... business logic fields

# Database Model (SQLAlchemy ORM)
class TollPassDB(Base):
    __tablename__ = "toll_passes"
    id = Column(Integer, primary_key=True)  # Technical ID
    pass_id = Column(String(50), unique=True)  # Business ID
    pass_type = Column(SQLEnum(PassTypeDB))  # DB Enum
    # ... database-specific fields
```

## 🧪 Testing the System

### Manual Testing with cURL

**1. Check available passes:**
```bash
curl "http://localhost:8000/api/pass/options?vehicle_type=four_wheeler"
```

**2. Purchase a pass:**
```bash
curl -X POST "http://localhost:8000/api/pass/purchase" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_reg": "MH-14-CD-5678",
    "toll_id": "T1",
    "booth_id": "B1",
    "pass_type": "seven_day"
  }'
```

**3. Process vehicle (first use):**
```bash
curl -X POST "http://localhost:8000/api/vehicle/process" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_reg": "MH-14-CD-5678",
    "toll_id": "T1",
    "booth_id": "B1"
  }'
```

**4. Check leaderboard:**
```bash
curl "http://localhost:8000/api/leaderboard?metric=vehicles_processed"
```

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint to expand
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. View response

## 🔧 Configuration

### Database Configuration

Edit `database/config.py` to change database settings:

```python
DATABASE_URL = "mysql+pymysql://username:password@host:port/database"

# Example for different host:
DATABASE_URL = "mysql+pymysql://root:mypassword@192.168.1.100:3306/toll_management"
```

### Pricing Configuration

Edit `services/pass_pricing_service.py` to modify pricing:

```python
# Two-wheeler pricing
PassType.SINGLE: 50,      # ₹50 for single journey
PassType.RETURN: 80,      # ₹80 for return journey
PassType.SEVEN_DAY: 250,  # ₹250 for 7-day pass

# Four-wheeler pricing
PassType.SINGLE: 100,
PassType.RETURN: 150,
PassType.SEVEN_DAY: 500,
```

## 🐛 Known Limitations

1. **ID Generation**: Uses in-memory counters (loads from DB count). In production, use database auto-increment or UUID.
2. **Concurrency**: No transaction locking for concurrent requests. In production, add optimistic/pessimistic locking.
3. **Authentication**: No user authentication or API keys. Add JWT/OAuth2 for production.
4. **Rate Limiting**: No request throttling. Add rate limiting middleware for production.
5. **Error Handling**: Basic error responses. Add comprehensive error codes and logging.

## 🚀 Future Enhancements

- [ ] Add user authentication (JWT tokens)
- [ ] Implement payment gateway integration
- [ ] Add email notifications for pass expiry
- [ ] Create admin dashboard
- [ ] Add comprehensive test suite (pytest)
- [ ] Implement caching (Redis) for frequently accessed data
- [ ] Add Docker support for easy deployment
- [ ] Create CI/CD pipeline
- [ ] Add monitoring and logging (Prometheus, Grafana)
- [ ] Implement WebSocket for real-time booth updates

## 📝 License

This project is created for educational purposes. Feel free to use it as a learning resource or starting point for your own projects.

## 🤝 Contributing

This is a learning project, but suggestions and improvements are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or feedback about this project, please open an issue on GitHub.

---

**Built for learning Clean Architecture, Design Patterns, and Database Integration**
