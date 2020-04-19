from app import app
from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import brewer
from bokeh.models import NumeralTickFormatter
from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.db import get_db, query
from app.plot import vbar, vbar_stack, line, multiline

import numpy as np
import pandas as pd
import math


@app.route('/customer', methods=['GET', 'POST'])
@login_required
def customer():
    '''
    Render order page
    '''
    date_start = request.form.get('date_start', '2018-01-01')
    date_end = request.form.get('date_end', '2018-01-31')
    if request.form.get('time_frame') is None:
        time_frame = 'date'
    else:
        time_frame = request.form.get('time_frame')

    time_dict = {'date': 'date', 'ww': 'week', 'mon': 'month', 'q': 'quarter'}

    # Active customer number trend
    act_data = get_customer_trend(date_start, date_end, time_frame)
    act_js, act_div = line(act_data, time_dict[time_frame], 'customer_number', 'number')

    # Order number by geo for each category
    geo_data = get_num_order_by_geo(date_start, date_end)
    geo_js, geo_div = vbar_stack(geo_data, 'category', 'order_number', 'number', brewer['Spectral'][9], 1, 
        'northeast', 'east', 'southeast', 'north', 'south', 'west', 'southwest', 'northwest', 'middle')

    # Geo order trend
    geo_trend_data = get_geo_order_trend(date_start, date_end, time_frame)
    geo_trend_js, geo_trend_div = multiline(geo_trend_data, time_dict[time_frame], 'order_number', 'number',
        'northeast', 'east', 'southeast', 'north', 'south', 'west', 'southwest', 'northwest', 'middle')

    # Repeat order (same prodcut > 2 times)
    repeat_data = get_repeat_order_by_time(date_start, date_end)
    repeat_js, repeat_div = vbar_stack(repeat_data, 'category', 'order_number', 'number', ["#3cba54", "#f4c20b"], 0.8, 
        'repeated', 'unrepeated')

    # Order number by gender for each category
    gender_data = get_num_order_by_gender_cat(date_start, date_end)
    gender_js, gender_div = vbar_stack(gender_data, 'category', 'order_number', 'number', ["#da3337", "#4986ec"], 0.8, 
        'female', 'male')

    # Customer state distribution for top 10 states
    customer_geo_data = get_customer_by_geo(date_start, date_end)
    customer_geo_js, customer_geo_div = vbar(customer_geo_data, 'state', 'number', 'number')

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
 
    html = render_template(
        'customer.html',
        act_js=act_js,
        act_div=act_div,
        customer_geo_js=customer_geo_js,
        customer_geo_div=customer_geo_div,
        repeat_js=repeat_js,
        repeat_div=repeat_div,
        gender_js=gender_js,
        gender_div=gender_div,
        geo_js=geo_js,
        geo_div=geo_div,
        geo_trend_js=geo_trend_js,
        geo_trend_div=geo_trend_div,
        js_resources=js_resources,
        css_resources=css_resources,
        date_start=date_start,
        date_end=date_end,
    )
    return html


def get_customer_trend(date_start, date_end, time_frame):
    """
    Return the trend of active customer number in the time range
    """
    time_dict = {'date': 'date', 'ww': 'week', 'mon': 'month', 'q': 'quarter'}
    if time_frame == 'date' or time_frame is None: # None is used for switch page default frame
        sql = f"""
        select salesdate, count(unique customerID)
        from sales 
        where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD') 
        group by salesdate
        order by salesdate
        """
        rows = query(sql)
        df = pd.DataFrame(columns=['date', 'customer_number'])
        for row in rows:
            df.loc[len(df), :] = row
        df['date'] = pd.to_datetime(df['date'])
    else:
        sql = f"""
        select to_char(salesdate, '{time_frame}'), count(unique customerID)
        from sales 
        where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
            and salesdate is Not null
        group by to_char(salesdate, '{time_frame}')
        order by to_char(salesdate, '{time_frame}')
        """
        rows = query(sql)
        df = pd.DataFrame(columns=[time_dict[time_frame], 'customer_number'])
        for row in rows:
            df.loc[len(df), :] = row
    return df


