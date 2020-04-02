import sqlalchemy
from .db_session import SqlAlchemyBase
from .users import SerializerMixin

category_association_table = sqlalchemy.Table('category_association', SqlAlchemyBase.metadata,
                                              sqlalchemy.Column('news', sqlalchemy.Integer,
                                                                sqlalchemy.ForeignKey('news.id')),
                                              sqlalchemy.Column('category', sqlalchemy.Integer,
                                                                sqlalchemy.ForeignKey('category.id')))


class Category(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
