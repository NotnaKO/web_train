import sqlalchemy

from .db_session import SqlAlchemyBase
from .users import SerializerMixin

association_table = sqlalchemy.Table('access_association', SqlAlchemyBase.metadata,
                                     sqlalchemy.Column('users', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('users.id')),
                                     sqlalchemy.Column('access', sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey('access.id'))
                                     )


class Access(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'access'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
