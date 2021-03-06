from flask import *
from flask_restful import reqparse, Resource
from .news import News, SEPARATOR
from .users import User
from .category import Category
from .db_session import create_session
from algorithms.user_alg import get_user_by_email, AuthError, check_user, ADDRESS
import random
import os
from algorithms.check import check_author_by_news_id
from algorithms.news_alg import abort_if_news_not_found, check_cat_string_list, BadCategoryError, \
    BigLenCategoryError, EmptyParamsError, NotUniqueCategoryError, get_category_by_name, get_response_by_news


# В этой ветке я подумаю о том, как оставить редактирование
class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        new_session = create_session()
        news = new_session.query(News).get(news_id)
        auth = new_session.query(User).get(news.author)
        return get_response_by_news(news, auth=auth, session=new_session)

    def delete(self, news_id):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)
        args = parser.parse_args()
        new_session = create_session()
        try:
            user = get_user_by_email(args['email'], new_session)
        except AuthError:
            return jsonify({'error': 'Bad user'})
        if not user.check_password(args['password']):
            return jsonify({'error': 'Bad password'})
        abort_if_news_not_found(news_id)
        news = new_session.query(News).get(news_id)
        if not check_author_by_news_id(user, news):
            return jsonify({'error': 'No rights'})
        os.remove(os.path.join('news/' + news.text_address))
        new_session.delete(news)
        new_session.commit()
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
        abort_if_news_not_found(news_id)
        new_session = create_session()
        user = new_session.query(User).filter(User.email == args['author']).first()
        news = new_session.query(News).get(news_id)
        if not check_author_by_news_id(user, news):
            return jsonify({'error': 'Bad user'})
        user.news.remove(news)
        news.header = args['header']
        news.preview = args['preview']
        sp = args['category_string_list'].split(',')
        try:
            check_cat_string_list(sp)
        except EmptyParamsError:
            return jsonify({'error': 'Empty category'})
        except BadCategoryError:
            return jsonify({'error': 'Bad categories'})
        except BigLenCategoryError:
            return jsonify({'error': 'Big length of category'})
        except NotUniqueCategoryError:
            return jsonify({'error': 'Not unique categories'})
        news.category = []
        for i in sp:
            cat = get_category_by_name(i.strip(), new_session)
            if cat:
                news.category.append(cat)
            else:
                news.category.append(Category(name=i.strip()))
        user.news.append(news)
        new_session.merge(user)
        new_session.commit()
        with open(os.path.join('news/' + news.text_address), encoding='utf-8', mode='w') as text_file:
            text_file.write(args['preview'] + SEPARATOR + args['text'])
        return jsonify({'success': 'OK'})


class NewsListResource(Resource):
    def get(self):
        new_session = create_session()
        news = new_session.query(News).all()
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
        new_session = create_session()
        user = get_user_by_email(args['author'], new_session)
        if not check_user(user, args['password']):
            return jsonify({'error': 'Bad user'})
        text_address = ''
        for i in range(5):
            a = args['header'] + str(user.id) + str(random.randint(1, 2 ** 14)) + '.txt'
            n = new_session.query(News).filter(News.text_address == a).first()
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
        sp = args['category_string_list'].split(',')
        try:
            check_cat_string_list(sp)
        except EmptyParamsError:
            return jsonify({'error': 'Empty category'})
        except BadCategoryError:
            return jsonify({'error': 'Bad categories'})
        except BigLenCategoryError:
            return jsonify({'error': 'Big length of category'})
        except NotUniqueCategoryError:
            return jsonify({'error': 'Not unique categories'})
        for i in sp:
            cat = get_category_by_name(i.strip(), new_session)
            if cat:
                news.category.append(cat)
            else:
                news.category.append(Category(name=i.strip()))
        user = get_user_by_email(args['author'], new_session)
        user.news.append(news)
        new_session.merge(user)
        new_session.commit()
        with open(os.path.join('news/' + result), encoding='utf-8', mode='w') as text_file:
            text_file.write(args['preview'] + SEPARATOR + args['text'])
        return jsonify({'success': 'OK'})
