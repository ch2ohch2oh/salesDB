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
from app.plot import formatter, hbar, multiline

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
    if request.form.get('time_frame') is None:
        time_frame = 'date'
    else:
        time_frame = request.form.get('time_frame')
    
    # average order_numbers
    avg = get_avg_selling_per(date_start, date_end)
    avg_order = formatter(avg[0][0])
    avg_revenue = formatter(avg[1][0], 'dollar')

    # most revenue
    revenue_total = get_employee_revenue_total(date_start, date_end)
    # sql result is reversed due to the hbar layout
    most_revenue_name = revenue_total.loc[9, 'employee']
    
    # Revenue by employee
    js_revenue_total, div_revenue_total = hbar(revenue_total, 'revenue', 'employee')

    # most orders
    orders_total = get_employee_orders_total(date_start, date_end)
    # sql result is reversed due to the hbar layout
    most_orders_name = orders_total.loc[9, 'employee']
    
    # Order numbers by employee
    js_orders_total, div_orders_total = hbar(orders_total, 'order_number', 'employee')

    time_dict = {'date': 'date', 'ww': 'week', 'mon': 'month', 'q': 'quarter'}

    # Top 5 revenue employee trend
    rev_top10 = revenue_total.loc[::-1, 'employee'].tolist()
    # sql result is reversed thus first reverse to correct sequence
    rev_top5 = rev_top10[: 5]
    rev_trend_data = get_employee_trend(date_start, date_end, time_frame, rev_top5, 'revenue')
    rev_trend_js, rev_trend_div = multiline(rev_trend_data, time_dict[time_frame], 'revenue', 'dollar', 
        rev_top5[0], rev_top5[1], rev_top5[2], rev_top5[3], rev_top5[4])

    # top 5 order number employee trend
    num_top10 = orders_total.loc[::-1 , 'employee'].tolist()
    num_top5 = num_top10[: 5]
    num_trend_data = get_employee_trend(date_start, date_end, time_frame, num_top5, 'order_number')
    num_trend_js, num_trend_div = multiline(num_trend_data, time_dict[time_frame], 'order_number', 'number',
        num_top5[0], num_top5[1], num_top5[2], num_top5[3], num_top5[4])

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
        rev_trend_js=rev_trend_js,
        rev_trend_div=rev_trend_div,
        num_trend_js=num_trend_js,
        num_trend_div=num_trend_div,
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
    df = pd.DataFrame(rows, columns=['employee', 'revenue'])
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
    df = pd.DataFrame(rows, columns=['employee', 'order_number'])
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


def get_employee_trend(date_start, date_end, time_frame, employee, basis='revenue'):
    """
    Return the revenue trend of top 5 employee
    Returned employee names replaced space to underscore
    """
    # employee = get_employee_top5(date_start, date_end, basis)

    basis_dict = {'revenue': 'sum(sales.total)', 'order_number': 'count(sales.salesID)'}
    time_dict = {'date': 'date', 'ww': 'week', 'mon': 'month', 'q': 'quarter'}

    if time_frame == 'date' or time_frame is None: # None is used for switch page default frame
        sql = f'''
        select salesdate, 
            sum(case when employee = '{employee[0]}' then {basis} else 0 end) as name1,
            sum(case when employee = '{employee[1]}' then {basis} else 0 end) as name2,
            sum(case when employee = '{employee[2]}' then {basis} else 0 end) as name3,
            sum(case when employee = '{employee[3]}' then {basis} else 0 end) as name4,
            sum(case when employee = '{employee[4]}' then {basis} else 0 end) as name5
        from
        (select salesdate, employee.name as employee, {basis_dict[basis]} as {basis}
         from sales, employee
         where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
             and sales.employeeID = employee.employeeID
             and employee.name in ('{employee[0]}', '{employee[1]}', '{employee[2]}', '{employee[3]}', '{employee[4]}')
        group by salesdate, employee.name)
        group by salesdate
        order by salesdate
        '''
        # the reason use name1/2/3/4/5 here is because {employee[0]} includes space -> error
        rows = query(sql)
        # replace the space in name to underscore otherwise will have problem to access dataframe column
        df = pd.DataFrame(columns=['date', employee[0].replace(" ", "_"), employee[1].replace(" ", "_"), employee[2].replace(" ", "_"), 
            employee[3].replace(" ", "_"), employee[4].replace(" ", "_")])
        for row in rows:
            df.loc[len(df), :] = row
        df['date'] = pd.to_datetime(df['date'])
    else:
        sql = f'''
        select range, 
            sum(case when employee = '{employee[0]}' then {basis} else 0 end) as name1,
            sum(case when employee = '{employee[1]}' then {basis} else 0 end) as name2,
            sum(case when employee = '{employee[2]}' then {basis} else 0 end) as name3,
            sum(case when employee = '{employee[3]}' then {basis} else 0 end) as name4,
            sum(case when employee = '{employee[4]}' then {basis} else 0 end) as name5
        from
        (select to_char(salesdate, '{time_frame}') as range, employee.name as employee, {basis_dict[basis]} as {basis}
         from sales, employee
         where salesdate between to_date('{date_start}', 'YYYY-MM-DD') and to_date('{date_end}', 'YYYY-MM-DD')
             and sales.employeeID = employee.employeeID
             and employee.name in ('{employee[0]}', '{employee[1]}', '{employee[2]}', '{employee[3]}', '{employee[4]}')
         group by to_char(salesdate, '{time_frame}'), employee.name)
        group by range
        order by range
        '''
        rows = query(sql)
        df = pd.DataFrame(columns=[time_dict[time_frame], employee[0].replace(" ", "_"), employee[1].replace(" ", "_"), employee[2].replace(" ", "_"), 
            employee[3].replace(" ", "_"), employee[4].replace(" ", "_")])
        for row in rows:
            df.loc[len(df), :] = row
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