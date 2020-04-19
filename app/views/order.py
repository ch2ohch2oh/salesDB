from app import app
from bokeh.embed import components
from bokeh.plotting import figure, show, output_file
from bokeh.resources import INLINE
from bokeh.models import NumeralTickFormatter
from bokeh.models import ColumnDataSource, HoverTool
from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.db import get_db, query
from app.plot import formatter, vbar, multiline

import numpy as np
import pandas as pd


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    '''
    Render order page
    '''
    date_start = request.form.get('date_start', '2018-01-01')
    date_end = request.form.get('date_end', '2018-01-31')
    if request.form.get('time_frame') is None:
        time_frame = 'date'
    else:
        time_frame = request.form.get('time_frame')

    # render template
    best_product = get_best_product(date_start, date_end)
    avg_price = formatter(get_avg_price(date_start, date_end), 'dollar')

    # Revenue by categories
    rev_data = get_rev_by_cat(date_start, date_end)
    rev_js, rev_div = vbar(rev_data, 'category', 'revenue', 'dollar')

    # Order number by categories
    order_num_data = get_num_order_by_cat(date_start, date_end)
    order_num_js, order_num_div = vbar(order_num_data, 'category', 'order_number')

    time_dict = {'date': 'date', 'ww': 'week', 'mon': 'month', 'q': 'quarter'}

    # Top 5 revenue category trend
    rev_top5 = rev_data.loc[: 5, 'category'].tolist()
    rev_trend_data = get_cat_trend(date_start, date_end, time_frame, rev_top5, 'revenue')
    rev_trend_js, rev_trend_div = multiline(rev_trend_data, time_dict[time_frame], 'revenue', 'dollar', 
        rev_top5[0], rev_top5[1], rev_top5[2], rev_top5[3], rev_top5[4])

    # top 5 order number category trend
    num_top5 = order_num_data.loc[: 5, 'category'].tolist()
    num_trend_data = get_cat_trend(date_start, date_end, time_frame, num_top5, 'order_number')
    num_trend_js, num_trend_div = multiline(num_trend_data, time_dict[time_frame], 'order_number', 'number',
        num_top5[0], num_top5[1], num_top5[2], num_top5[3], num_top5[4])

    # Max, avg, min price for top 5 categories
    price_data = get_max_avg_min_price_by_cat(date_start, date_end)
    price_js, price_div = multiline(price_data, 'category', 'price', 'dollar', 
        'max_price', 'avg_price', 'min_price')

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
 
    html = render_template(
        'order.html',
        rev_js=rev_js,
        rev_div=rev_div,
        order_num_js=order_num_js,
        order_num_div=order_num_div,
        price_js=price_js,
        price_div=price_div,
        rev_trend_js=rev_trend_js,
        rev_trend_div=rev_trend_div,
        num_trend_js=num_trend_js,
        num_trend_div=num_trend_div,
        js_resources=js_resources,
        css_resources=css_resources,
        best_product=best_product,
        avg_price=avg_price,
        date_start=date_start,
        date_end=date_end,
    )
    return html


def get_best_product(date_start, date_end):
    """
    Return the best selling product rank by total revenue within the time range.
    """
    sql = f"""
    select productname
    from (select productname, count(sales.salesID)
            from sales, product
            where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
                and sales.productID = product.productID
            group by product.PRODUCTNAME
            order by count(sales.salesID) desc)
    where rownum = 1
    """
    rows = query(sql)
    return rows[0][0]


def get_avg_price(date_start, date_end):
    """
    Return the average selling price of all orders within given time range.
    """
    sql = f"""
    select sum / cnt
    from (select count(salesID) as cnt, sum(total) as sum
            from sales
            where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD'))
    """
    rows = query(sql)
    return rows[0][0]


