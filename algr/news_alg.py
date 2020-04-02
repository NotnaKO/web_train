from data.db_session import create_session
from flask import abort, jsonify
from data.news import SEPARATOR, News
from data.users import User
from data.category import Category
import os

MAX_LEN_CATEGORY = 3
CATEGORY_LIST = {'politic', 'technology', 'health'}
CHECK_MAIN_LIST = ('health', 'technology', 'politic')


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


def get_preview_and_text(text_address: str):
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


def get_data_by_list(sp: list, named=False):
    if not named:
        res = [False, False, False]
        for i in sp:
            if i.name == 'politic':
                res[0] = True
            elif i.name == 'health':
                res[2] = True
            elif i.name == 'technology':
                res[1] = True
        if res:
            return res
        else:
            raise BadCategoryError
    else:
        return ','.join(map(lambda x: x.name, sp))


def get_news_by_category_name(category_name: str, return_session=False):
    session = create_session()
    news = session.query(News).join(News.category).filter(Category.name == category_name).all()
    if not return_session:
        return news
    else:
        return news, session


def get_response_by_news(news, auth=None, session=None):
    if not session:
        session = create_session()
    if not auth:
        auth = session.query(User).get(news.author)
    d = {'news': news.to_dict(
        only=('id', 'header', 'modified_date'))}
    d['news']['all_categories'] = get_data_by_list(news.category, True).split(',')
    try:
        d['news']['main_category'] = get_main_cat_news_of_string_list(get_data_by_list(news.category, True))
    except BadCategoryError:
        return jsonify({'error': 'Bad categories'})
    d['news']['politic'], d['news']['technology'], d['news']['health'] = get_data_by_list(news.category)
    d['news']['author_surname'] = auth.surname
    d['news']['author_name'] = auth.name
    d['news']['author_id'] = auth.id
    with open(os.path.join('news', news.text_address), encoding='utf-8') as f:
        d['news']['text'] = f.read()
    return jsonify(d)


def get_main_cat_news_of_string_list(st: str):
    sp = st.split(',')
    for i in CHECK_MAIN_LIST:
        if i in sp:
            return i
    raise BadCategoryError


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
