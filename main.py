import requests
from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from flask_wtf import *
from wtforms import *
from wtforms.fields.html5 import EmailField
from wtforms.validators import *
from data import users_resourse, news_resource
from data.news import News, SEPARATOR
from data.db_session import create_session
from data.db_session import global_init
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
global_init('db/economy_science.db')
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
address = 'http://127.0.0.1:8080'
# address = 'https://pybank.herokuapp.com'
api.add_resource(users_resourse.UserListResource, '/api/v2/users')
api.add_resource(news_resource.NewsListResource, '/api/v2/news')
api.add_resource(users_resourse.UserResource, '/api/v2/users/<int:user_id>')
api.add_resource(news_resource.NewsResource, '/api/v2/news/<int:news_id>')


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class NewsForm(FlaskForm):
    author = StringField('Ваше логин')
    header = StringField('Заголовок новости', validators=[DataRequired()])
    theme = StringField('Тема новости', validators=[DataRequired()])
    preview = TextAreaField('Описание новости', validators=[DataRequired()])
    text = TextAreaField('Текст новости', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = EmailField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class MainNews:
    def __init__(self, idi: int):
        news = requests.get(address + f'/api/v2/news/{idi}').json()['news']
        self.header = news['header']
        self.preview, self.content = news['text'].split(SEPARATOR)
        self.theme = news['theme']
        self.author_surname = news['author_surname']
        self.author_name = news['author_name']
        self.date = news['modified_date'].split()[0]
        self.z = True


class Zagl:
    def __init__(self):
        self.header = ''
        self.preview, self.content = '', ''
        self.theme = ''
        self.author_surname = ''
        self.author_name = ''
        self.date = ''
        self.z = False


class Page:
    def __init__(self, i: int):
        self.id = i


@login_manager.user_loader
def load_user(user_id):
    session = create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        form.password.errors = ["Неправильный логин или пароль"]
        return render_template('login.html',
                               form=form)
    return render_template('login.html', title='Вход', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            form.password.errors = ["Пароли не совпадают"]
            return render_template('register.html', title='Регистрация',
                                   form=form)
        try:
            if int(form.age.data) < 6:
                form.age.errors = ["Возраст должен быть не менбше 6"]
                return render_template('register.html', title='Регистрация',
                                       form=form)
        except BaseException:
            form.age.errors = ['Неправильный формат возраста']
            return render_template('register.html', title='Регистрация',
                                   form=form)
        session = create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            form.email.errors = ["Такой пользователь уже есть"]
            return render_template('register.html', title='Регистрация',
                                   form=form)
        resp = requests.post(address + '/api/v2/users', json={
            'name': form.name.data,
            'surname': form.surname.data,
            'age': form.age.data,
            'address': form.address.data,
            'email': form.email.data,
            'password': form.password.data
        })
        if 'success' in resp.json():
            return redirect('/login')
        else:
            return render_template('register.html', title='Регистрация',
                                   form=form, message='Произошла ошибка. Проверьте данные ещё раз.')
    return render_template('register.html', title='Регистрация', form=form)


@login_required
@app.route('/news/add_news', methods=['GET', 'POST'])
def reg_news():
    form = NewsForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            resp = requests.post(address + '/api/v2/news', json={
                'author': current_user.email,
                'header': form.header.data,
                'theme': form.theme.data,
                'preview': form.preview.data,
                'text': form.text.data,
                'password': form.password.data
            }).json()
        else:
            resp = requests.post(address + '/api/v2/news', json={
                'author': form.author.data,
                'header': form.header.data,
                'theme': form.theme.data,
                'preview': form.preview.data,
                'text': form.text.data,
                'password': form.password.data
            }).json()
        if 'success' in resp:
            return redirect('/')
        elif 'error' in resp:
            if resp['error'] == 'not_unique_header':
                form.header.errors = ['Пожалуйста, выберете другой заголовок. Этот уже занят.']
            if resp['error'] == 'Bad user':
                form.password.errors = ['Неверный пароль.']
    return render_template('add_news.html', title='Добавление новости', form=form, current_user=current_user)


def abort_if_page_not_found(page_id):
    abort(404)


@app.route('/news/page/<int:number>')
def news(number):
    news = requests.get(address + '/api/v2/news').json()['news']
    max_news = len(news)
    sp = []
    for i in range(number * 6, number * 6 + 6):
        if i < max_news:
            sp.append(MainNews(news[i]['id']))
        else:
            break
    if not sp:
        abort_if_page_not_found(number)
    params = {
        'main_news': sp[0],
        'news2': sp[1] if len(sp) > 1 else Zagl(),
        'news3': sp[2] if len(sp) > 2 else Zagl(),
        'news4': sp[3] if len(sp) > 3 else Zagl(),
        'news5': sp[4] if len(sp) > 4 else Zagl(),
        'news6': sp[5] if len(sp) > 5 else Zagl(),
        'page': Page(number),
        'max_page_id': max_news // 6}
    return render_template('index.html', **params)


@app.route('/')  # Пока просто заглушка для удобства тестирования
def main():
    return render_template('base.html', title='Главная страница')


@app.route('/news/edit_news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        session = create_session()
        news = session.query(News).filter(News.id == id).filter(
            (News.user == current_user) | (1 == current_user.id)).first()
        if news:
            form.news.data = news.news
            form.team_leader.data = news.team_leader
            form.work_size.data = news.work_size
            form.collaborators.data = news.collaborators
            form.is_finished.data = news.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = create_session()
        news = session.query(News).filter(News.id == id).filter(
            (News.user == current_user) | (1 == current_user.id)).first()
        if news:
            news.is_finished = form.is_finished.data
            news.collaborators = form.collaborators.data
            news.work_size = form.work_size.data
            news.team_leader = form.team_leader.data
            news.news = form.news.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_news.html', title='Edit news', form=form)


@app.route('/news/delete_news/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = create_session()
    news = session.query(News).filter(News.id == id).filter(
        (News.user == current_user) | (1 == current_user.id)).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run()
