# VIPOE BACKEND
#### LINUX
1. ``python -m venv venv``
2. ``source venv/bin/activate``
3. ``pip install -r requirements.txt``
4. ``docker-compose up --build``
5. ``docker-compose exec backend alembic revision --autogenerate -m "Init database"``
5. ``docker-compose exec backend alembic upgrade head``