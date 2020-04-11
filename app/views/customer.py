from app import app
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import brewer
from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.db import get_db, query

import numpy as np
import pandas as pd


@app.route('/customer', methods=['GET', 'POST'])
@login_required
def customer():
    '''
    Render order page
    '''
    date_start = request.form.get('date_start', '2018-01-01')
    date_end = request.form.get('date_end', '2018-03-12')

    # Customer geo distribution
    customer_geo_data = get_customer_by_geo(date_start, date_end)
    customer_geo_source = ColumnDataSource(customer_geo_data)
    customer_geo_hover = HoverTool(tooltips=[('Number', '@number'), ('Zipcode', '@zipcode')])
    customer_geo_fig = figure(x_range = customer_geo_data.category, sizing_mode='scale_width', height=200, 
        tools=[customer_geo_hover],)
    customer_geo_fig.vbar(x='category', top='customer_geober', source=customer_geo_source, width=0.9, 
        hover_color='red', hover_fill_alpha=0.8)
    customer_geo_js, customer_geo_div = components(customer_geo_fig)

    # Repeat order (same prodcut > 3 times)
    repeat_data = get_repeat_order_by_time(date_start, date_end)
    repeat_source = ColumnDataSource(repeat_data)
    repeat_hover = HoverTool(tooltips=[('Category', '@category'), ('Repeated', '@repeated'), 
        ('Unrepeated', '@unrepeated')])
    repeat_fig = figure(x_range = repeat_data.category, sizing_mode='scale_width', height=200, tools=[repeat_hover])
    names = ['repeated', 'unrepeated']
    repeat_fig.vbar_stack(names, x='category', width=0.9, alpha=0.5, color=["blue", "red"], legend_label=names, 
        source=repeat_source, hover_color='yellow', hover_fill_alpha=0.8)
    repeat_js, repeat_div = components(repeat_fig)

    # Order number by gender for each category
    gender_data = get_num_order_by_gender_cat(date_start, date_end)
    gender_source = ColumnDataSource(gender_data)
    gender_hover = HoverTool(tooltips=[('Category', '@category'), ('Male', '@male'), ('Female', '@female')])
    gender_fig = figure(x_range = gender_data.category, sizing_mode='scale_width', height=200, 
        tools=[gender_hover])
    gender = ['female', 'male']
    gender_fig.vbar_stack(gender, x='category', width=0.9, alpha=0.5, color=["purple", "green"], legend_label=gender, 
        source=gender_source,hover_color='yellow', hover_fill_alpha=0.8)
    gender_js, gender_div = components(gender_fig)

    # Order number by geo for each category
    geo_data = get_num_order_by_geo(date_start, date_end)
    geo_source = ColumnDataSource(geo_data)
    ['category', 'northeast', 'east', 'southeast', 'north', 'south', 'west', 'southwest', 
        'nouthwest', 'middle']
    geo_hover = HoverTool(tooltips=[('Category', '@category'), ('Northeast', '@northeast'), ('East', '@east'), 
        ('Southeast', '@southeast'), ('North', '@north'), ('South', '@south'), ('West', '@west'), ('Southwest', '@southwest'), 
        ('Northwest', '@northwest'), ('Middle', '@middle')])
    geo_fig = figure(x_range = geo_data.category, sizing_mode='scale_width', height=200, 
        tools=[geo_hover])
    region = ['East', 'West','North', 'South', 'Northeast', 'Southeast', 'Southwest', 'Nouthwest', 'Middle']
    geo_fig.vbar_stack(region, x='category', width=0.9, alpha=0.5, color=brewer['Spectral'][9], legend_label=names,
        source=geo_source, hover_color='yellow', hover_fill_alpha=0.8)
    geo_js, geo_div = components(geo_fig)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
 
    html = render_template(
        'order.html',
        customer_geo_js=customer_geo_js,
        customer_geo_div=customer_geo_div,
        repeat_js=repeat_js,
        repeat_div=repeat_div,
        gender_js=repeat_js,
        gender_div=repeat_div,
        geo_js=repeat_js,
        geo_div=repeat_div,
        js_resources=js_resources,
        css_resources=css_resources,
        date_start=date_start,
        date_end=date_end,
    )
    return html

