from flask import *
from flask_restful import reqparse, abort, Resource
from requests import post
from .db_session import create_session
from .users import User
from algr.user_search import get_by_email, AuthError

address = 'https://pybank.herokuapp.com'


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
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        try:
            user = get_by_email(args['email'])
        except AuthError:
            return jsonify({'error': 'Bad user'})
        if not user.check_password(args['password']):
            return jsonify({'error': 'Bad password'})
        abort_if_user_not_found(user_id)
        session = create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        if 'success' in self.delete(user_id).json:
            args = parser.parse_args()
            session = create_session()
            user = User(
                surname=args['surname'],
                name=args['name'],
                age=args['age'],
                email=args['email'],
                address=args['address'],
                position=args['position'],
                id=user_id
            )
            user.set_password(args['password'])
            session.add(user)
            session.commit()
            return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('age', required=True, type=int)
parser.add_argument('email', required=True)
parser.add_argument('address', required=True)
parser.add_argument('password', required=True)
parser.add_argument('position', type=int, default=3)


class UserListResource(Resource):
    def get(self):
        session = create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('id', 'surname', 'name')) for item in user]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            email=args['email'],
            address=args['address'],
            position=args['position']
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
