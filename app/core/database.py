
import databases
import sqlalchemy

from pydantic import BaseModel

# SQLAlchemy specific code

# "postgresql://user:password@postgresserver/database"
DATABASE_URL = "postgresql://postgres:postgres@localhost/data"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

images = sqlalchemy.Table(
    "images",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("relative_path", sqlalchemy.String),
)


engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)


class ImageIn(BaseModel):
    text: str
    relative_path: str


class Image(ImageIn):
    id: int

