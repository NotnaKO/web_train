from data.db_session import create_session
from .user_alg import address
from flask import abort
from data.news import SEPARATOR
from data.news import News


def abort_if_news_not_found(news_id):
    session = create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f"news {news_id} not found")


def get_news_by_id(ids):
    session = create_session()
    return session.query(News).get(ids)


def get_preview_and_text(text_address):
    n = text_address[0].name
    with open('news/{}'.format(n), encoding='utf-8') as file:
        s = file.read()
    return s.split(SEPARATOR)
