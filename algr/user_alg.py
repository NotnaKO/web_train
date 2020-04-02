from data.db_session import create_session
from data.users import User
import requests
from data.news import SEPARATOR

address = 'https://pynews.herokuapp.com'


# address = 'http://127.0.0.1:5000'


def check_user(use, pas):
    if type(use) != User:
        return False
    if use.check_password(pas):
        return True
    return False


class MainNews:
    def __init__(self, idi: int, all_cat=False):
        news = requests.get(address + f'/api/v2/news/{idi}').json()['news']
        self.header = news['header']
        self.preview, self.content = news['text'].split(SEPARATOR)
        self.politic, self.technology, self.health = news['politic'] if 'politic' in news else False, news[
            'technology'] if 'technology' in news else False, news['health'] if 'health' in news else False
        self.author_surname = news['author_surname']
        self.author_name = news['author_name']
        self.author = news['author_id']
        self.id = news['id']
        self.date = news['modified_date'].split()[0]
        self.main_category = news['main_category']
        if all_cat:
            self.all_categories = news['all_categories']
        self.z = True


class Zagl:
    def __init__(self):
        self.header = ''
        self.preview, self.content = '', ''
        self.politic, self.technology, self.health = False, False, False
        self.author_surname = ''
        self.author_name = ''
        self.date = ''
        self.category = ''
        self.z = False


class AuthError(Exception):
    pass


def get_user_by_email(user_email, session=False):
    if not session:
        session = create_session()
    user = session.query(User).filter(User.email == user_email).first()
    if not user:
        raise AuthError
    return user


def get_user_by_id(ids, session=False):
    if not session:
        session = create_session()
    return session.query(User).get(ids)


def get_params_to_show_user(user, current_user, form, message=''):
    news = []
    if user.position != 3:
        news = user.news
    params = {
        'title': user.surname + ' ' + user.name,
        'surname': form.surname.data if form.surname.data else user.surname,
        'name': form.name.data if form.name.data else user.name,
        'age': form.age.data if form.age.data else user.age,
        'address': form.address.data if form.address.data else user.address,
        'id': user.id,
        'current_id': current_user.id if current_user.is_authenticated else -1,
        'status': 'Автор' if user.position != 3 else 'Пользователь',
        'form': form,
        'message': message
    }
    if len(news) >= 2:
        params['news1'] = MainNews(news[-1].id)
        params['news2'] = MainNews(news[-2].id)
    elif len(news) == 1:
        params['news1'] = MainNews(news[-1].id)
        params['news2'] = Zagl()
    else:
        params['news1'] = Zagl()
        params['news2'] = Zagl()
    return params
