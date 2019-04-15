from flask import Flask, flash, redirect, render_template, request, session, abort
from validate_email import validate_email
import mysql.connector
import re

host = '127.0.0.1'
database = 'magic_store'
user = 'root'
password = 'password'

def validateID(id):
  idErr = ''
  if(len(id) < 1):
    idErr = 'Field is required'
    return idErr
  if(len(id) > 30 or len(id) < 8):
    idErr = 'Must be between 8 and 30 characters'
    return idErr
  if not re.match("^[A-Za-z0-9]*$", id):  
    idErr = 'Only letters and numbers are allowed'
  return idErr

def validateFirst(fname):
	fnErr = ''
	if(len(fname) < 1):
		fnErr = 'Field is required'
		return fnErr
	return fnErr
	
def validateLast(lname):
	lnErr = ''
	if(len(lname) < 1):
		lnErr = 'Field is required'
		return lnErr
	return lnErr
	
def validatePassword(password):
  pwErr = ''
  if(len(password) < 1):
    pwErr = 'Field is required'
    return pwErr
  if(len(password) > 30 or len(password) < 6):
    pwErr = 'Must be between 6 and 30 characters'
    return pwErr
  if not re.match("^[A-Za-z0-9]*$", password):  
    pwErr = 'Only letters and numbers are allowed'
  return pwErr

def validateConf(password, conf):
  confErr = ''
  if(password != conf):
    confErr = 'Passwords do not match'
  return confErr
  
def validateZip(zip):
  zipErr = ''
  if len(zip) < 1:
    zipErr = 'Field is required'
    return zipErr
  if not re.match("^[0-9]*$", zip) or not zip:  
    zipErr = 'Only numbers are allowed'
    return zipErr
  if len(zip) != 5:
    zipErr = 'ZIP code must be 5 digits'
  return zipErr

def validateEmail(email):
  emailErr = ''
  if(len(email) < 1): 
    emailErr = 'Field is required'
    return emailErr
  if(len(email) > 100):
    emailErr = 'Must be fewer than 100 characters'
    return emailErr
  if(not validate_email(email)):
    emailErr = 'Not a valid email'
  return emailErr

def validateAddress(address):
	addErr = ''
	if(len(address) < 1): 
		addErr = 'Field is required'
		return addErr
	return addErr

def validateCity(city):
	cityErr = ''
	if(len(city) < 1): 
		cityErr = 'Field is required'
		return cityErr
	return cityErr
	
def validateState(state):
  stateErr = ''
  if(len(state) < 1):
    stateErr = 'Field is required'
    return stateErr
  return stateErr
	
# def getLeaders():
  # leaders = []
  # conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
  # cursor = conn.cursor()
  # select_leaders = ("SELECT USER_ID, CAREER_WINS, AGE, LOCATION, LAST_LOGIN FROM USER_INFO ORDER BY CAREER_WINS DESC")
  # cursor.execute(select_leaders)
  # row = cursor.fetchone()
  # rownum = 1
  # while row is not None and rownum < 20:
    # leaders.append(row)
    # row = cursor.fetchone()
    # rownum += 1
    
  # return leaders
  
def verifyCredentials(form):
  credErr = idErr = pwErr = ''
  idErr = validateID(form['username'])
  pwErr = validatePassword(form['password'])
  
  # If the id or password don't meet criteria, automatically return an error
  if idErr or pwErr:
    credErr = 'Invalid user name or password'
    return credErr
    
  conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
  cursor = conn.cursor(buffered=True)
  select_query = ("SELECT username FROM user WHERE username = %s and password = %s")
  select_criteria = (form['username'], form['password'])
  cursor.execute(select_query, select_criteria)
  numRows = cursor.rowcount
  cursor.close()
  conn.close()
  
  if numRows < 1: 
    credErr = 'Invalid user name or password'
    return credErr
  
  return credErr  
	
# def updateLastLogin(username):
	# conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	# cursor = conn.cursor()
	# update_login = ("UPDATE USER_INFO SET LAST_LOGIN = CURDATE() WHERE USER_ID = %s")
	# update_crit = (username,)
	# cursor.execute(update_login, update_crit)
	# conn.commit()
	# cursor.close()
	# conn.close()

