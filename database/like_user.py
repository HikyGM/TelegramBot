import sqlalchemy
from .db_session import SqlAlchemyBase


class Like(SqlAlchemyBase):
    __tablename__ = 'like_users'
    id_like = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_tg = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    like_user_tg = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
