import requests
from flask import Flask, render_template, redirect, abort, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from flask_wtf import *
from wtforms import *
from wtforms.fields.html5 import EmailField
from wtforms.validators import *
from data import users_resourse, news_resource
from data.db_session import global_init
from algr.user_alg import get_params_to_show_user, MainNews, Zagl, get_user_by_email, get_user_by_id, AuthError
from algr.news_alg import get_news_by_id, get_preview_and_text, get_string_list_by_data, EmptyParamsError, \
    get_data_by_list, get_news_by_category_name, get_response_by_news, CATEGORY_LIST

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'
global_init('db/economy_science.db')
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
address = users_resourse.address
api.add_resource(users_resourse.UserListResource, '/api/v2/users')
api.add_resource(news_resource.NewsListResource, '/api/v2/news')
api.add_resource(users_resourse.UserResource, '/api/v2/users/<int:user_id>')
api.add_resource(news_resource.NewsResource, '/api/v2/news/<int:news_id>')


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[Email()])
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
    politic = BooleanField('Политика')
    technology = BooleanField('Технологии')
    health = BooleanField('Здоровье')
    preview = TextAreaField('Описание новости', validators=[DataRequired()])
    text = TextAreaField('Текст новости', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class LoginForm(FlaskForm):
    email = EmailField('Логин', validators=[Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class UserForm(RegisterForm):
    new_password = PasswordField('Новый пароль')
    email = EmailField('Email')
    submit = submit2 = SubmitField('Сохранить')
    old_password = PasswordField('Старый пароль')
    password = PasswordField('Ваш пароль')
    password_again = PasswordField('Повторите пароль')


class EditNewsForm(NewsForm):
    submit = SubmitField('Сохранить')


class Page:
    def __init__(self, i: int):
        self.id = i


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        try:
            user = get_user_by_email(login_form.email.data)
        except AuthError:
            login_form.email.errors = ['Не найден такой пользователь']
            return render_template('login.html', title='Вход', form=login_form)
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            return redirect("/")
        login_form.password.errors = ["Неправильный логин или пароль"]
        return render_template('login.html',
                               form=login_form)
    return render_template('login.html', title='Вход', form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    reg_form = RegisterForm()
    if reg_form.validate_on_submit():
        # password  similar check
        if reg_form.password.data != reg_form.password_again.data:
            reg_form.password.errors = ["Пароли не совпадают"]
            return render_template('register.html', title='Регистрация',
                                   form=reg_form)
        resp = requests.post(address + '/api/v2/users', json={
            'name': reg_form.name.data,
            'surname': reg_form.surname.data,
            'age': reg_form.age.data,
            'address': reg_form.address.data,
            'email': reg_form.email.data,
            'password': reg_form.password.data
        })
        if 'success' in resp.json():
            return redirect('/login')
        else:
            resp_js = resp.json()
            er = True
            # email
            if resp_js['error'] == 'EmailLetterError':
                reg_form.email.errors = ['Email может состоять из английских букв, цифр и других символов']
            elif resp_js['error'] == 'EnglishError':
                reg_form.email.errors = ['Email должен содержать английские буквы']
            elif resp_js['error'] == 'OthersLettersError':
                reg_form.email.errors = ['Email должен содержать другие символы']
            elif resp_js['error'] == 'SimilarUserError':
                reg_form.email.errors = ["Такой пользователь уже есть"]
            # password
            elif resp_js['error'] == 'PasswordLetterError':
                reg_form.password.errors = ['В пароле должны присутствовать строчные и прописные буквы.']
            elif resp_js['error'] == 'LengthError':
                reg_form.password.errors = ['В пароле должно быть 8 и больше символов.']
            elif resp_js['error'] == 'LanguageError':
                reg_form.password.errors = ['В пароле должныть только буквы английского языка, цифры и другие символы.']
            elif resp_js['error'] == 'DigitError':
                reg_form.password.errors = ['В пароле должны быть цифры.']
            elif resp_js['error'] == 'SequenceError':
                reg_form.password.errors = ['В пароле не должно быть трёх символов, идущих подряд на клавиатуре.']
            # age
            elif resp_js['error'] == 'AgeRangeError' or resp_js['error'] == 'ValueAgeError':
                reg_form.age.errors = ['Возраст должен быть натуральным числом от 6 до 110']
            else:
                er = False
            if er:
                return render_template('register.html', title='Регистрация',
                                       form=reg_form)
            else:
                return render_template('register.html', title='Регистрация',
                                       form=reg_form, message='Произошла ошибка. Проверьте данные ещё раз.')
    return render_template('register.html', title='Регистрация', form=reg_form)


@app.route('/users/<int:ids>', methods=['GET', 'POST'])
def show_users_data(ids):
    user_form = UserForm()
    if user_form.validate_on_submit():
        user = get_user_by_id(ids)
        resp = requests.put(address + f'/api/v2/users/{ids}', json={
            'name': user_form.name.data,
            'surname': user_form.surname.data,
            'age': user_form.age.data,
            'address': user_form.address.data,
            'email': user.email,
            'password': user_form.password.data,
            'new_password': user_form.new_password.data,
            'old_password': user_form.old_password.data,
            'password_again': user_form.password_again.data,
            'position': user.position
        })
        if 'success' in resp.json():
            user = get_user_by_id(ids)
            params = get_params_to_show_user(user, current_user, user_form)
            if user_form.password.data and not all(
                    [user_form.old_password.data, user_form.new_password.data, user_form.password_again]):
                return render_template('show_users.html', success_load_data=True, **params)
            if all([user_form.old_password.data, user_form.new_password.data,
                    user_form.password_again]) and not user_form.password.data:
                return render_template('show_users.html', success_set_password=True, **params)
            if all([user_form.old_password.data, user_form.new_password.data,
                    user_form.password_again]) and user_form.password.data:
                return render_template('show_users.html', success_set_password=True, success_load_data=True, **params)
        else:
            user = get_user_by_id(ids)
            resp_js = resp.json()
            er = True
            # email
            if resp_js['error'] == 'EmailLetterError':
                user_form.email.errors = ['Email может состоять из английских букв, цифр и других символов']
            elif resp_js['error'] == 'EnglishError':
                user_form.email.errors = ['Email должен содержать английские буквы']
            elif resp_js['error'] == 'OthersLettersError':
                user_form.email.errors = ['Email должен содержать другие символы']
            elif resp_js['error'] == 'SimilarUserError':
                user_form.email.errors = ["Такой пользователь уже есть"]
            # password
            elif resp_js['error'] == 'PasswordLetterError':
                if user_form.password.data:
                    user_form.password.errors = ['В пароле должны присутствовать строчные и прописные буквы.']
                if user_form.new_password.data:
                    user_form.new_password.errors = ['В пароле должны присутствовать строчные и прописные буквы.']
            elif resp_js['error'] == 'LengthError':
                if user_form.password.data:
                    user_form.password.errors = ['В пароле должно быть 8 и больше символов.']
                if user_form.new_password.data:
                    user_form.new_password.errors = ['В пароле должно быть 8 и больше символов.']
            elif resp_js['error'] == 'LanguageError':
                if user_form.password.data:
                    user_form.password.errors = [
                        'В пароле должныть только буквы английского языка, цифры и другие символы.']
                if user_form.new_password.data:
                    user_form.new_password.errors = [
                        'В пароле должныть только буквы английского языка, цифры и другие символы.']
            elif resp_js['error'] == 'DigitError':
                if user_form.password.data:
                    user_form.password.errors = ['В пароле должны быть цифры.']
                if user_form.new_password.data:
                    user_form.new_password.errors = ['В пароле должны быть цифры.']
            elif resp_js['error'] == 'SequenceError':
                if user_form.password.data:
                    user_form.password.errors = ['В пароле не должно быть трёх символов, идущих подряд на клавиатуре.']
                if user_form.new_password.data:
                    user_form.new_password.errors = [
                        'В пароле не должно быть трёх символов, идущих подряд на клавиатуре.']
            # age
            elif resp_js['error'] == 'AgeRangeError' or resp_js['error'] == 'ValueAgeError':
                user_form.age.errors = ['Возраст должен быть натуральным числом от 6 до 110.']
            elif resp_js['error'] == 'Bad user':
                user_form.password.errors = ['Ошибка пользователя. Попробуйте выйти и зайти снова.']
            elif resp_js['error'] == 'Bad password':
                user_form.password.errors = ['Ошибка пользователя. Пожалуйста, введите правильный пароль.']
            elif resp_js['error'] == 'Not equal new and again':
                user_form.password_again.errors = ['Пароли не совпадают']
            elif resp_js['error'] == 'Bad old password':
                user_form.old_password.errors = ['Ошибка пользователя. Пожалуйста, введите правильный пароль.']
            elif resp_js['error'] == 'Not all new password':
                user_form.old_password.errors = ['Пожалуйста, заполните все поля паролей перед сменой.']
            elif resp_js['error'] == 'Empty passwords':
                user_form.password.errors = ['Пожалуйста, заполните это поле, если хотите изменить свои данные']
                user_form.old_password.errors = ['Пожалуйста, заполните это поле, если сменить пароль']
            else:
                er = False
            params = get_params_to_show_user(user, current_user, user_form)
            if er:
                return render_template('show_users.html', **params)
            else:
                return render_template('show_users.html', **params,
                                       message='Произошла ошибка. Проверьте данные ещё раз.')
    else:
        user = get_user_by_id(ids)
        params = get_params_to_show_user(user, current_user, user_form)
        if not current_user.is_authenticated and (user.position != 2 and user.position != 1):
            abort(404)
        if current_user.is_authenticated:
            if not (user.position == 2 or (user.position == 3 and user.id == current_user.id) or (
                    current_user.position == 1)):
                abort(404)
        return render_template('show_users.html', **params)


@app.route('/news/news_by_author/<int:ids>/page/<int:number>')
def show_news_by_author(ids, number):
    user = get_user_by_id(ids)
    if user.position == 3:
        abort(404)
    else:
        return news_page(news_resp=jsonify({'news': [item.to_dict(
            only=('id', 'header')) for item in user.news]}), by_author=True, number=number)


@login_required
@app.route('/news/add_news', methods=['GET', 'POST'])
def add_news():
    news_form = NewsForm()
    if news_form.validate_on_submit():
        try:
            cat_str_list = get_string_list_by_data(news_form.politic.data, news_form.technology.data,
                                                   news_form.health.data)
        except EmptyParamsError:
            return render_template('add_news.html', title='Добавление новости', form=news_form,
                                   current_user=current_user,
                                   message="Пожалуйста, выберете категорию новости.")
        if current_user.is_authenticated:
            resp = requests.post(address + '/api/v2/news', json={
                'author': current_user.email,
                'header': news_form.header.data,
                'category_string_list': cat_str_list,
                'preview': news_form.preview.data,
                'text': news_form.text.data,
                'password': news_form.password.data
            }).json()
            user = current_user
        else:
            resp = requests.post(address + '/api/v2/news', json={
                'author': news_form.author.data,
                'header': news_form.header.data,
                'category_string_list': cat_str_list,
                'preview': news_form.preview.data,
                'text': news_form.text.data,
                'password': news_form.password.data
            }).json()
            user = get_user_by_email(news_form.author.data)
        if 'success' in resp and user.position == 3:
            p = requests.put(address + '/api/v2/users/{}'.format(user.id), json={
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'email': user.email,
                'position': 2,
                'age': user.age,
                'address': user.address,
                'password': news_form.password.data
            })
            if 'success' in p.json():
                return redirect('/news')
        elif 'error' in resp:
            if resp['error'] == 'not_unique_header':
                news_form.header.errors = ['Пожалуйста, выберете другой заголовок. Этот уже занят.']
            elif resp['error'] == 'Bad user':
                news_form.password.errors = ['Неверный пароль.']
        elif 'success' in resp and user.position != 3:
            return redirect('/news')
        else:
            return render_template('add_news.html', title='Добавление новости', form=news_form,
                                   current_user=current_user,
                                   message='Произошла непредвиденная ошибка, пожалуйста попробуйте позже.')
    return render_template('add_news.html', title='Добавление новости', form=news_form, current_user=current_user)


@app.route('/news/category/<category>/<int:number>')
def show_category_news_page(category: str, number):
    if category not in CATEGORY_LIST:
        abort(404)
    translate = {
        'politic': "Политика",
        'technology': "Технологии",
        'health': "Здоровье"
    }
    news_and_session = get_news_by_category_name(category, return_session=True)
    news_resp = {'news': []}
    for i in news_and_session[0]:
        el = get_response_by_news(i, session=news_and_session[1]).json
        news_resp['news'].append(el['news'])
    return news_page(number=number, news_resp=jsonify(news_resp), by_category=True,
                     title=translate[category])


@app.route('/news/<int:number>')
def show_news(number):
    news = MainNews(number, all_cat=True)
    return render_template('show_news.html', news=news, title='Новости')


@app.route('/news/page/<int:number>')
def news_page(number=0, news_resp=None, by_author=False, title='Главная', by_category=False):
    def abort_if_page_not_found():
        abort(404)

    if news_resp is None:
        news = requests.get(address + '/api/v2/news').json()['news']
    else:
        news = news_resp.json['news']
    max_news = len(news)
    if max_news == 0:
        abort(404)
    sp = []
    for i in range(max_news - number * 6 - 1, max_news - number * 6 - 7 if max_news - number * 6 - 7 >= 0 else -1, -1):
        if 0 <= i < max_news:
            sp.append(MainNews(news[i]['id']))
        else:
            break
    if not sp:
        abort_if_page_not_found()
    params = {
        'main_news': sp[0],
        'news2': sp[1] if len(sp) > 1 else Zagl(),
        'news3': sp[2] if len(sp) > 2 else Zagl(),
        'news4': sp[3] if len(sp) > 3 else Zagl(),
        'news5': sp[4] if len(sp) > 4 else Zagl(),
        'news6': sp[5] if len(sp) > 5 else Zagl(),
        'page': Page(number),
        'max_page_id': max_news // 6 - 1 if max_news % 6 == 0 else max_news // 6,
        'by_author': by_author,
        'by_category': by_category,
        'title': title}
    return render_template('news_page.html', **params)


@app.route('/news')
def f():
    return redirect('/')


@app.route('/')  # Пока просто заглушка для удобства тестирования
def main():
    return news_page()


@app.route('/news/edit_news/<int:ids>', methods=['GET', 'POST'])
@login_required
def edit_news(ids):
    ed_news_form = EditNewsForm()
    if ed_news_form.validate_on_submit():
        try:
            cat_str_list = get_string_list_by_data(ed_news_form.politic.data, ed_news_form.technology.data,
                                                   ed_news_form.health.data)
        except EmptyParamsError:
            return render_template('add_news.html', title='Добавление новости', form=ed_news_form,
                                   current_user=current_user,
                                   message="Пожалуйста, выберете категорию новости.")
        resp = requests.put(address + f'/api/v2/news/{ids}', json={
            'password': ed_news_form.password.data,
            'author': current_user.email,
            'preview': ed_news_form.preview.data,
            'category_string_list': cat_str_list,
            'text': ed_news_form.text.data,
            'header': ed_news_form.header.data
        })
        resp_js = resp.json()
        if 'success' in resp_js:
            return redirect('/news')
        elif resp_js['error'] == 'Bad user':
            ed_news_form.password.errors = ['Неверный пароль. Попробуйте ещё раз.']
        elif resp_js['error'] == 'not unique header':
            ed_news_form.header.errors = ['Уже есть много статей с таким заголовком, пожалуйста выбирете другой.']
        elif resp_js['error'] == 'Empty category':
            return render_template('add_news.html', title='Редактирование новости', form=ed_news_form,
                                   message='Пожалуста, выберете хотя бы одну категорию своей новости.')
        else:
            return render_template('add_news.html', title='Редактирование новости', form=ed_news_form,
                                   message='Произошла непредвиденная ошибка, пожалуйста попробуйте позже.')
    news = get_news_by_id(ids)
    if news.user == current_user or current_user.position == 1:
        ed_news_form.header.data = news.header
        ed_news_form.politic.data, ed_news_form.technology.data, ed_news_form.health.data = get_data_by_list(
            news.category)
        ed_news_form.preview.data, ed_news_form.text.data = get_preview_and_text(news.text_address)
    else:
        abort(404)
    return render_template('add_news.html', title='Редактирование новости', form=ed_news_form)


@app.route('/news/delete_news/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(ids):
    if 'success' in requests.delete(address + '/api/v2/news/{}'.format(ids)):
        return redirect('/news')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run()