def get_num_order_by_cat(date_start, date_end):
    """
    Return the order numbers for each category within the time range.
    """
    sql = f"""
    select productcategory.name, count(salesID)
    from sales, product, productcategory
    where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
        and sales.productID = product.productID
        and product.categoryID = productcategory.categoryID
    group by productcategory.name
    order by count(salesID) desc
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['category', 'order_number'])
    for row in rows:
        df.loc[len(df), :] = row
    return df


def get_rev_by_cat(date_start, date_end):
    """
    Return the total revenue for each category within the time range.
    """
    sql = f"""
    select productcategory.name, sum(sales.total)
    from sales, product, productcategory
    where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD') 
        and sales.productID = product.productID 
        and product.productID = productcategory.categoryID
    group by productcategory.name
    order by sum(sales.total) desc"""
    rows = query(sql)

    df = pd.DataFrame(columns=['category', 'revenue'])
    for row in rows:
        df.loc[len(df), :] = row
    return df

def get_max_avg_min_price_by_cat(date_start, date_end):
    """
    Return the max, average and minimum price for each category within the time range.
    """
    sql = f"""
    select *
    from (select productcategory.name as category, max(price) as max, avg(price) as avg, min(price) as min
          from sales, product, productcategory
          where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
              and sales.productID = product.productID
              and product.categoryID = productcategory.categoryID
          group by productcategory.name
          order by count(salesID))
    where rownum < 6
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['category', 'max_price', 'avg_price', 'min_price'])
    for row in rows:
        df.loc[len(df), :] = row
    return df


def get_cat_trend(date_start, date_end, time_frame, category, basis='revenue'):
    """
    Return the revenue trend of top 5 category
    """
    basis_dict = {'revenue': 'sum(sales.total)', 'order_number': 'count(sales.salesID)'}
    time_dict = {'date': 'date', 'ww': 'week', 'mon': 'month', 'q': 'quarter'}

    if time_frame == 'date' or time_frame is None: # None is used for switch page default frame
        sql = f'''
        select salesdate, 
            sum(case when category = '{category[0]}' then {basis} else 0 end) as {category[0]},
            sum(case when category = '{category[1]}' then {basis} else 0 end) as {category[1]},
            sum(case when category = '{category[2]}' then {basis} else 0 end) as {category[2]},
            sum(case when category = '{category[3]}' then {basis} else 0 end) as {category[3]},
            sum(case when category = '{category[4]}' then {basis} else 0 end) as {category[4]}
        from
        (select salesdate, productcategory.name as category, {basis_dict[basis]} as {basis}
        from sales, product, productcategory
        where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD') 
            and sales.productID = product.productID 
            and product.productID = productcategory.categoryID
            and productcategory.name in ('{category[0]}', '{category[1]}', '{category[2]}', '{category[3]}', '{category[4]}')
        group by salesdate, productcategory.name)
        group by salesdate
        order by salesdate
        '''
        rows = query(sql)
        df = pd.DataFrame(columns=['date', category[0], category[1], category[2], category[3], category[4]])
        for row in rows:
            df.loc[len(df), :] = row
        df['date'] = pd.to_datetime(df['date'])
    else:
        sql = f'''
        select range, 
            sum(case when category = '{category[0]}' then {basis} else 0 end) as {category[0]},
            sum(case when category = '{category[1]}' then {basis} else 0 end) as {category[1]},
            sum(case when category = '{category[2]}' then {basis} else 0 end) as {category[2]},
            sum(case when category = '{category[3]}' then {basis} else 0 end) as {category[3]},
            sum(case when category = '{category[4]}' then {basis} else 0 end) as {category[4]}
        from
        (select to_char(salesdate, '{time_frame}') as range, productcategory.name as category, {basis_dict[basis]} as {basis}
        from sales, product, productcategory
        where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD') 
            and salesdate is Not null
            and sales.productID = product.productID 
            and product.productID = productcategory.categoryID
            and productcategory.name in ('{category[0]}', '{category[1]}', '{category[2]}', '{category[3]}', '{category[4]}')
        group by to_char(salesdate, '{time_frame}'), productcategory.name)
        group by range
        order by range
        '''
        rows = query(sql)
        df = pd.DataFrame(columns=[time_dict[time_frame], category[0], category[1], category[2], category[3], category[4]])
        for row in rows:
            df.loc[len(df), :] = row
    return df

def get_revenue_by_category1(date_start, date_end):

    sql = f"""
    select productcategory.name, sum(sales.total)
    from sales, product, productcategory
    where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD') 
        and sales.productID = product.productID 
        and product.productID = productcategory.categoryID
    group by productcategory.name
    order by sum(sales.total) desc"""
    res = query(sql)
    return res

@app.route('/ct1')
def get_revenue_by_category2():
    date_start = request.form.get('date_start', '2018-01-01')
    date_end = request.form.get('date_end', '2018-01-31')
    res = []
    for tup in get_revenue_by_category1(date_start,date_end):

        res.append({"name": (tup[0]), "value": int(tup[1]/1000000000)})
    return jsonify({"data": res})