def createUser(form):
  conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
  cursor = conn.cursor()
  add_user = ("INSERT INTO user"
              "(username, first_name, last_name, address, city, state, zip, password, email)"
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
  user_data = (form['username'], form['fname'], form['lname'], form['address'], form['city'], form['state'], form['zip'], form['password'], form['email'])
  cursor.execute(add_user, user_data)
  conn.commit()
  cursor.close()
  conn.close()
 
def addCartItem(form, session):
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	add_item = ("INSERT INTO cart"
              "(card_name, cart_username, quantity, unit_price)"
               "VALUES (%s, %s, %s, %s)")
	item_data = (form['cardName'], session['username'], form['qty'], form['price'])
	cursor.execute(add_item, item_data)
	conn.commit()
	cursor.close()
	conn.close()
	
def getCartTotal(session):
	total = 0
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	get_total = ("SELECT SUM(unit_price * quantity) FROM cart WHERE cart_username = '") + session['username'] + "'"
	cursor.execute(get_total)
	total = cursor.fetchone()
	conn.commit()
	cursor.close()
	conn.close()
	return total
	
def getCartItems(session):
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	get_items = ("SELECT card_name, unit_price, SUM(quantity) FROM cart WHERE cart_username = '") + session['username'] + "' GROUP BY card_name, unit_price"
	cursor.execute(get_items)
	items = cursor.fetchall()
	conn.commit()
	cursor.close()
	conn.close()
	return items
	
def clearCart(session):
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	delete = ("DELETE from cart WHERE cart_username = '") + session['username'] + "'"
	cursor.execute(delete)
	conn.commit()
	cursor.close()
	conn.close()
	
def getOrders(session):
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	get_orders = ("SELECT order_id, order_date, tracking_no from magic_store.order")
	cursor.execute(get_orders)
	orders = cursor.fetchall()
	conn.commit()
	cursor.close()
	conn.close()
	return orders
	
def viewOrder(orderID):
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	view_order = "SELECT order_id, order_date, tracking_no from magic_store.order WHERE order_id = '" + orderID + "'"
	cursor.execute(view_order)
	order = cursor.fetchone()
	conn.commit()
	cursor.close()
	conn.close()
	return order
	
def viewOrderTotal(orderID):
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	total_qry = "SELECT SUM(item_qty * item_price) FROM order_item WHERE order_number = '" + orderID + "'"
	cursor.execute(total_qry)
	total = cursor.fetchone()
	conn.commit()
	cursor.close()
	conn.close()
	return total

def viewOrderItems(orderID):
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	viewItems = "SELECT item_name, item_qty, item_price FROM order_item WHERE order_number = '" + orderID + "'"
	cursor.execute(viewItems)
	items = cursor.fetchall()
	conn.commit()
	cursor.close()
	conn.close()
	return items
	
def getAccountInfo(session):
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	getInfo =  ("SELECT username, first_name, last_name, address, city, state, zip, email FROM user WHERE username = '") + session['username'] + "'"
	cursor.execute(getInfo)
	info = cursor.fetchone()
	conn.commit()
	cursor.close()
	conn.close()
	return info

def createOrder(userName):
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	add_order = "INSERT INTO magic_store.order (order_user, order_date, tracking_no) VALUES ('" + userName + "', CURDATE(), '9200190158236707861872')"
	cursor.execute(add_order)
	conn.commit()
	cursor.close()
	conn.close() 

def getLastOrderID():
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	getLastOrder = ("SELECT MAX(order_id) from magic_store.order")
	cursor.execute(getLastOrder)
	lastOrder = cursor.fetchone()[0]
	conn.commit()
	cursor.close()
	conn.close()
	return lastOrder

def createOrderItems(userName, orderID):
	conn = mysql.connector.connect(host=host, database=database, user=user, password=password)
	cursor = conn.cursor()
	getCartItems = "SELECT card_name, quantity, unit_price from cart WHERE cart_username = '" + userName + "'"
	cursor.execute(getCartItems)
	items = cursor.fetchall()
	for item in items:
		insertItem = "INSERT INTO order_item (item_name, item_qty, order_number, item_price) VALUES ('" + item[0] + "', '" + str(item[1]) + "', '" + str(orderID) + "', '" + str(item[2]) + "')"
		cursor.execute(insertItem)
		print(insertItem)
	conn.commit()
	cursor.close()
	conn.close()

