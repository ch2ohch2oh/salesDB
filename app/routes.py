from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app import app
from app.forms import LoginForm

from .views.overview import overview
from app.models import User, user_loader

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('overview'))
    
    form = LoginForm(request.form)
    if app.debug:
        print(f'username: {request.form}')
        print(f'username: {form.username.data}')
        print(f'password: {form.password.data}')

    if form.validate_on_submit():
        if not User.check_password(form.username.data, form.password.data):
            print('Invalid username or password')
            flash('Invalid username or password')
            return redirect(url_for('login'))
        user = user_loader(form.username.data)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('overview')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/customer', methods=['GET', 'POST'])
@login_required
def customer():
    pass

@app.route('/employee', methods=['GET', 'POST'])
@login_required
def employee():
    pass

@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    pass