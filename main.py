from flask import Flask
from flask_restful import Api

from data import users_resourse, articles_resoursce
from data.db_session import global_init

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
global_init('db/mars_exploers.db')
api = Api(app)
url = 'http://127.0.0.1:8080/'
api.add_resource(users_resourse.UserListResource, '/api/v2/users')
api.add_resource(articles_resoursce.ArticlesListResource, '/api/v2/articles')
api.add_resource(users_resourse.UserResource, '/api/v2/users/<int:user_id>')
api.add_resource(articles_resoursce.ArticlesResource, '/api/v2/articles/<int:article_id>')

if __name__ == '__main__':
    app.run()
