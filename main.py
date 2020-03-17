from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from flask_wtf import *
from wtforms import *
from wtforms.fields.html5 import EmailField
from wtforms.validators import *

from data import users_resourse, articles_resoursce
from data.articles import Articles
from data.db_session import create_session
from data.db_session import global_init
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
global_init('db/economy_science.db')
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
url = 'http://127.0.0.1:8080/'
api.add_resource(users_resourse.UserListResource, '/api/v2/users')
api.add_resource(articles_resoursce.ArticlesListResource, '/api/v2/articles')
api.add_resource(users_resourse.UserResource, '/api/v2/users/<int:user_id>')
api.add_resource(articles_resoursce.ArticlesResource, '/api/v2/articles/<int:article_id>')


class RegisterForm(FlaskForm):
    email = EmailField('Login/email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ArticlesForm(FlaskForm):
    team_leader = IntegerField('Team leader id', validators=[DataRequired()])
    article = StringField('Article Title', validators=[DataRequired()])
    work_size = IntegerField('Work size', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_finished = BooleanField('Is article finished?')
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = EmailField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Войти')


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
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        try:
            if int(form.age.data) < 0:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message='Возраст должен быть не меньше 0')
        except BaseException:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message='Неправильный возраст')
        session = create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            age=form.age.data,
            position=form.position.data,
            surname=form.surname.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Register', form=form)


@app.route('/addarticle', methods=['GET', 'POST'])
def reg_article():
    form = ArticlesForm()
    if form.validate_on_submit():
        session = create_session()
        article = Articles(
            team_leader=form.team_leader.data,
            article=form.article.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data,
        )
        current_user.articles.append(article)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('add_article.html', title='Register article', form=form)


@app.route('/')
def main():
    lis = list()
    session = create_session()
    items = []
    for article in session.query(Articles).all():
        user = session.query(User).filter(User.id == article.team_leader).first()
        fin = 'Is finished' if article.is_finished else 'Is not finished'
        lis.append(
            [article.article, user.surname + ' ' + user.name, f'{article.work_size} часов', article.collaborators, fin])
        items.append(article)
    return render_template('index.html', list_data=lis, n=len(lis), title='Works Log', item=items)


@app.route('/articles/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_articles(id):
    form = ArticlesForm()
    if request.method == "GET":
        session = create_session()
        articles = session.query(Articles).filter(Articles.id == id).filter(
            (Articles.user == current_user) | (1 == current_user.id)).first()
        if articles:
            form.article.data = articles.article
            form.team_leader.data = articles.team_leader
            form.work_size.data = articles.work_size
            form.collaborators.data = articles.collaborators
            form.is_finished.data = articles.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        session = create_session()
        articles = session.query(Articles).filter(Articles.id == id).filter(
            (Articles.user == current_user) | (1 == current_user.id)).first()
        if articles:
            articles.is_finished = form.is_finished.data
            articles.collaborators = form.collaborators.data
            articles.work_size = form.work_size.data
            articles.team_leader = form.team_leader.data
            articles.article = form.article.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_article.html', title='Edit article', form=form)


@app.route('/articles_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    session = create_session()
    articles = session.query(Articles).filter(Articles.id == id).filter(
        (Articles.user == current_user) | (1 == current_user.id)).first()
    if articles:
        session.delete(articles)
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
