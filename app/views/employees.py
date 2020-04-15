from app import app
from bokeh.io import show
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.models import NumeralTickFormatter
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from bokeh.layouts import gridplot

from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from math import pi

from app.db import get_db, query
from app.plot import formatter

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
    time_frame = request.form.get('time_frame')
    # print(time_frame)
    
    # average order_numbers
    avg = get_avg_selling_per(date_start, date_end)
    avg_order = formatter(avg[0][0])
    avg_revenue = formatter(avg[1][0], 'dollar')

    # most revenue
    revenue_total = get_employee_revenue_total(date_start, date_end)
    
    # Revenue by employees
    most_revenue_name = revenue_total.loc[9, 'name']
    revenue_range = revenue_total.revenue.max() - revenue_total.revenue.min()

    # revenue by employee
    revenue_total_source = ColumnDataSource(revenue_total)
    revenue_total_hover = HoverTool(tooltips=[('Employee', '@name'), ('Revenue', '@revenue{$ 0.00 a}')])
    revenue_total_fig = figure(sizing_mode='scale_width', height=300, y_range=revenue_total.name,
        x_range=(revenue_total.revenue.min() - revenue_range/10, revenue_total.revenue.max()), 
        tools=[revenue_total_hover], toolbar_location=None,)
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
    js_revenue_total, div_revenue_total = components(revenue_total_fig)

    # most orders
    orders_total = get_employee_orders_total(date_start, date_end)
    orders_source = ColumnDataSource(orders_total)
    most_orders_name = orders_total.loc[9, 'name']
    orders_range = orders_total.orders.max() - orders_total.orders.min()
    
    # orders by employees
    orders_total_source = ColumnDataSource(orders_total)
    orders_total_hover = HoverTool(tooltips=[('Employee', '@name'), ('Order number', '@orders{0.00 a}')])
    orders_total_fig = figure(sizing_mode='scale_width', height=300,
        y_range=orders_total.name, x_range=(orders_total.orders.min() - orders_range/10, orders_total.orders.max()),
        tools=[orders_total_hover], toolbar_location=None,)
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
    js_orders_total, div_orders_total = components(orders_total_fig)
    
    # gender relation distribution in order
    g = get_ec_gender(date_start, date_end)
    gender = pd.Series(g).reset_index(name='orders').rename(columns={'index':'gender'})
    gender['angle'] = gender['orders']/gender['orders'].sum() * 2*pi
    gender['color'] = Category20c[len(g)]
    gender_hover = HoverTool(tooltips=[('Gender', '@gender'), ('Order number', '@orders{0.00 a}')])
    gender_fig = figure(sizing_mode='scale_width', height=400, toolbar_location=None,
            tools=[gender_hover], x_range=(-0.5, 1.0))
    gender_fig.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend='gender', source=gender, 
        hover_color='red', hover_fill_alpha=0.8)
    gender_fig.axis.axis_label=None
    gender_fig.axis.visible=False
    gender_fig.grid.grid_line_color = None
    js_gender, div_gender = components(gender_fig)

    # state relation distribution in order
    s = get_ec_state(date_start, date_end)
    print(s)
    state = pd.Series(s).reset_index(name='orders').rename(columns={'index':'state'})
    state['angle'] = state['orders']/state['orders'].sum() * 2*pi
    state['color'] = ["#3182bd", "#9ecae1"]
    state_hover = HoverTool(tooltips=[('State', '@state'), ('Order number', '@orders{0.00 a}')])
    state_fig = figure(sizing_mode='scale_width', height=400, toolbar_location=None,
           tools=[state_hover], x_range=(-0.5, 1.0))
    state_fig.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend='state', source=state, 
        hover_color='red', hover_fill_alpha=0.8)
    state_fig.axis.axis_label=None
    state_fig.axis.visible=False
    state_fig.grid.grid_line_color = None
    js_state, div_state = components(state_fig)

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    html = render_template(
        'employees.html',
        js_resources=js_resources,
        css_resources=css_resources,
        div_revenue_total=div_revenue_total,
        js_revenue_total=js_revenue_total,
        div_orders_total=div_orders_total,
        js_orders_total=js_orders_total,
        js_gender=js_gender,
        div_gender=div_gender,
        js_state=js_state,
        div_state=div_state,
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


def get_ec_gender(date_start, date_end):
    """
    Return the order number for each gender distribution.
    """
    sql = f"""
    select 
        sum(case when c_gender = 'Male' and e_gender = 'M' then order_num else 0 end) as cm_em, 
        sum(case when c_gender = 'Female' and e_gender = 'F' then order_num else 0 end) as cf_ef,
        sum(case when c_gender = 'Female' and e_gender = 'M' then order_num else 0 end) as cf_em,
        sum(case when c_gender = 'Male' and e_gender = 'F' then order_num else 0 end) as cm_ef
    from (select count(salesID) as order_num, customer.gender as c_gender, employee.gender as e_gender
          from customer, sales, employee
          where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
              and customer.customerID = sales.customerID
              and employee.employeeID = sales.employeeID
          group by customer.gender, employee.gender)
    """
    rows = query(sql)
    df = {'C_Male : E_Male': rows[0][0], 'C_Female : E_Female': rows[0][1], 'C_Female : E_Male': rows[0][2], 
        'C_Male : E_Female': rows[0][3]}
    return df


def get_ec_state(date_start, date_end):
    """
    Return the order number for customer and emolpyee from same state.
    """
    sql = f"""
    select 
        sum(case when c_state = e_state then order_num else 0 end) as same_state, 
        sum(case when c_state != e_state then order_num else 0 end) as diff_state
    from(select count(salesID) as order_num, city1.state as c_state, city2.state as e_state
         from customer, city city1, sales, employee, city city2
         where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
            and customer.customerID = sales.customerID
            and employee.employeeID = sales.employeeID
            and customer.city = city1.cityID
            and employee.city = city2.cityID
         group by city1.state, city2.state)
    """
    rows = query(sql)
    df = {'Same state': rows[0][0], 'Different state': rows[0][1]}
    return df