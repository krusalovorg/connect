import os

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import flask
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, \
    current_user
from wtforms.validators import DataRequired

from forms.search import SearchForm
from forms.users import RegisterForm, LoginForm
from data.users import User
from data import db_session

import sqlite3  # new!!!!!!!!!

db = 'db/db.db'  # new !!!!!!!

PASS = "NFTMarket123"
marka = "NFTMarket"

UPLOAD_FOLDER = 'static/img/'

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secreret123123'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

res = []

DEBUG = True

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/db.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)


# new
@app.route('/func_run')
def func_run():
    x = request.args.get('par_1')
    y = request.args.get('par_2')
    z = request.args.get('par_3')
    if z == "remove_user":
        if current_user.is_authenticated and current_user.role == "admin":
            db_sess = db_session.create_session()
            item = db_sess.query(User).filter(User.id == x).first()
            if item:
                db_sess.delete(item)

                db_sess.commit()


@app.route("/", methods=['GET', 'POST'])
def index():
    global res
    res.clear()
    form = SearchForm()
    # if form.validate_on_submit():
    #     db_sess = db_session.create_session()
    #     for i in users:
    #         if str(form.ttle.data).lower() in str(i.title).lower():
    #             res.append(i.id)
    #     return redirect('/search_results')
    # db_sess = db_session.create_session()
    # goods = db_sess.query(NFT)

    if current_user.is_authenticated:
        return render_template("main.html", title='Главная страница', form2=form, role=current_user.role)
    else:
        return render_template("main.html", title='Главная страница', form2=form, role=False)


@login_required
@app.route("/profile/<r>", methods=['GET', 'POST'])
def profile(r):
    global res
    nfts = []

    # db_sess = db_session.create_session()
    # a = db_sess.query(User)  # .filter(User.nickname == r).first()
    # for i in a:
    #     if i.nickname == r:
    #         print(i)

    con = sqlite3.connect(db)
    cur = con.cursor()
    try:
        db_imgs = cur.execute("SELECT image, banner FROM users WHERE nickname = ?", (r,)).fetchall()[0]
    except IndexError as ie:
        print(ie)
        return redirect('/')

    if not os.path.exists(f'{db_imgs[0]}'):
        cur.execute("UPDATE users SET image = NULL WHERE nickname = ?", (r,))
    if not os.path.exists(f'{db_imgs[1]}'):
        cur.execute("UPDATE users SET banner = NULL WHERE nickname = ?", (r,))

    user = cur.execute("SELECT * FROM users WHERE nickname = ?", (r,)).fetchone()
    con.commit()

    form = SearchForm()
    # if form.validate_on_submit():
    #     db_sess = db_session.create_session()
    #     goods = db_sess.query(Goods)
    #     for i in goods:
    #         if str(form.ttle.data).lower() in str(i.title).lower():
    #             res.append(i.id)
    #     return redirect('/search_results')
    #
    # db_sess = db_session.create_session()
    # nft = db_sess.query(NFT)
    # for i in nft:
    #     if i.address == current_user.address:
    #         nfts.append()

    return render_template("profile.html", title=r, form2=form, user=user)


