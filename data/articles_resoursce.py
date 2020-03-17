from flask import *
from flask_restful import reqparse, abort, Resource

from .articles import Articles
from .db_session import create_session


def abort_if_article_not_found(article_id):
    session = create_session()
    article = session.query(Articles).get(article_id)
    if not article:
        abort(404, message=f"article {article_id} not found")


class ArticlesResource(Resource):
    def get(self, article_id):
        abort_if_article_not_found(article_id)
        session = create_session()
        article = session.query(Articles).get(article_id)
        return jsonify({'article': article.to_dict(
            only=('id', 'author', 'header', 'text_address'))})

    def delete(self, article_id):
        abort_if_article_not_found(article_id)
        session = create_session()
        article = session.query(Articles).get(article_id)
        session.delete(article)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('author', required=True, type=int)
parser.add_argument('header', required=True)
parser.add_argument('text_address', required=True, type=int)


class ArticlesListResource(Resource):
    def get(self):
        session = create_session()
        article = session.query(Articles).all()
        return jsonify({'article': [item.to_dict(
            only=('author', 'header', 'text_address')) for item in article]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        article = Articles(author=args['author'], header=args['header'], text_address=args['text_address'])
        session.add(article)
        session.commit()
        return jsonify({'success': 'OK'})
