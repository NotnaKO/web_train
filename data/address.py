import sqlalchemy

from .db_session import SqlAlchemyBase
from .users import SerializerMixin

association_table = sqlalchemy.Table('association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('news', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('news.id')),
                                     sqlalchemy.Column('address', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('address.id'))
                                     )


class Address(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'address'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
