# FastAPI Starter Kit 🚀

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/) [![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT) [![PyPI Version](https://img.shields.io/pypi/v/fastapi-starter-kit.svg)](https://pypi.org/project/fastapi-starter-kit/)

**FastAPI Starter Kit** is a production-ready starter template for building FastAPI projects with authentication, role-based access, and pre-configured boilerplate code. It helps developers quickly bootstrap a FastAPI project following best practices.

---

## 🌟 Features

- **Authentication & Authorization**
  - JWT authentication (login/logout, token refresh)
  - User registration with hashed passwords
  - Basic role-based access control
- **Database**
  - SQLAlchemy ORM integration
  - Alembic migrations
- **Project Structure**
  - Modular with `routers`, `services`, `models`, and `schemas`
  - Pre-configured middleware for exception logging
  - Dependency management via `dependencies.py`
- **Utilities**
  - Token generation and validation
  - Password utilities
  - Notification and email service hooks
- **Development-ready**
  - `.env` configuration
  - Logging setup (`logs/app.log`)
  - Test setup with `pytest`

---

## ⚡ Getting Started

### 1. Install the package

```bash
pip install fastapi-starter-kit
```

### 2. Create a new project
- This command scaffolds the project structure with all necessary folders, files, and initial configuration.
```bash
fastapi-starter <project_name>
cd <project_name>
```

### 3. Install project dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
A default `.env` file is automatically created when you generate the project.

It includes basic application, database, JWT, and logging configuration such as:

```dotenv
APP_NAME=FastAPI Starter Pack
APP_DESCRIPTION=A well-structured FastAPI starter with JWT auth
APP_VERSION=1.0.0
DEBUG=True

# Database
DATABASE_URL=sqlite:///./app.db

# JWT Settings
JWT_SECRET_KEY=<your_secret_key_here>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=1440  # 24H

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

LOGIN_URL=/auth/login
```

### 5. Initialize the database
```bash
alembic upgrade head
```

### 6. Run the application
Option: 1
```bash
python main.py
```
Option: 2
```bash
uvicorn main:app --reload
```

Your API will be available at http://127.0.0.1:8000.


## 🏗️ Project Structure
```bash
project_a/
├── app/
│   ├── api/
│   ├── auth/
│   ├── core/
│   ├── external_services/
│   ├── middleware/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   └── utils/
├── main.py
├── app.db
├── migrations/
├── logs/
├── .env
└── tests/
```


## 🛠️ Contributing

Contributions, bug reports, and feature requests are welcome!
Please follow these steps:
1. Fork the repository
2. Create a new branch for your feature/fix
3. Make your changes
4. Write tests if applicable
5. Submit a pull request


## 📜 License
This project is licensed under the **MIT License**. See the [LICENSE](https://github.com/jay0311-dev/fastapi-starter-kit/blob/release/LICENSE) file for details.


## 💡 Notes

- Designed for rapid project setup with authentication and role-based access
- Easily extensible to include more modules, APIs, and services
- Logging, database, and middleware are pre-configured for best practices