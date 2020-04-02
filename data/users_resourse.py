from flask import *
from flask_restful import reqparse, abort, Resource
from .db_session import create_session
from .users import User
from algr.user_alg import get_user_by_email, AuthError, get_user_by_id, address
from algr.check import full_decode_errors, some_decode_errors, make_new_password, NotEqualError
from .news import News


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
            user = get_user_by_email(args['email'])
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
        parser.add_argument('password')
        parser.add_argument('position', required=True)
        parser.add_argument('old_password')
        parser.add_argument('password_again')
        parser.add_argument('new_password')
        args = parser.parse_args()
        if get_user_by_email(args['email']) != get_user_by_id(user_id):
            return jsonify({'error': 'Bad user'})
        if args['password']:
            er = some_decode_errors(args)
            if er is not True:
                return er
            user = get_user_by_email(args['email'])
            news = user.news
            if not user.check_password(args['password']):
                return jsonify({'error': 'Bad password'})
            if 'success' in self.delete(user_id).json:
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
                session.add(user)
                user.set_password(args['password'])
                for n in news:
                    news = session.query(News).get(n.id)
                    user.news.append(news)
                session.merge(user)
                session.commit()
                if not any([args['old_password'], args['new_password'], args['password_again']]):
                    return jsonify({'success': 'OK'})
        if args['old_password'] and args['new_password'] and args['password_again']:
            try:
                a = make_new_password(args['old_password'], args['new_password'], args['password_again'],
                                      user=get_user_by_email(args['email']))
                if a is not True:
                    return a
            except AuthError:
                return jsonify({'error': 'Bad old password'})
            except NotEqualError:
                return jsonify({'error': 'Not equal new and again'})
            session = create_session()
            user = get_user_by_id(user_id)
            user.set_password(args['new_password'])
            session.merge(user)
            session.commit()
            return jsonify({'success': 'OK'})
        if (any([args['old_password'], args['new_password'], args['password_again']]) and args['password']) and not all(
                [args['old_password'], args['new_password'], args['password_again']]):
            return jsonify({'error': 'Not all new password'})
        return jsonify({'error': 'Empty passwords'})


parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('age', required=True, type=int)
parser.add_argument('email', required=True)
parser.add_argument('address', required=True)


class UserListResource(Resource):
    def get(self):
        session = create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('id', 'surname', 'name')) for item in user]})

    def post(self):
        parser.add_argument('password', required=True)
        parser.add_argument('position', type=int, default=3)
        args = parser.parse_args()
        # email check
        er = full_decode_errors(args)
        if er is not True:
            return er
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
