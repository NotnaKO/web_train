from flask import *
from flask_restful import reqparse, Resource
from .news import News, SEPARATOR
from .users import User
from .category import Category
from .db_session import create_session
from algr.user_alg import get_user_by_email, AuthError, check_user, address
import random
import os
import requests
from algr.news_alg import abort_if_news_not_found


class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = create_session()
        news = session.query(News).get(news_id)
        d = {'news': news.to_dict(
            only=('id', 'header', 'modified_date'))}
        for i in news.category:
            if i.name == 'politic':
                d['news']['politic'] = True
            elif i.name == 'technology':
                d['news']['technology'] = True
            elif i.name == 'health':
                d['news']['health'] = True
        auth = session.query(User).get(news.author)
        d['news']['author_surname'] = auth.surname
        d['news']['author_name'] = auth.name
        d['news']['author_id'] = auth.id
        with open(os.path.join('news', news.text_address), encoding='utf-8') as f:
            d['news']['text'] = f.read()
        return jsonify(d)

    def delete(self, news_id):
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
        abort_if_news_not_found(news_id)
        session = create_session()
        news = session.query(News).get(news_id)
        os.remove('news/{}'.format(news.text_address[0].name))
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, news_id):
        parser = reqparse.RequestParser()
        parser.add_argument('password', required=True)
        parser.add_argument('author', required=True, type=str)
        parser.add_argument('header', required=True)
        parser.add_argument('category_string_list', required=True, type=str)
        parser.add_argument('preview', required=True, type=str)
        parser.add_argument('text', required=True, type=str)
        args = parser.parse_args()
        if not check_user(get_user_by_email(args['author']), args['password']):
            return jsonify({'error': 'Bad user'})
        d = requests.delete(address + f'/api/v2/news/{news_id}', json={
            'email': args['author'],
            'password': args['password']
        })
        session = create_session()
        user = session.query(User).filter(User.email == args['author']).first()
        text_address = ''
        for i in range(5):
            a = args['header'] + str(user.id) + str(random.randint(1, 2 ** 14)) + '.txt'
            n = session.query(News).filter(News.text_address == a).first()
            if not n:
                text_address = a
                break
        if not text_address:
            return jsonify({'error': 'not_unique_header'})
        if 'success' in d.json():
            if not check_user(user, args['password']):
                return jsonify({'error': 'Bad user'})

            result = ''
            for i in text_address:
                if i.isdigit() or i.isalpha() or i == '.':
                    result += i
            news = News(author=user.id, header=args['header'], text_address=result)
            for i in args['category_string_list'].split(','):
                news.category.append(Category(name=i.strip()))
            user.news.append(news)
            session.merge(user)
            session.merge(news)
            session.commit()
            with open(os.path.join('news/' + result), encoding='utf-8', mode='w') as text_file:
                text_file.write(args['preview'] + SEPARATOR + args['text'])
            return jsonify({'success': 'OK'})
        else:
            return d


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
        parser.add_argument('category_string_list', required=True, type=str)
        parser.add_argument('preview', required=True, type=str)
        parser.add_argument('text', required=True, type=str)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        session = create_session()
        user = session.query(User).filter(User.email == args['author']).first()
        if not check_user(user, args['password']):
            return jsonify({'error': 'Bad user'})
        text_address = ''
        for i in range(5):
            a = args['header'] + str(user.id) + str(random.randint(1, 2 ** 14)) + '.txt'
            n = session.query(News).filter(News.text_address == a).first()
            if not n:
                text_address = a
                break
        if not text_address:
            return jsonify({'error': 'not_unique_header'})
        result = ''
        for i in text_address:
            if i.isdigit() or i.isalpha() or i == '.':
                result += i
        news = News(author=user.id, header=args['header'], text_address=result)
        for i in args['category_string_list'].split(','):
            news.category.append(Category(name=i.strip()))
        user.news.append(news)
        session.merge(user)
        session.merge(news)
        session.commit()

        with open(os.path.join('news/' + result), encoding='utf-8', mode='w') as text_file:
            text_file.write(args['preview'] + SEPARATOR + args['text'])
        return jsonify({'success': 'OK'})
