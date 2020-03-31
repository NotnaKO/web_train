from data.db_session import create_session
from flask import abort
from data.news import SEPARATOR, News
from data.category import Category

MAX_LEN_CATEGORY = 3
CATEGORY_LIST = {'politic', 'technology', 'health'}


class NewsError(Exception):
    pass


class EmptyParamsError(NewsError):
    pass


class BigLenCategoryError(NewsError):
    pass


class NotUniqueCategoryError(NewsError):
    pass


class BadCategoryError(NewsError):
    pass


def abort_if_news_not_found(news_id, session=False):
    if not session:
        session = create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404, message=f"news {news_id} not found")


def get_news_by_id(ids, session=False):
    if not session:
        session = create_session()
    return session.query(News).get(ids)


def get_preview_and_text(text_address):
    n = text_address
    with open('news/{}'.format(n), encoding='utf-8') as file:
        s = file.read()
    return s.split(SEPARATOR)


def get_string_list_by_data(politic=False, technology=False, health=False):
    sp = list()
    if not any([politic, technology, health]):
        raise EmptyParamsError
    if politic:
        sp.append('politic')
    if technology:
        sp.append('technology')
    if health:
        sp.append('health')
    return ','.join(sp)


def get_data_by_list(sp: list):
    res = [False, False, False]
    for i in sp:
        if i.name == 'politic':
            res[0] = True
        elif i.name == 'health':
            res[2] = True
        elif i.name == 'technology':
            res[1] = True
    return res


def check_cat_string_list(sp: list):
    if not sp:
        raise EmptyParamsError
    if len(sp) > MAX_LEN_CATEGORY:
        raise BigLenCategoryError
    if len(set(sp)) != len(sp):
        raise NotUniqueCategoryError
    if set(sp) > CATEGORY_LIST:
        raise BadCategoryError
    return True


def get_category_by_name(name: str, session=False):
    if not session:
        session = create_session()
    cat = session.query(Category).filter(Category.name == name).first()
    return cat
