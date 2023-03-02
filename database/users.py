import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id_user = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_user_tg = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    name_user_tg = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name_user = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    gender_user = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo_user = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age_user = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    sity_user = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    info_user = sqlalchemy.Column(sqlalchemy.String, nullable=True)
