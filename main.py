from flask import Flask, render_template, redirect, abort, request, Markup
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
import schedule

from data import db_session
from data.users import User, Article, Request, Comment

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init('db/bad_ui.sqlite')
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# Заставка, которая используется по умолчанию при добавлении записи
DEFAULT_IMG = 'https://sun9-14.userapi.com/c851336/v851336298/154110/Q_2YL1-RMoA.jpg'


# Форма регистрации
class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


# Форма логина
class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


# Форма создания новой записи
class NewArticle(FlaskForm):
    thumbnail = StringField('Заставка (url)', default=DEFAULT_IMG)
    html_code = TextAreaField('html', validators=[DataRequired()])
    script_code = TextAreaField('script')
    css_code = TextAreaField('css')
    is_anonymous = BooleanField('Не показывать ник автора', default=False)
    submit = SubmitField('Создать')


# Форма заявки в модераторы
class ModForm(FlaskForm):
    introduction = StringField('Представьтесь', validators=[DataRequired()])
    about = TextAreaField('Расскажите о своих качествах, как модератора', validators=[DataRequired()])
    submit = SubmitField('Отправить')


# Форма комментария
class CommentForm(FlaskForm):
    text_data = TextAreaField('Оставьте комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')


@app.route('/')
@app.route('/index/')
def index():
    session = db_session.create_session()
    articles = session.query(Article).all()
    session.close()
    return render_template('index.html', title='Bad UI collection', articles=articles)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        session.close()
        if user and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        session.close()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/article', methods=['GET', 'POST'])
def add_article():
    form = NewArticle()
    if form.validate_on_submit():
        session = db_session.create_session()
        article = Article()
        article.thumbnail = form.thumbnail.data
        article.html_code = form.html_code.data
        article.script_code = form.script_code.data
        article.css_code = form.css_code.data
        article.is_anonymous = form.is_anonymous.data
        article.author_name = current_user.name
        current_user.articles.append(article)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('article.html', title='Добавление новости', form=form)


@app.route('/delete_article/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_article(id):
    session = db_session.create_session()
    news = session.query(Article).filter(Article.id == id,
                                         Article.author == current_user).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/article/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    form = NewArticle()
    if request.method == "GET":
        session = db_session.create_session()
        article = session.query(Article).filter(Article.id == id,
                                                Article.author == current_user).first()
        if article:
            form.thumbnail.data = article.thumbnail
            form.html_code.data = article.html_code
            form.lang_choice.data = article.lang_choice
            form.script_code.data = article.script_code
            form.css_code.data = article.css_code
            form.is_anonymous.data = article.is_anonymous
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        article = session.query(Article).filter(Article.id == id,
                                                Article.author == current_user).first()
        if article:
            article.thumbnail = form.thumbnail.data
            article.html_code = form.html_code.data
            article.lang_choice = form.lang_choice.data
            article.script_code = form.script_code.data
            article.css_code = form.css_code.data
            article.is_anonymous = form.is_anonymous.data
            article.author_name = current_user.name
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('article.html', title='Редактирование записи', form=form)


@app.route('/<int:id>')
def show_article(id):
    session = db_session.create_session()
    article = session.query(Article).filter(Article.id == id).first()
    html, css, script = Markup(article.html_code), article.css_code, article.script_code
    article.views += 1
    session.commit()
    session.close()
    return render_template('show_article.html', html=html, css=css, script=script)


@app.route('/moderatorRequest', methods=['GET', 'POST'])
def mod_request():
    """Отправление запроса стать модератером


    """
    form = ModForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        m_request = Request()
        m_request.introduction = form.introduction.data
        m_request.about = form.about.data
        m_request.applicant_id = current_user.id
        session.add(m_request)
        session.commit()
        return redirect('/')
    return render_template('moderatorRequest.html', title='Стать модератором', form=form)


@app.route('/comments/<int:id>', methods=['GET', 'POST'])
def article_comments(id):
    session = db_session.create_session()
    article_data = session.query(Article).filter(Article.id == id).first()
    comments_data = session.query(Comment).filter(Comment.article == id).all()
    form = CommentForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        comm = Comment()
        comm.text = form.text_data.data
        comm.article = id
        session.add(comm)
        session.commit()
        return redirect(f'/comments/{id}')
    return render_template('comments.html', comm=comments_data, form=form, title='Комментарии',
                           art_id=id, author=article_data.author_name, art_anon=article_data.is_anonymous)


# Страница о нас, в комментариях через API Яндекс карт передаётся ссылка на фотографию Pee Pee island
@app.route('/about')
def about_us():
    return render_template('about.html', title='О нас',
                           img='https://static-maps.yandex.ru/1.x/?ll=-52.836568,47.1912634&spn=0.0009,0.0007&l=map')


def check_for_new_mods():
    """Проверка базы данных на наличие новых принятых заявок в модераторы

    * Вызывается каждую минуту
    """
    session = db_session.create_session()
    requests = session.query(Request).all()
    for item in requests:
        if item.is_request_accepted is True:
            user = session.query(User).filter(User.id == item.applicant_id).first()
            user.is_moderator = True
    session.commit()
    session.close()


schedule.every().minute.do(check_for_new_mods)

if __name__ == '__main__':
    app.run()
    while True:
        schedule.run_pending()
