from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm

blueprint = Blueprint('auth', __name__, template_folder='templates')

# Процесс регистрации пользователя
@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, message="Пароли не совпадают")
        
        db_sess = db_session.create_session()
        try:
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', form=form, message="Такой пользователь уже существует")
            
            user = User(
                name=form.name.data,
                email=form.email.data,
                address=form.address.data,
                city=form.city.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            flash('Регистрация успешна! Войдите в систему', 'success')
            return redirect(url_for('auth.login'))
        finally:
            db_sess.close()
    
    return render_template('register.html', form=form)

# Процесс авторизации пользователя
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash(f'Добро пожаловать, {user.name}!', 'success')
                return redirect(url_for('catalog.index'))
            flash('Неверный email или пароль', 'danger')
        finally:
            db_sess.close()
    
    return render_template('login.html', form=form)

# Процесс выхода пользователя из аккаунта
@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('catalog.index'))