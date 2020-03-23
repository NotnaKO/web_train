from flask import *
from flask_restful import reqparse, abort, Resource

from .db_session import create_session
from .users import User


def abort_if_user_not_found(user_id):
    session = create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"user {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'email', 'address'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('id', 'surname', 'name')) for item in user]})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('surname', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('age', required=True, type=int)
        parser.add_argument('email', required=True)
        parser.add_argument('address', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        session = create_session()
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            email=args['email'],
            address=args['address']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
