from app import app
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.models import NumeralTickFormatter
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.layouts import gridplot
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
    date_end = request.form.get('date_end', '2018-01-31')
    
    # average order_numbers
    avg = get_avg_selling_per(date_start, date_end)
    avg_order = avg[0][0]
    if 10**3 < avg_order < 10**6:
        avg_order = str(round(avg_order / 10**3, 3)) + ' Thousand'
    elif 10**6 < avg_order < 10**9:
        avg_order = str(round(avg_order / 10**6, 3)) + ' Million'
    elif avg_order > 10**9:
        avg_order = str(round(avg_order / 10**9, 3)) + ' Billion'

    avg_revenue = avg[1][0]
    if 10**6 < avg_revenue < 10**9:
        avg_revenue = '$ ' + str(round(avg_revenue / 10**6, 3)) + ' Million'
    elif 10**9 < avg_revenue < 10**12:
        avg_revenue = '$ ' + str(round(avg_revenue / 10**9, 3)) + ' Billion'
    elif avg_revenue >= 10**12:
        avg_revenue = '$ ' + str(round(avg_revenue / 10**12, 3)) + ' Trillion'

    # most revenue
    revenue_total = get_employee_revenue_total(date_start, date_end)
    
    # Revenue by employees
    most_revenue_name = revenue_total.loc[0, 'name']
    revenue_range = revenue_total.revenue.max() - revenue_total.revenue.min()

    # revenue by employee
    revenue_total_source = ColumnDataSource(revenue_total)
    revenue_total_hover = HoverTool(tooltips=[('Employee', '@name'), ('Revenue', '@revenue{$ 0.00 a}')])
    revenue_total_fig = figure(sizing_mode='scale_width', height=300, y_range=revenue_total.name,
        x_range=(revenue_total.revenue.min() - revenue_range/10, revenue_total.revenue.max()), 
        tools=[revenue_total_hover])
    revenue_total_fig.hbar(y='name', right='revenue', source=revenue_total_source, height=0.8, 
        hover_color='red', hover_fill_alpha=0.8)
    # styling visual
    revenue_total_fig.xaxis.axis_label = 'Revenue'
    revenue_total_fig.xaxis.axis_label_text_font_size = "12pt"
    revenue_total_fig.xaxis.axis_label_standoff = 10
    revenue_total_fig.yaxis.axis_label = 'Employee'
    revenue_total_fig.yaxis.axis_label_text_font_size = "12pt"
    revenue_total_fig.yaxis.axis_label_standoff = 10
    revenue_total_fig.xaxis.major_label_text_font_size = '11pt'
    revenue_total_fig.yaxis.major_label_text_font_size = '11pt'
    revenue_total_fig.xaxis[0].formatter = NumeralTickFormatter(format="$ 0.00 a")

    # most orders
    orders_total = get_employee_orders_total(date_start, date_end)
    orders_source = ColumnDataSource(orders_total)
    most_orders_name = orders_total.loc[0, 'name']
    orders_range = orders_total.orders.max() - orders_total.orders.min()
    
    # orders by employees
    orders_total_source = ColumnDataSource(orders_total)
    orders_total_hover = HoverTool(tooltips=[('Employee', '@name'), ('Order number', '@orders{0.00 a}')])
    orders_total_fig = figure(sizing_mode='scale_width', height=300,
        y_range=orders_total.name, x_range=(orders_total.orders.min() - orders_range/10, orders_total.orders.max()),
        tools=[orders_total_hover])
    orders_total_fig.hbar(y='name', right='orders', source=orders_total_source, height=0.8, 
        hover_color='red', hover_fill_alpha=0.8)
    # styling visual
    orders_total_fig.xaxis.axis_label = 'Employee'
    orders_total_fig.xaxis.axis_label_text_font_size = "12pt"
    orders_total_fig.xaxis.axis_label_standoff = 10
    orders_total_fig.yaxis.axis_label = 'Order numbers'
    orders_total_fig.yaxis.axis_label_text_font_size = "12pt"
    orders_total_fig.yaxis.axis_label_standoff = 10
    orders_total_fig.xaxis.major_label_text_font_size = '11pt'
    orders_total_fig.yaxis.major_label_text_font_size = '11pt'
    orders_total_fig.xaxis[0].formatter = NumeralTickFormatter(format="0.00 a")
    

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    js_revenue_total, div_revenue_total = components(revenue_total_fig)
    js_orders_total, div_orders_total = components(orders_total_fig)

    html = render_template(
        'employees.html',
        js_resources=js_resources,
        css_resources=css_resources,
        div_revenue_total=div_revenue_total,
        js_revenue_total=js_revenue_total,
        div_orders_total=div_orders_total,
        js_orders_total=js_orders_total,
        # js_fig=js_fig,
        # div_fig=div_fig,
        most_orders_name=most_orders_name,
        most_revenue_name=most_revenue_name,
        avg_order=avg_order,
        avg_revenue=avg_revenue,
        date_start=date_start,
        date_end=date_end,
    )
    return html


def get_employee_revenue_total(date_start, date_end):
    """
    return employee name and revenue for top 10
    """
    sql = f"""
    select *
    from(select employee.name, sum(sales.total) as revenue
         from sales, employee
         where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
             and sales.employeeID = employee.employeeID
         group by employee.name
         order by sum(sales.total) desc)
    where rownum < 11
    order by revenue asc
    """
    # need to make output to be ascending order to further plot be descending order
    rows = query(sql)
    df = pd.DataFrame(rows, columns=['name', 'revenue'])
    print(df)
    return df

def get_employee_orders_total(date_start, date_end):
    """
    return employee name and order number for top 10
    """
    sql = f"""
    select *
    from (select employee.name as name, count(sales.salesID) as order_number
          from sales, employee
          where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
              and sales.employeeID = employee.employeeID
          group by employee.name
          order by count(sales.salesID) desc)
    where rownum < 11
    order by order_number asc
    """
    rows = query(sql)
    df = pd.DataFrame(rows, columns=['name', 'orders'])
    # print(df.head())
    return df


def get_avg_selling_per(date_start, date_end):
    """
    Return the average order numbers of each employee within the time range.
    """
    sql = f"""
    select sum(order_num) / count(name), sum(revenue) / count(name)
    from (select count(sales.salesID) as order_num, sum(sales.total) as revenue, employee.name as name
          from sales, employee
          where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
              and sales.employeeID = employee.employeeID
          group by employee.name)
    """
    rows = query(sql)
    df = pd.DataFrame(rows)
    return df


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