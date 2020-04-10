from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app import app
from app.forms import LoginForm
# import views

from .views.overview import overview
from .views.employees import employees

# from .views.customer import customer
# from .views.employee import employee
# from .views.order import order
from app.models import User, user_loader
from app.db import get_db

import logging

# logger = logging.getLogger('salesDB')

# @app.context_processor
# def override_url_for():
#     return dict(url_for=dated_url_for)

# def dated_url_for(endpoint, **values):
#     if endpoint == 'static':
#         filename = values.get('filename', None)
#         if filename:
#             file_path = os.path.join(app.root_path,
#                                  endpoint, filename)
#             values['q'] = int(os.stat(file_path).st_mtime)
#     return url_for(endpoint, **values)

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


@app.route('/test/city')
def test_city():
    db = get_db()
    cur = db.cursor()
    cities = list(cur.execute('select * from city'))
    # print(f'cities: {cities}')
    return render_template('test_city.html', cities=cities)

