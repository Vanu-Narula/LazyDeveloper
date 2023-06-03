For running Migrations
source - https://medium.com/@peytonrunyan/alembic-101-897f322c9334

1. Delete the migration directory and run command - alembic init migrations
2. Check alembic.ini, the sqlalchemy.url should point to your SQLite DB file
3. Run command - alembic revision --autogenerate -m "Create database model"
4. Run command - alembic upgrade head

Your migration will be completed.