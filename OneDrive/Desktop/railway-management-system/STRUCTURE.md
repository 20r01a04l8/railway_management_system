railway-management-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   ├── exceptions.py
│   │   │   └── logging.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── station.py
│   │   │   ├── train.py
│   │   │   └── booking.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── station.py
│   │   │   ├── train.py
│   │   │   └── booking.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── station.py
│   │   │   ├── train.py
│   │   │   └── booking.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── station.py
│   │   │   ├── train.py
│   │   │   └── booking.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   ├── middleware.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── stations.py
│   │   │       ├── trains.py
│   │   │       └── bookings.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── correlation.py
│   │       └── metrics.py
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── alembic.ini
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   └── integration/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
├── frontend/
└── docs/