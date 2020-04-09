from app import app
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.db import get_db


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    pass

# restful api
@app.route('/api/best_product', methods=['GET'])
def best_product():
    """
    Return the best selling product rank by total revenue within the time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"""
        select productname
        from (select productname, count(sales.salesID)
              from sales, product
              where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
                  and sales.productID = product.productID
              group by product.PRODUCTNAME
              order by count(sales.salesID) desc)
        where rownum = 1"""))
    data = dict(best_product=rows[0][0])
    return jsonify(data)

@app.route('/api/avg_price', methods=['GET'])
def avg_price():
    """
    Return the average selling price of all orders within given time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"""
        select sum / cnt
        from (select count(salesID) as cnt, sum(total) as sum
              from sales
              where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD'))"""))
    data = dict(avg_price=rows[0][0])
    return jsonify(data)

@app.route('/api/num_order_by_cat', methods=['GET'])
def num_order_by_cat():
    """
    Return the order numbers for each category within the time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = cur.execute(
        f"""
        select productcategory.name, count(salesID)
        from sales, product, productcategory
        where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
            and sales.productID = product.productID
            and product.categoryID = productcategory.categoryID
        group by productcategory.name
        order by count(salesID) desc""")
    data = []
    for row in rows:
        data.append({'cat_name': row[0], 'revenue': row[1]})
    return jsonify(data)

@app.route('/api/max_avg_min_price_by_cat', methods=['GET'])
def max_avg_min_price_by_cat():
    """
    Return the max, average and minimum price for each category within the time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = cur.execute(
        f"""
        select productcategory.name as category, max(price) as max, avg(price) as avg, min(price) as min
        from sales, product, productcategory
        where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
            and sales.productID = product.productID
            group by product.PRODUCTNAME
        group by productcategory.name""")
    data = []
    for row in rows:
        data.append({'cat_name': row[0], 'revenue': row[1]})
    return jsonify(data)