# restful api
def get_customer_by_geo(date_start, date_end):
    """
    Return the customer numbers for each zipcode.
    """
    db = get_db()
    cur = db.cursor()
    sql = f"""
    select count(customer.customerID) as num, city.zipcode as zipcode
    from customer, city
    where customer.city = city.cityID
    group by city.zipcode
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['number', 'zipcode'])
    for row in rows:
        df.loc[len(df), :] = row
    return df


def get_repeat_order_by_time(date_start, date_end):
    """
    Return the number of repeated purchases (same prodcut > 3 times)
    and the total number of orders for different category with the time range.
    """
    sql = f"""
    with orders as 
        (select sales.customerID as customer_id, productcategory.name as category, sales.salesID as salesID
            from customer, sales, product, productcategory
            where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date({date_end}, 'YYYYMMDD')
            and customer.customerID = sales.customerID
            and sales.productID = product.productID
                and product.categoryID = productcategory.categoryID)
    select avg(number_total), sum(number_repeat) as repeat, cat1 as category
    from (select count(salesID) as number_total, category as cat1
            from orders
            group by category
            )
            inner join
            (select count(salesID) as number_repeat, category as cat2
            from orders
            group by customer_id, category
            having count(salesID) > 3
            )
        on cat1 = cat2
    group by cat1
    """
    # the reason use avg(number_total) is after the group by, 
    # for the same category, each row has same value for number_total
    rows = query(sql)
    df = pd.DataFrame(columns=['total', 'repeated', 'category'])
    for row in rows:
        df.loc[len(df), :] = row
    df['unrepeated'] = df['total'] - df['repeated']
    return df

# 需要给 customer table 添加随机性别，可以使用 excel 完成
def get_num_order_by_gender_cat(date_start, date_end):
    """
    Return the number of male and female purchasing orders for each category in time range.
    """
    sql = f"""
    with gender_cat as 
        (select saleID, customer.gender as gender, productcategory.name as category
         from customer, sales, product, productcategory
         where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date({date_end}, 'YYYYMMDD')
            and customer.customerID = sales.customerID
            and sales.productID = product.productID
            and product.categoryID = productcategory.categoryID)
    select female, male, category
    from (select count(salesID) as female, category
          from gender_cat where gender = 'Female'
          group by category)
         join
         (select count(salesID) as male, category
          from gender_cat where gender = 'Male'
          group by category)
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['female', 'male', 'category'])
    for row in rows:
        df.loc[len(df), :] = row
    return df

# 需要 zipcode 的范围确定东西南北，大致确定
def get_num_order_by_geo(date_start, date_end):
    """
    Return the number of orders in different geo region for each category in time range.
    """
    sql = f"""
    with gender_cat as
        (select count(salesID) as order_num, city.zipcode as zipcode, productcategory.name as category
         from customer, sales, product, productcategory, city
         where salesdate between to_date('2018-01-01', 'YYYY-MM-DD') and to_date('2018-01-02', 'YYYY-MM-DD')
             and customer.customerID = sales.customerID
             and sales.productID = product.productID
             and product.categoryID = productcategory.categoryID
             and customer.city = city.cityID
         group by zipcode, productcategory.name)
    select
        case when zipcode between 0 and 19999 then 'Northeast'
        when zipcode between 20000 and 29999 then 'East'
        when zipcode between 30000 and 39999 then 'Southeast'
        when zipcode between 40000 and 59999 then 'North'
        when zipcode between 70000 and 79999 then 'South'
        when zipcode between 88900 and 95000 then 'West'
        when zipcode between 95001 and 96999 then 'Southwest'
        when zipcode between 97000 and 99999 then 'Nouthwest'
        else 'Middle' end as range, sum(order_num), category
    from gender_cat
    group by
        case when zipcode between 0 and 19999 then 'Northeast'
        when zipcode between 20000 and 29999 then 'East'
        when zipcode between 30000 and 39999 then 'Southeast'
        when zipcode between 40000 and 59999 then 'North'
        when zipcode between 70000 and 79999 then 'South'
        when zipcode between 88900 and 95000 then 'West'
        when zipcode between 95001 and 96999 then 'Southwest'
        when zipcode between 97000 and 99999 then 'Nouthwest'
        else 'Middle' end, category
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['category', 'northeast', 'east', 'southeast', 'north', 'south', 'west', 'southwest', 
        'northwest', 'middle'])
    for row in rows:
        df.loc[len(df), :] = row
    return df