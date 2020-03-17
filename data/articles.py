from sqlalchemy import orm
import sqlalchemy
from .db_session import SqlAlchemyBase
from .users import SerializerMixin
import datetime


class Article(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'article'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    header = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text_address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)
    user = orm.relation('User')
