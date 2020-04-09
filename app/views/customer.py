from app import app
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from app.db import get_db


@app.route('/customer', methods=['GET', 'POST'])
@login_required
def customer():
    pass

# restful api
@app.route('/api/customer_by_geo', methods=['GET'])
def customer_by_geo():
    """
    Return the customer numbers for each zipcode.
    """
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"""
        select count(customer.customerID) as num, city.zipcode as zipcode
        from customer, city
        where customer.city = city.cityID
        group by city.zipcode)"""))
    data = []
    for row in rows:
        data.append({'cat_name': row[0], 'revenue': row[1]})
    return jsonify(data)

@app.route('/api/repeat_order_by_time', methods=['GET'])
def repeat_order_by_time():
    """
    Return the number of repeated purchases (same prodcut > 3 times)
    and the total number of orders for different category with the time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"""
        with orders as 
            (select sales.customerID as customer_id, productcategory.name as category, sales.salesID as salesID
             from customer, sales, product, productcategory
             where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
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
        group by cat1"""))
    # the reason use avg(number_total) is after the group by, 
    # for the same category, each row has same value for number_total
    data = []
    for row in rows:
        data.append({'cat_name': row[0], 'revenue': row[1]})
    return jsonify(data)

# 需要给 customer table 添加随机性别，可以使用 excel 完成
@app.route('/api/num_order_by_gender_cat', methods=['GET'])
def num_order_by_gender_cat():
    """
    Return the number of male and female purchasing orders for each category in time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"""
        select count(saleID) as order_num, customer.gender as gender, productcategory.name as category
        from customer, sales, product, productcategory
        where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
            and customer.customerID = sales.customerID
            and sales.productID = product.productID
            and product.categoryID = productcategory.categoryID)
        group by productcategory.name, customer.gender"""))
    data = []
    for row in rows:
        data.append({'cat_name': row[0], 'revenue': row[1]})
    return jsonify(data)

# 需要 zipcode 的范围确定东西南北，大致确定
@app.route('/api/num_order_by_geo', methods=['GET'])
def num_order_by_geo():
    """
    Return the number of orders in different geo region for each category in time range.
    """
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    db = get_db()
    cur = db.cursor()
    rows = list(cur.execute(
        f"""
        with geo as
           (select count(saleID) as order_num, city.zipcode as zipcode, productcategory.name as category
            from customer, sales, product, productcategory, city
            where salesdate between to_date({date_start}, 'YYYYMMDD') and to_date({date_end}, 'YYYYMMDD')
                and customer.customerID = sales.customerID
                and sales.productID = product.productID
                and product.categoryID = productcategory.categoryID
                and customer.city = city.cityID)
            group by productcategory.name, city.zipcode)
        select region.range as [region], count(*) as [order_num], category
        from (select case  
              when zipcode between 0 and 19999 then 'Northeast'
              when zipcode between 20000 and 29999 then 'East'
              when zipcode between 30000 and 39999 then 'Southeast'
              when zipcode between 40000 and 59999 then 'North'
              when zipcode between 70000 and 79999 then 'South'
              when zipcode between 88900 and 95000 then 'West'
              when zipcode between 95001 and 96999 then 'Southwest'
              when zipcode between 97000 and 9999 then 'Nouthwest'
              else 'Middle' end as range
              from geo) region
        group by region.range, category
        """))
    data = []
    for row in rows:
        data.append({'cat_name': row[0], 'revenue': row[1]})
    return jsonify(data)