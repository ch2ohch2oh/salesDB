from app import app
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.db import get_db


@app.route('/overview', methods=['GET', 'POST'])
@login_required
def overview():
    """Render overview page"""

    if app.debug:
        print(request.form)

    # date_start = request.form['date_start']
    # date_end = request.form['date_end']
    # if date_start == '':
    date_start = '1234-11-11'
    # if date_end == '':
    date_end = '4321-11-11'

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

# restful api
@app.route('/api/total_orders', methods=['GET'])
def total_orders():
    """
    Return the total number of orders within given time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"select count(*) from sales where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')"))
    print(rows)
    data = dict(total_orders=rows[0][0])
    return jsonify(data)


@app.route('/api/total_revenue', methods=['GET'])
def total_revenue():
    """
    Return the total revenue within given time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"select sum(total) from sales where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')"))
    print(rows)
    data = dict(total_revenue=rows[0][0])
    return jsonify(data)


@app.route('/api/revenue_by_time', methods=['GET'])
def revenue_by_time():
    """
    Return the revenue for each day within the time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = cur.execute(
        f"select salesdate, sum(total) from sales where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD') group by salesdate order by salesdate")
    data = []
    for row in rows:
        data.append({'salesdate': row[0], 'revenue': row[1]})
    return jsonify(data)


@app.route('/api/revenue_by_cat', methods=['GET'])
def revenue_by_cat():
    """
    Return the total revenue for each category within the time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = cur.execute(
        f"""
        select productcategory.name, sum(sales.total)
        from sales, product, productcategory
        where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
            and sales.productID = product.productID
            and product.productID = productcategory.categoryID
        group by productcategory.name
        order by sum(sales.total) desc""")
    data = []
    for row in rows:
        data.append({'cat_name': row[0], 'revenue': row[1]})
    return jsonify(data)