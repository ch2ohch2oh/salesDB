from app import app
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

@app.route('/overview', methods=['GET', 'POST'])
@login_required
def overview():
    """Render overview page"""

    if app.debug:
        print(request.form)
    
    date_start = request.form['date_start']
    date_end = request.form['date_end']
    if date_start == '':
        date_start='1234-11-11'
    if date_end == '':
        date_end='4321-11-11'
    
    # init a basic bar chart:
    # http://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html#bars
    rev_fig = figure(sizing_mode='scale_width')
    rev_fig.vbar(
        x=[1, 2, 3, 4],
        width=0.5,
        bottom=0,
        top=[1.7, 2.2, 4.6, 3.9],
        color='navy'
    )
    trend_script, trend_div = components(rev_fig)
    
    cat_fig = figure(sizing_mode='scale_width')
    cat_fig.vbar(
        x=[1, 2, 3, 4],
        width=0.5,
        bottom=0,
        top=[2.7, 1.2, 3.6, 1.9],
        color='navy'
    )
    cat_js, cat_div = components(cat_fig)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    total_sales = 123123
    total_orders = 321321

    
    html = render_template(
        'overview.html',
        trend_script=trend_script,
        trend_div=trend_div,
        cat_js=cat_js,
        cat_div=cat_div,
        js_resources=js_resources,
        css_resources=css_resources,
        total_sales=total_sales,
        total_orders=total_orders,
        date_start=date_start,
        date_end=date_end,
    )
    return html