@login_required
@app.route("/settings", methods=['GET', 'POST'])
def settings():
    global res

    ################################# форма тут для того, чтобы сохранять дефолтыне значения
    class RedactingForm(FlaskForm):
        nickname = StringField('Никнейм', validators=[DataRequired()], default=current_user.nickname)
        description = StringField('Описание', validators=[DataRequired()], default=current_user.description)
        name = StringField('Имя', validators=[DataRequired()], default=current_user.name)
        surname = StringField('Фамилия', validators=[DataRequired()], default=current_user.surname)
        submit = SubmitField('Применить')

    ##################################
    form = SearchForm()

    # if form.validate_on_submit():
    #     db_sess = db_session.create_session()
    #     goods = db_sess.query(Goods)
    #     for i in goods:
    #         if str(form.ttle.data).lower() in str(i.title).lower():
    #             res.append(i.id)
    #     return redirect('/search_results')

    form_redact = RedactingForm()
    if form_redact.validate_on_submit():
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute("UPDATE users SET nickname = ?, description = ?, name = ?, surname = ? WHERE id = ?", (
            form_redact.nickname.data, form_redact.description.data, form_redact.name.data, form_redact.surname.data,
            current_user.id))

        file = request.files["file"]
        filename = file.filename
        if filename:
            oldfile = cur.execute("SELECT image FROM users WHERE id = ?", (current_user.id,)).fetchone()[0]
            if oldfile:
                os.remove(oldfile)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("UPDATE users SET image = ? WHERE id = ?", (
                os.path.join(app.config['UPLOAD_FOLDER'], filename),
                current_user.id))

        file = request.files["file2"]
        filename = file.filename
        if filename:
            oldfile = cur.execute("SELECT banner FROM users WHERE id = ?", (current_user.id,)).fetchone()[0]
            if oldfile:
                os.remove(oldfile)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cur.execute("UPDATE users SET banner = ? WHERE id = ?", (
                os.path.join(app.config['UPLOAD_FOLDER'], filename),
                current_user.id))

        con.commit()
        return redirect(f"/profile/{current_user.nickname}")

    return render_template("settings.html", title='Настройки', form2=form, form_red=form_redact)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/search_results', methods=['GET', 'POST'])
# def search_results():
#     global res
#     categories = get_category()
#     form = SearchForm()
#     if form.validate_on_submit():
#         res.clear()
#         db_sess = db_session.create_session()
#         goods = db_sess.query(NFT)
#         for i in goods:
#             if str(form.ttle.data).lower() in str(i.title).lower():
#                 res.append(i.id)
#         return redirect('/search_results')
#
#     # form.button.data true - false
#     db_sess = db_session.create_session()
#     goods = db_sess.query(NFT)
#
#     return render_template('search_results.html', title='Результаты поиска',
#                            res=res, form2=form,
#                            goods=goods, cats=categories)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    global res

    form2 = SearchForm()
    # if form2.validate_on_submit():
    #     db_sess = db_session.create_session()
    #     goods = db_sess.query(NFT)
    #     for i in goods:
    #         if str(form2.ttle.data).lower() in str(i.title).lower():
    #             res.append(i.id)
    #     return redirect('/search_results')

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают", form2=form2)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   form2=form2)
        if form.email.data == "adminpanel@adminpanel.adminpanel":
            user = User(
                nickname=form.nickname.data,
                surname=form.surname.data,
                name=form.name.data,
                email=form.email.data,
                role="admin",
                description="NFT художник.. ( изменить описание можно в настройках аккаунта )"
            )
        else:
            user = User(
                nickname=form.nickname.data,
                surname=form.surname.data,
                name=form.name.data,
                email=form.email.data,
                role="user",
                description="NFT художник.. ( изменить описание можно в настройках аккаунта )",
            )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,
                           form2=form2)


@app.route('/admin/users', methods=['GET', 'POST'])
def admin_users():
    if current_user.is_authenticated and current_user.role == "admin":
        global res

        form2 = SearchForm()
        # if form2.validate_on_submit():
        #     db_sess = db_session.create_session()
        #     goods = db_sess.query(NFT)
        #     for i in goods:
        #         if str(form2.ttle.data).lower() in str(i.title).lower():
        #             res.append(i.id)
        #     return redirect('/search_results')
        #
        db_sess = db_session.create_session()
        users = db_sess.query(User)
        return render_template('admin/users.html', title='Пользователи', users=users,
                               form2=form2, role=current_user.role)
    else:
        return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    global res

    form2 = SearchForm()
    # if form2.validate_on_submit():
    #     db_sess = db_session.create_session()
    #     goods = db_sess.query(NFT)
    #     for i in goods:
    #         if str(form2.ttle.data).lower() in str(i.title).lower():
    #             res.append(i.id)
    #     return redirect('/search_results')

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form,
                               form2=form2)
    return render_template('login.html', title='Авторизация', form=form,
                           form2=form2)


if __name__ == '__main__':
    main()
