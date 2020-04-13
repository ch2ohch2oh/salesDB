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

import numpy as np
import pandas as pd


@app.route('/customer', methods=['GET', 'POST'])
@login_required
def customer():
    '''
    Render order page
    '''
    date_start = request.form.get('date_start', '2018-01-01')
    date_end = request.form.get('date_end', '2018-01-31')

    # Customer geo distribution
    customer_geo_data = get_customer_by_geo(date_start, date_end)
    customer_geo_source = ColumnDataSource(customer_geo_data)
    customer_geo_hover = HoverTool(tooltips=[('Number', '@number{0.00 a}'), ('City name', '@city_name')])
    customer_geo_fig = figure(x_range = customer_geo_data.city_name, sizing_mode='scale_width', height=200, 
        tools=[customer_geo_hover], toolbar_location=None,)
    customer_geo_fig.vbar(x='city_name', top='number', source=customer_geo_source, width=0.9, 
        hover_color='red', hover_fill_alpha=0.8)
    # styling visual
    customer_geo_fig.xaxis.axis_label = 'Category'
    customer_geo_fig.xaxis.axis_label_text_font_size = "12pt"
    customer_geo_fig.xaxis.axis_label_standoff = 10
    customer_geo_fig.yaxis.axis_label = 'Order numbers'
    customer_geo_fig.yaxis.axis_label_text_font_size = "12pt"
    customer_geo_fig.yaxis.axis_label_standoff = 10
    customer_geo_fig.xaxis.major_label_text_font_size = '11pt'
    customer_geo_fig.yaxis.major_label_text_font_size = '11pt'
    customer_geo_fig.yaxis[0].formatter = NumeralTickFormatter(format="$ 0.00 a")
    customer_geo_js, customer_geo_div = components(customer_geo_fig)
    

    # Repeat order (same prodcut > 3 times)
    repeat_data = get_repeat_order_by_time(date_start, date_end)
    repeat_source = ColumnDataSource(repeat_data)
    names = ['repeated', 'unrepeated']
    repeat_fig = figure(x_range = repeat_data.category, sizing_mode='scale_width', height=200, 
        tools='hover', tooltips='$name: @$name{0.00 a}', toolbar_location=None,)
    repeat_fig.vbar_stack(names, x='category', width=0.9, alpha=0.8, color=[ "#3cba54", "#f4c20b"], legend_label=names, 
        source=repeat_source,)
    # styling visual
    repeat_fig.xaxis.axis_label = 'Category'
    repeat_fig.xaxis.axis_label_text_font_size = "12pt"
    repeat_fig.xaxis.axis_label_standoff = 10
    repeat_fig.yaxis.axis_label = 'Order numbers'
    repeat_fig.yaxis.axis_label_text_font_size = "12pt"
    repeat_fig.yaxis.axis_label_standoff = 10
    repeat_fig.xaxis.major_label_text_font_size = '11pt'
    repeat_fig.yaxis.major_label_text_font_size = '11pt'
    repeat_fig.yaxis[0].formatter = NumeralTickFormatter(format="0.00 a")
    repeat_js, repeat_div = components(repeat_fig)

    # Order number by gender for each category
    gender_data = get_num_order_by_gender_cat(date_start, date_end)
    gender_source = ColumnDataSource(gender_data)
    gender_fig = figure(x_range = gender_data.category, sizing_mode='scale_width', height=200, 
        tools='hover', tooltips='$name: @$name{$ 0.00 a}', toolbar_location=None,)
    gender = ['female', 'male']
    gender_fig.vbar_stack(gender, x='category', width=0.9, alpha=0.6, color=["#da3337", "#4986ec"], legend_label=gender, 
        source=gender_source)
    # styling visual
    gender_fig.xaxis.axis_label = 'Category'
    gender_fig.xaxis.axis_label_text_font_size = "12pt"
    gender_fig.xaxis.axis_label_standoff = 10
    gender_fig.yaxis.axis_label = 'Order numbers'
    gender_fig.yaxis.axis_label_text_font_size = "12pt"
    gender_fig.yaxis.axis_label_standoff = 10
    gender_fig.xaxis.major_label_text_font_size = '11pt'
    gender_fig.yaxis.major_label_text_font_size = '11pt'
    gender_fig.yaxis[0].formatter = NumeralTickFormatter(format="0.00 a")
    gender_js, gender_div = components(gender_fig)

    # Order number by geo for each category
    geo_data = get_num_order_by_geo(date_start, date_end)
    geo_source = ColumnDataSource(geo_data)
    geo_fig = figure(x_range = geo_data.category, sizing_mode='scale_width', height=200, tools='hover', 
        tooltips='$name: @$name{$ 0.00 a}', toolbar_location=None, )
    region = ['northeast', 'east', 'southeast', 'north', 'south', 'west', 'southwest', 
        'northwest', 'middle']
    geo_fig.vbar_stack(region, x='category', width=0.9, color=brewer['Spectral'][9], legend_label=region,
        source=geo_source)
    # styling visual
    geo_fig.xaxis.axis_label = 'Category'
    geo_fig.xaxis.axis_label_text_font_size = "12pt"
    geo_fig.xaxis.axis_label_standoff = 10
    geo_fig.yaxis.axis_label = 'Order Numbers'
    geo_fig.yaxis.axis_label_text_font_size = "12pt"
    geo_fig.yaxis.axis_label_standoff = 10
    geo_fig.xaxis.major_label_text_font_size = '11pt'
    geo_fig.yaxis.major_label_text_font_size = '11pt'
    geo_fig.yaxis[0].formatter = NumeralTickFormatter(format="0.00 a")
    geo_js, geo_div = components(geo_fig)
    # show(geo_fig)

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
 
    html = render_template(
        'customer.html',
        customer_geo_js=customer_geo_js,
        customer_geo_div=customer_geo_div,
        repeat_js=repeat_js,
        repeat_div=repeat_div,
        gender_js=gender_js,
        gender_div=gender_div,
        geo_js=geo_js,
        geo_div=geo_div,
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
    sql = f"""
    select count(customer.customerID) as num, city.cityname as city_name
    from customer, city
    where customer.city = city.cityID
    group by city.cityname
    """
    rows = query(sql)
    df = pd.DataFrame(columns=['number', 'city_name'])
    for row in rows:
        df.loc[len(df), :] = row
    print(df)
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
    print(df)
    return df

# 需要给 customer table 添加随机性别，可以使用 excel 完成
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

# 需要 zipcode 的范围确定东西南北，大致确定
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