from app import app
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.db import get_db, query

import pandas as pd
import numpy as np
import math

@app.route('/employees', methods=['GET', 'POST'])
@login_required
def employees():
    """
    Render employee page
    """
    date_start = request.form.get('date_start', '2018-01-01')
    date_end = request.form.get('date_end', '2018-03-12')

    revenue_total = get_employee_revenue_total(date_start, date_end)

    most_revenue_name = revenue_total.loc[0, 'name']
    revenue_mean = revenue_total.revenue.mean()
    revenue_range = revenue_total.revenue.max() - revenue_total.revenue.min()

    fig_revenue_total = figure(sizing_mode='scale_width', height=200,
        y_range=revenue_total.name,
        x_range=(revenue_mean - revenue_range / 2 * 1.5, 
            revenue_mean + revenue_range / 2 * 1.5))
    fig_revenue_total.hbar(y=revenue_total.name, 
        right=revenue_total.revenue, height=0.5)
    fig_revenue_total.xaxis.major_label_orientation = math.pi/2

    orders_total = get_employee_orders_total(date_start, date_end)
    most_orders_name = orders_total.loc[0, 'name']
    orders_mean = orders_total.orders.mean()
    orders_range = orders_total.orders.max() - orders_total.orders.min()

    fig_orders_total = figure(sizing_mode='scale_width', height=200,
        x_range=orders_total.name,
        y_range=(orders_mean - orders_range / 2 * 1.5,
            orders_mean + orders_range / 2 * 1.5))
    fig_orders_total.vbar(x=orders_total.name, 
        top=orders_total.orders, width=0.9)
    fig_orders_total.xaxis.major_label_orientation = math.pi/2

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    js_revenue_total, div_revenue_total = components(fig_revenue_total)
    js_orders_total, div_orders_total = components(fig_orders_total)

    html = render_template(
        'employees.html',
        js_resources=js_resources,
        css_resources=css_resources,
        div_revenue_total=div_revenue_total,
        js_revenue_total=js_revenue_total,
        div_orders_total=div_orders_total,
        js_orders_total=js_orders_total,
        most_orders_name=most_orders_name,
        most_revenue_name=most_revenue_name,
        date_start=date_start,
        date_end=date_end,
    )
    return html

def get_employee_revenue_orders_total(date_start, date_end):
    """

    """
    sql = f"""
    select employee.name, sum(sales.total), count(*)
    from sales, employee
    where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
        and sales.employeeID = employee.employeeID
    group by employee.name
    order by sum(sales.total) desc
    """
    rows = query(sql)
    df = pd.DataFrame(rows, columns=['name', 'revenue', 'orders'])
    print(df.head())
    return df


def get_employee_revenue_total(date_start, date_end):
    """

    """
    sql = f"""
    select employee.name, sum(sales.total)
    from sales, employee
    where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
        and sales.employeeID = employee.employeeID
    group by employee.name
    order by sum(sales.total) desc
    """
    rows = query(sql)
    df = pd.DataFrame(rows, columns=['name', 'revenue'])
    print(df.head())
    return df

def get_employee_orders_total(date_start, date_end):
    """
    """
    sql = f"""
    select employee.name as name, count(sales.salesID) as order_number
    from sales, employee
    where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
        and sales.employeeID = employee.employeeID
    group by employee.name
    order by count(sales.salesID) desc"""
    rows = query(sql)
    df = pd.DataFrame(rows, columns=['name', 'orders'])
    # print(df.head())
    return df

@app.route('/api/best_employee', methods=['GET'])
def best_employee():
    """
    Return the best seller employee ranked by total revenue within the time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"""
        select name
        from (select employee.name as name, sum(sales.total)
              from sales, employee
              where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
                  and sales.employeeID = employee.employeeID
              
              )
        where rownum = 1"""))
    data = dict(best_employee=rows[0][0])
    return jsonify(data)

@app.route('/api/avg_selling_per', methods=['GET'])
def avg_selling_per():
    """
    Return the average order numbers of each employee within the time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"""
        select sum(order_num) / count(name)
        from (select count(sales.salesID) as order_num, employee.name as name
              from sales, employee
              where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
                  and sales.employeeID = employee.employeeID
              group by employee.name
              order by count(sales.salesID) desc)"""))
    data = dict(avg_selling_per=rows[0][0])
    return jsonify(data)

@app.route('/api/num_order_by_employee', methods=['GET'])
def num_order_by_employee():
    """
    Return the order numbers and revenue of each employee within the time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"""
        select employee.name as name, count(sales.salesID) as order_number, sum(sales.total) as revenue
        from sales, employee
        where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
            and sales.employeeID = employee.employeeID
        group by employee.name
        order by count(sales.salesID) desc"""))
    data = []
    for row in rows:
        data.append({'employee': row[0], 'order numbers': row[1], 'revenue': row[2]})
    return jsonify(data)

# optional and under construction
@app.route('/api/top5_employee_monthly', methods=['GET'])
def top5_employee_monthly():
    """
    Return the monthly order numbers and revenue trending of 2018 year top 5 employee ranked by revenue.
    """
    date_start = 20180101
    date_end = 20181231
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"""
        select employee.name as name, count(sales.salesID) as order_number, sum(sales.total) as revenue
        from sales, employee
        where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
            and sales.employeeID = employee.employeeID
        group by employee.name
        order by sum(sales.salesID) desc)"""))
    data = []
    for row in rows:
        data.append({'employee': row[0], 'order number': row[1], 'revenue': row[2]})
    return jsonify(data)