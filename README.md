# VIPOE BACKEND
#### LINUX
1. ``python -m venv venv``
2. ``source venv/bin/activate``
3. ``pip install -r requirements.txt``
4. ``docker-compose up --build``
5. ``docker-compose exec backend alembic upgrade head``
5. ``docker-compose exec backend alembic revision --autogenerate -m "Init database"``
6. ``psql -U johnvo -d vipoedb -h localhost -p 5433 -f app/init_data.sql``