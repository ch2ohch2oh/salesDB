from app import app
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, HoverTool
from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.db import get_db, query
from app.plot import formatter, vbar, line

import numpy as np
import pandas as pd

@app.route('/overview', methods=['GET', 'POST'])
def overview():
    """Render overview page
    
    TODO: improve tooltips style
    """
    date_start = request.form.get('date_start', '2018-01-01')
    date_end = request.form.get('date_end', '2018-01-31')
    if request.form.get('time_frame') is None:
        time_frame = 'date'
    else:
        time_frame = request.form.get('time_frame')

    # total revenue
    total_sales = formatter(get_total_revenue(date_start, date_end), 'dollar')

    # total order numbers
    total_orders = formatter(get_total_orders(date_start, date_end))

    # Revenue over time
    time_dict = {'date': 'date', 'ww': 'week', 'mon': 'month', 'q': 'quarter'}
    trend_source = get_revenue_by_time(date_start, date_end, time_frame)
    trend_script, trend_div = line(trend_source, time_dict[time_frame], 'revenue', 'dollar')
    
    # Revenue by categoreis
    cat_data = get_revenue_by_category(date_start, date_end)
    cat_js, cat_div = vbar(cat_data, 'category', 'revenue', 'dollar')

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
 
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


def get_total_orders(date_start, date_end):
    """
    Return the total number of orders within given time range.
    """
    sql = f"select count(*) from sales where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')"
    rows = query(sql)
    return rows[0][0]


def get_total_revenue(date_start, date_end):
    """
    Return the total revenue within given time range.
    """
    db = get_db()
    cur = db.cursor()
    sql =  f"select sum(total) from sales where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')"
    rows = query(sql)
    return rows[0][0]

def get_revenue_by_time(date_start, date_end, time_frame):
    """
    Return the revenue for each day within the time range.
    """
    time_dict = {'date': 'date', 'ww': 'week', 'mon': 'month', 'q': 'quarter'}
    if time_frame == 'date' or time_frame is None: # None is used for switch page default frame
        sql = f"""
        select salesdate, sum(total)
        from sales 
        where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD') 
        group by salesdate order by salesdate
        """
        rows = query(sql)
        df = pd.DataFrame(columns=['date', 'revenue'])
        for row in rows:
            df.loc[len(df), :] = row
        df['date'] = pd.to_datetime(df['date'])
    else:
        sql = f"""
        select to_char(salesdate, '{time_frame}'), sum(total)
        from sales 
        where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
            and salesdate is Not null
        group by to_char(salesdate, '{time_frame}')
        order by to_char(salesdate, '{time_frame}')
        """
        rows = query(sql)
        df = pd.DataFrame(columns=[time_dict[time_frame], 'revenue'])
        for row in rows:
            df.loc[len(df), :] = row
        print(df)
    return df

def get_revenue_by_category(date_start, date_end):
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
