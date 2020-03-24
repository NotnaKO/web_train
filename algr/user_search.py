from flask_restful import abort
from flask import jsonify

from data.db_session import create_session
from data.users import User


class AuthError(Exception):
    pass


def get_by_email(user_email):
    session = create_session()
    user = session.query(User).filter(User.email == user_email).first()
    if not user:
        raise AuthError
    return user


def get_by_id(ids):
    session = create_session()
    return session.query(User).get(ids)
