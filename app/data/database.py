import time

import databases
import sqlalchemy
from sqlalchemy import exc

from app.config import DATABASE_URL

# SQLAlchemy specific code

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

images = sqlalchemy.Table(
    "images",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("relative_path", sqlalchemy.String),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"),
                      nullable=False),
)

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True, nullable=False, index=True),
    sqlalchemy.Column("full_name", sqlalchemy.String),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("hashed_password", sqlalchemy.String),
    sqlalchemy.Column("disabled", sqlalchemy.Boolean),
)

# Wait until the database is available
created = False
while not created:
    try:
        engine = sqlalchemy.create_engine(
            DATABASE_URL
        )
        metadata.create_all(engine)
        created = True
    except exc.OperationalError:
        time.sleep(5)
