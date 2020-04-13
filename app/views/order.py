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

    # render template
    best_product = get_best_product(date_start, date_end)
    avg_price = '$ ' + str(round(get_avg_price(date_start, date_end) / 1000000, 3)) + ' Million'

    # Order number by categories
    order_num_data = get_num_order_by_cat(date_start, date_end)
    order_num_source = ColumnDataSource(order_num_data)
    order_num_hover = HoverTool(tooltips=[('Category', '@category'), ('Order number', '@order_number{0.00 a}')])
    order_num_fig = figure(x_range = order_num_data.category, sizing_mode='scale_width', height=250, 
        tools=[order_num_hover], toolbar_location=None,)
    order_num_fig.vbar(x='category', top='order_number', source=order_num_source, width=0.9, 
        hover_color='red', hover_fill_alpha=0.8)
    # styling visual
    order_num_fig.xaxis.axis_label = 'Category'
    order_num_fig.xaxis.axis_label_text_font_size = "12pt"
    order_num_fig.xaxis.axis_label_standoff = 10
    order_num_fig.yaxis.axis_label = 'Order numbers'
    order_num_fig.yaxis.axis_label_text_font_size = "12pt"
    order_num_fig.yaxis.axis_label_standoff = 10
    order_num_fig.xaxis.major_label_text_font_size = '11pt'
    order_num_fig.yaxis.major_label_text_font_size = '11pt'
    order_num_fig.yaxis[0].formatter = NumeralTickFormatter(format="$ 0.00 a")
    order_num_js, order_num_div = components(order_num_fig)
    
    # Max, avg, min price for top 6 categories
    price_data = get_max_avg_min_price_by_cat(date_start, date_end)
    price_source = ColumnDataSource(price_data)
    # price_hover = HoverTool(tooltips=[('Category', '@category'), ('Max price', '@max_price{$ 0.00 a}'), 
   #     ('Average price', '@avg_price{$ 0.00 a}'), ('Min price', '@min_price{$ 0.00 a}')])
    price_fig = figure(x_range = price_data.category, sizing_mode='scale_width', height=250, toolbar_location=None,)
    plot1 = price_fig.line(x='category', y='max_price', line_color="#1D91C0", line_width=5, source=price_source,)
    price_fig.add_tools(HoverTool(renderers=[plot1], tooltips=[('Category', '@category'), ('Max price', '@max_price{$ 0.00 a}')],
        mode='vline'))
    plot2 = price_fig.line(x='category', y='avg_price', line_color="#FB8072", line_width=5, source=price_source)
    price_fig.add_tools(HoverTool(renderers=[plot2], tooltips=[('Category', '@category'), ('Average price', '@avg_price{$ 0.00 a}')],
        mode='vline'))
    plot3 = price_fig.line(x='category', y='min_price', line_color="#CAB2D6", line_width=5, source=price_source)
    price_fig.add_tools(HoverTool(renderers=[plot3], tooltips=[('Category', '@category'), ('Min price', '@min_price{$ 0.00 a}')],
        mode='vline'))
    # styling visual
    price_fig.xaxis.axis_label = 'Category'
    price_fig.xaxis.axis_label_text_font_size = "12pt"
    price_fig.xaxis.axis_label_standoff = 10
    price_fig.yaxis.axis_label = 'Price'
    price_fig.yaxis.axis_label_text_font_size = "12pt"
    price_fig.yaxis.axis_label_standoff = 10
    price_fig.xaxis.major_label_text_font_size = '11pt'
    price_fig.yaxis.major_label_text_font_size = '11pt'
    price_fig.yaxis[0].formatter = NumeralTickFormatter(format="$ 0.00 a")
    price_js, price_div = components(price_fig)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
 
    html = render_template(
        'order.html',
        order_num_js=order_num_js,
        order_num_div=order_num_div,
        price_js=price_js,
        price_div=price_div,
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
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['category', 'order_number'])
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
    where rownum < 7
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['category', 'max_price', 'avg_price', 'min_price'])
    for row in rows:
        df.loc[len(df), :] = row
    return df
