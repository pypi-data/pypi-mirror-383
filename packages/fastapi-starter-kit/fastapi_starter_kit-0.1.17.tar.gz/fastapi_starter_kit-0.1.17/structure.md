.
├── fastapi_starter
│   ├── cli.py
│   ├── __init__.py
│   └── template
│       ├── alembic.ini
│       ├── app
│       │   ├── api
│       │   │   ├── __init__.py
│       │   │   └── user.py
│       │   ├── auth
│       │   │   ├── __init__.py
│       │   │   ├── jwt_handler.py
│       │   │   ├── password_utils.py
│       │   │   └── routes.py
│       │   ├── core
│       │   │   ├── config.py
│       │   │   ├── database.py
│       │   │   ├── __init__.py
│       │   │   └── logging_config.py
│       │   ├── dependencies.py
│       │   ├── external_services
│       │   │   ├── email.py
│       │   │   ├── __init__.py
│       │   │   └── notification.py
│       │   ├── __init__.py
│       │   ├── middleware
│       │   │   └── exception_logging.py
│       │   ├── models
│       │   │   ├── base.py
│       │   │   ├── __init__.py
│       │   │   └── user.py
│       │   ├── routers
│       │   │   ├── __init__.py
│       │   │   └── users.py
│       │   ├── schemas
│       │   │   ├── __init__.py
│       │   │   └── user.py
│       │   └── utils
│       │       ├── __init__.py
│       │       ├── token.py
│       │       └── validation.py
│       ├── app.db
│       ├── .env
│       ├── logs
│       │   └── app.log
│       ├── main.py
│       ├── migrations
│       │   ├── env.py
│       │   ├── README
│       │   ├── script.py.mako
│       │   └── versions
│       │       ├── 65827262450c_init_db.py
│       │       └── c82632d6b4af_create_user_and_token_table.py
│       ├── requirements.txt
│       └── tests
│           ├── conftest.py
│           ├── __init__.py
│           ├── test_auth.py
│           └── test_users.py
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
├── README.md
├── requirements.txt
├── setup.cfg
├── setup.py
└── structure.md

18 directories, 54 files
