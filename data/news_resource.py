from flask import *
from flask_restful import reqparse, abort, Resource
from .news import News, SEPARATOR
from .users import User
from .address import Address
from .db_session import create_session
import random
import os


def abort_if_news_not_found(news_id):
    session = create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f"news {news_id} not found")


def check_user(use, pas):
    if type(use) != User:
        return False
    if use.check_password(pas):
        return True
    return False


class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = create_session()
        news = session.query(News).get(news_id)
        d = {'news': news.to_dict(
            only=('id', 'header', 'theme', 'modified_date'))}
        auth = session.query(User).get(news.author)
        d['news']['author_surname'] = auth.surname
        d['news']['author_name'] = auth.name
        d['news']['author_id'] = auth.id
        with open(os.path.join('news', news.text_address[0].name), encoding='utf-8') as f:
            d['news']['text'] = f.read()
        return jsonify(d)

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = create_session()
        news = session.query(News).get(news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class NewsListResource(Resource):
    def get(self):
        session = create_session()
        news = session.query(News).all()
        return jsonify({'news': [item.to_dict(
            only=('id', 'header')) for item in news]})

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('author', required=True, type=str)
        parser.add_argument('header', required=True)
        parser.add_argument('theme', required=True, type=str)
        parser.add_argument('preview', required=True, type=str)
        parser.add_argument('text', required=True, type=str)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        session = create_session()
        user = session.query(User).filter(User.email == args['author']).first()
        if user.email != args['author']:
            return jsonify({'error': 'Bad author'})
        if not check_user(user, args['password']):
            return jsonify({'error': 'Bad user'})
        text_address = ''
        for i in range(5):
            a = args['header'] + str(user.id) + str(random.randint(1, 2 ** 14)) + '.txt'
            ad = session.query(Address).filter(Address.name == a).first()
            if not ad:
                text_address = a
                break
        if not text_address:
            return jsonify({'error': 'not_unique_header'})
        s = ''
        for i in text_address:
            if i.isdigit() or i.isalpha():
                s += i
        news = News(author=user.id, header=args['header'], theme=args['theme'])
        news.text_address.append(Address(name=s))
        user.news.append(news)
        session.merge(user)
        session.merge(news)
        session.commit()

        with open(os.path.join('news/' + s), encoding='utf-8', mode='w') as text_file:
            text_file.write(args['preview'] + SEPARATOR + args['text'])
        return jsonify({'success': 'OK'})
