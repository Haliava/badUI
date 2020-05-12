import datetime
import sqlalchemy.ext.declarative as dec
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    """Таблица users в базе данных bad_ui.sqlite
    
    Поля:
    id (integer): id пользователя
    name (string): ник пользователя (пока он не отображается в комментариях)
    is_moderator (boolean): является пользователь модератором или нет
    request_id (integer): id запроса пользователя в модераторы
    hashed_password (string): хэшированный пароль польщователя, указанный при регистрации
    """
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
        """Хэшировать пароль"""
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """Совпадает ли введённый пароль с хэшированным"""
        return check_password_hash(self.hashed_password, password)


class Article(SqlAlchemyBase):
    """Таблица articles в базе данных bad_ui.sqlite
    
    Поля:
    id (integer): id записи
    thumbnail (string): url заставки новости (отображается на главной странице)
    is_anonymous (boolean): показывать ник автора или нет
    author_name (string): ник автора
    html_code (string): html код записи
    css_code (string): css код записи
    script_code (string): js код записи
    views (integer): просмотры записи (обновляется каждый раз при открытии записи,
    даже если пользователь уже видел эту запись за текущую сессию)
    """
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
    """Таблица requests в базе данных bad_ui.sqlite

    Поля:
    id (integer): id запроса
    introduction (string): представление пользователя
    about (string): пользователь рассказывает о себе
    applicant_id (integer): id пользователя, который делает запрос
    is_request_accepted (boolean): принят запрос или отклонён
    """
    __tablename__ = 'requests'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    introduction = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    applicant_id = sqlalchemy.Column(sqlalchemy.ForeignKey('users.id'))
    is_request_accepted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=None)


class Comment(SqlAlchemyBase):
    """Таблица comments в базе данных bad_ui.sqlite

    Поля:
    id (integer): id комментария
    article (integer): id комментируемой записи
    user_id (integer): id комментирующего
    text (integer): текст комментария
    """
    __tablename__ = 'comments'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    article = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('articles.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False, default='')