def get_num_order_by_geo(date_start, date_end):
    """
    Return the number of orders in different geo region for each category in time range.
    """
    sql = f"""
    with geo_cat as
        (select count(salesID) as order_num, city.zipcode as zipcode, productcategory.name as category
        from customer, sales, product, productcategory, city
        where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
            and customer.customerID = sales.customerID
            and sales.productID = product.productID
            and product.categoryID = productcategory.categoryID
            and customer.city = city.cityID
        group by zipcode, productcategory.name)
    select category,
        sum(case when zipcode between 0 and 19999 then order_num else 0 end) as northeast, 
        sum(case when zipcode between 20000 and 29999 then order_num else 0 end) as east,
        sum(case when zipcode between 30000 and 39999 then order_num else 0 end) as southeast,
        sum(case when zipcode between 40000 and 59999 then order_num else 0 end) as north,
        sum(case when zipcode between 70000 and 79999 then order_num else 0 end) as south,
        sum(case when zipcode between 84000 and 95000 then order_num else 0 end) as west,
        sum(case when zipcode between 95001 and 96999 then order_num else 0 end) as southwest,
        sum(case when zipcode between 97000 and 99999 then order_num else 0 end) as nouthwest,
        sum(case when zipcode between 60000 and 69999 or zipcode between 80000 and 83999 then order_num else 0 end) as middle
    from geo_cat
    group by category
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['category', 'northeast', 'east', 'southeast', 'north', 'south', 'west', 'southwest', 
        'northwest', 'middle'])
    for row in rows:
        df.loc[len(df), :] = row
    return df


def get_geo_order_trend(date_start, date_end, time_frame):
    """
    Return trend of order number in different geo region in time range.
    """
    basis_dict = {'revenue': 'sum(sales.total)', 'order_number': 'count(sales.salesID)'}
    time_dict = {'date': 'date', 'ww': 'week', 'mon': 'month', 'q': 'quarter'}

    if time_frame == 'date' or time_frame is None: # None is used for switch page default frame
        sql = f'''
        select salesdate,
            sum(case when zipcode between 0 and 19999 then order_num else 0 end) as northeast, 
            sum(case when zipcode between 20000 and 29999 then order_num else 0 end) as east,
            sum(case when zipcode between 30000 and 39999 then order_num else 0 end) as southeast,
            sum(case when zipcode between 40000 and 59999 then order_num else 0 end) as north,
            sum(case when zipcode between 70000 and 79999 then order_num else 0 end) as south,
            sum(case when zipcode between 84000 and 95000 then order_num else 0 end) as west,
            sum(case when zipcode between 95001 and 96999 then order_num else 0 end) as southwest,
            sum(case when zipcode between 97000 and 99999 then order_num else 0 end) as nouthwest,
            sum(case when zipcode between 60000 and 69999 or zipcode between 80000 and 83999 then order_num else 0 end) as middle
        from
        (select salesdate, count(salesID) as order_num, city.zipcode as zipcode
        from customer, sales, city
        where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
            and customer.customerID = sales.customerID
            and customer.city = city.cityID
        group by salesdate, zipcode)
        group by salesdate
        order by salesdate
        '''
        rows = query(sql)
        df = pd.DataFrame(columns=['date', 'northeast', 'east', 'southeast', 'north', 'south', 'west', 'southwest', 
            'northwest', 'middle'])
        for row in rows:
            df.loc[len(df), :] = row
        df['date'] = pd.to_datetime(df['date'])
    else:
        sql = f'''
        select range,
            sum(case when zipcode between 0 and 19999 then order_num else 0 end) as northeast, 
            sum(case when zipcode between 20000 and 29999 then order_num else 0 end) as east,
            sum(case when zipcode between 30000 and 39999 then order_num else 0 end) as southeast,
            sum(case when zipcode between 40000 and 59999 then order_num else 0 end) as north,
            sum(case when zipcode between 70000 and 79999 then order_num else 0 end) as south,
            sum(case when zipcode between 84000 and 95000 then order_num else 0 end) as west,
            sum(case when zipcode between 95001 and 96999 then order_num else 0 end) as southwest,
            sum(case when zipcode between 97000 and 99999 then order_num else 0 end) as nouthwest,
            sum(case when zipcode between 60000 and 69999 or zipcode between 80000 and 83999 then order_num else 0 end) as middle
        from
        (select to_char(salesdate, '{time_frame}') as range, count(salesID) as order_num, city.zipcode as zipcode
        from customer, sales, city
        where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
            and customer.customerID = sales.customerID
            and customer.city = city.cityID
        group by to_char(salesdate, '{time_frame}'), zipcode)
        group by range
        order by range
        '''
        rows = query(sql)
        df = pd.DataFrame(columns=[time_dict[time_frame], 'northeast', 'east', 'southeast', 'north', 'south', 'west', 
            'southwest', 'northwest', 'middle'])
        for row in rows:
            df.loc[len(df), :] = row
    return df

def get_repeat_order_by_time(date_start, date_end):
    """
    Return the number of repeated purchases (same prodcut > 2 times)
    and the total number of orders for different category with the time range.
    """
    sql = f"""
    with orders as 
        (select sales.customerID as customer_id, productcategory.name as category, sales.salesID as salesID
         from customer, sales, product, productcategory
         where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
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
          having count(salesID) > 2
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


def get_num_order_by_gender_cat(date_start, date_end):
    """
    Return the number of male and female purchasing orders for each category in time range.
    """
    sql = f"""
    with gender_cat as 
        (select count(salesID) as order_num, customer.gender as gender, productcategory.name as category
         from customer, sales, product, productcategory
         where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
            and customer.customerID = sales.customerID
            and sales.productID = product.productID
            and product.categoryID = productcategory.categoryID
         group by customer.gender, productcategory.name)
    select category,
        sum(case when gender = 'Male' then order_num else 0 end) as male, 
        sum(case when gender = 'Female' then order_num else 0 end) as female
    from gender_cat
    group by category
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['category', 'female', 'male'])
    for row in rows:
        df.loc[len(df), :] = row
    return df


def get_customer_by_geo(date_start, date_end):
    """
    Return the customer numbers for top 10 states
    """
    sql = f"""
    select *
    from
    (select count(customer.customerID) as num, city.state as state
     from customer, city
     where customer.city = city.cityID
     group by city.state
     order by count(customer.customerID) desc)
    where rownum < 11
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['number', 'state'])
    for row in rows:
        df.loc[len(df), :] = row
    return df