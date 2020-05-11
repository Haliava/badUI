import datetime
import sqlalchemy.ext.declarative as dec
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    articles = orm.relation('Article', back_populates='author', lazy='subquery')
    is_moderator = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    request_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('requests.applicant_id'))
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f'<User> {self.id} {self.name} {self.email} {self.about}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Article(SqlAlchemyBase):
    __tablename__ = 'articles'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    thumbnail = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    author_name = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('users.name'))
    author = orm.relation('User', back_populates='articles', lazy='subquery')
    html_code = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    script_code = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    css_code = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_anonymous = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    views = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    comments = orm.relation('Comment', lazy='subquery')


class Request(SqlAlchemyBase):
    __tablename__ = 'requests'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    introduction = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    applicant_id = sqlalchemy.Column(sqlalchemy.ForeignKey('users.id'))
    is_request_accepted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=None)


class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    article = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('articles.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='')


# session = create_session()
# user = session.query(User).filter(User.id == 1).first()
# news = News(title="Личная запись", content="Эта запись личная",
#             is_private=True)
# user.news.append(news)
# session.commit()
# user = session.query(User).filter((User.id == 1)).first()
# print(user)
# user.name = "Измененное имя пользователя"
# user.created_date = datetime.datetime.now()
# session.commit()
# user = session.query(User).filter(User.id == 3).first()
# session.delete(user)
# session.commit()
