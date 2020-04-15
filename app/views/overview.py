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
from app.plot import formatter, vbar

import numpy as np
import pandas as pd

@app.route('/overview', methods=['GET', 'POST'])
def overview():
    """Render overview page
    
    TODO: improve tooltips style
    """
    date_start = request.form.get('date_start', '2018-01-01')
    date_end = request.form.get('date_end', '2018-01-31')
    time_frame = request.form.get('time_frame')

    # total revenue
    total_sales = formatter(get_total_revenue(date_start, date_end), 'dollar')

    # total order numbers
    total_orders = formatter(get_total_orders(date_start, date_end))

    # Revenue over time
    rev_source = ColumnDataSource(get_revenue_by_time(date_start, date_end))
    rev_hover = HoverTool(tooltips=[('Date', '@date{%F}'), ('Revenue', '@revenue{$ 0.00 a}')],
        formatters={'@date': 'datetime'})
    rev_fig = figure(sizing_mode='scale_width', x_axis_type='datetime', height=200,
        tools=[rev_hover], toolbar_location=None,)
    rev_fig.line(x='date', y='revenue', source=rev_source, line_width=2)
    # styling visual
    rev_fig.xaxis.axis_label = 'Time'
    rev_fig.xaxis.axis_label_text_font_size = "12pt"
    rev_fig.xaxis.axis_label_standoff = 10
    rev_fig.yaxis.axis_label = 'Revenue'
    rev_fig.yaxis.axis_label_text_font_size = "12pt"
    rev_fig.yaxis.axis_label_standoff = 10
    rev_fig.xaxis.major_label_text_font_size = '11pt'
    rev_fig.yaxis.major_label_text_font_size = '11pt'
    rev_fig.yaxis[0].formatter = NumeralTickFormatter(format="$ 0.00 a")
    trend_script, trend_div = components(rev_fig)
    
    # Revenue by categoreis
    cat_data = get_revenue_by_category(date_start, date_end)
    cat_js, cat_div = vbar(cat_data, 'category', 'revenue', 'dollar')
    '''
    cat_fig = vbar(cat_data, 'category', 'revenue', 'dollar')
    
    cat_source = ColumnDataSource(cat_data)
    cat_hover = HoverTool(tooltips=[('Category', '@category'), ('Revenue', '@revenue{$ 0.00 a}')])
    cat_fig = figure(x_range = cat_data.category, sizing_mode='scale_width', height=300, tools=[cat_hover], 
        toolbar_location=None,)
    # styling visual
    cat_fig.vbar(x='category', top='revenue', source=cat_source, width=0.9, hover_color='red', hover_fill_alpha=0.8)
    cat_fig.xaxis.axis_label = 'Category'
    cat_fig.xaxis.axis_label_text_font_size = "12pt"
    cat_fig.xaxis.axis_label_standoff = 10
    cat_fig.yaxis.axis_label = 'Revenue'
    cat_fig.yaxis.axis_label_text_font_size = "12pt"
    cat_fig.yaxis.axis_label_standoff = 10
    cat_fig.xaxis.major_label_text_font_size = '10pt'
    cat_fig.yaxis.major_label_text_font_size = '11pt'
    cat_fig.yaxis[0].formatter = NumeralTickFormatter(format="$ 0.00 a")
    cat_js, cat_div = components(cat_fig)
    '''
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

def get_revenue_by_time(date_start, date_end):
    """
    Return the revenue for each day within the time range.
    """
    sql = f"""
    select salesdate, sum(total) from sales 
    where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD') 
    group by salesdate order by salesdate
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['date', 'revenue'])
    for row in rows:
        df.loc[len(df), :] = row
    df['date'] = pd.to_datetime(df['date'])
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
