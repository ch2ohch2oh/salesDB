from app import app
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.db import get_db


@app.route('/employee', methods=['GET', 'POST'])
@login_required
def employee():
    pass

# restful api
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
              group by employee.name
              order by sum(sales.total) desc)
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