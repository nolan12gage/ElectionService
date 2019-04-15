
from database import *

from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import os, re, sys
import mysql.connector
import json
import requests
import xmltodict

# gameReturnPoint = '/'

application = Flask(__name__)
application.secret_key = '6FljLk488f32'

# @application.route('/about')
# def about():
	# print(gameReturnPoint)
	# return render_template('about.html')  

@application.route('/join', methods=['GET', 'POST'])
def createAccount():  
	idErr = fnErr = lnErr = pwErr = confErr = emailErr = addErr = cityErr = stateErr = zipErr = ''
	if request.method == 'POST':
			idErr = validateID(request.form['username'])
			fnErr = validateFirst(request.form['fname'])
			lnErr = validateLast(request.form['lname'])
			pwErr = validatePassword(request.form['password'])
			confErr = validateConf(request.form['password'], request.form['confirmPassword'])
			emailErr = validateEmail(request.form['email'])
			addErr = validateEmail(request.form['address'])
			cityErr = validateEmail(request.form['city'])
			stateErr = validateState(request.form['state'])
			zipErr = validateZip(request.form['zip'])

			if not idErr and not pwErr and not confErr and not emailErr and not stateErr and not zipErr:
				createUser(request.form)
				return redirect(url_for('.login'))
			else: 
				username = password = confPass = email = state = zip = ''
				if not idErr:
					username = request.form['username']
				if not pwErr and not confErr:
					password = request.form['password']
					confPass = request.form['confirmPassword']
				if not emailErr:
					email = request.form['email']
				if not stateErr:
					state = request.form['state']
				if not zipErr:
					zip = request.form['zip']
				return render_template('createAccount.html', idErr=idErr, pwErr=pwErr, confErr=confErr, emailErr=emailErr, 
															 stateErr=stateErr, zipErr=zipErr, username=username,
															 password=password, confPass=confPass, email=email, state=state, zip=zip)
	return render_template('createAccount.html', idErr=idErr, pwErr=pwErr, confErr=confErr, emailErr=emailErr, stateErr=stateErr, zipErr=zipErr)
  
@application.route('/login', methods=['GET', 'POST'])
def login():
	loginErr = idErr = pwErr = ''
	if request.method == 'POST':
		loginErr = verifyCredentials(request.form)
		if not loginErr:
			session['username'] = request.form['username']
			return redirect(url_for('start'))
		else:
			return render_template('loginForm.html', loginErr=loginErr, username=request.form['username'])
	return render_template('loginForm.html', loginErr=loginErr)

@application.route('/logout')
def logout():
    # remove the username from the session if it's there
	session.pop('username', None)
	return redirect(url_for('start'))

@application.route('/', methods=['GET', 'POST'])
def start():
	return render_template('start.html', session=session)

@application.route('/results', methods=['GET', 'POST']) # skip for now and come back
def results():
	return render_template('results.html', session=session)		
		
@application.route('/checkout', methods=['GET', 'POST'])
def checkout():
	if 'username' in session:
		total = request.form['total']
		return render_template('checkout.html', total=total, session=session)
	else:
		return redirect(url_for('login'))

@application.route('/cart', methods=['GET', 'POST'])
def cart():
	if 'username' in session:
		if request.method == 'POST':
			if request.form['empty'] == 'empty':
				clearCart(session)
			else:
				addCartItem(request.form, session)
		cartItems = getCartItems(session)
		if getCartTotal(session)[0]:
			cartTotal = round(getCartTotal(session)[0], 2)
		else:
			cartTotal = 0
		return render_template('cart.html', cartTotal=cartTotal, cartItems=cartItems, session=session)
	else:
		return redirect(url_for('login'))
		
@application.route('/card', methods=['GET', 'POST'])
def card():
	err = imgLink = cardName = price = ''
	cname = request.form['cname']
	scryfall_ep = 'https://api.scryfall.com/cards/named?fuzzy=' + cname
	response = requests.get(scryfall_ep)
	card_json = response.json()
	obj = card_json['object']
	print(obj)
	if(obj == 'error'):
		err = card_json['details']
	else: 
		cardName = card_json['name']
		imgLink = card_json['image_uris']['normal']
		price = card_json['prices']['usd']
	return render_template('card.html', err=err, imgLink=imgLink, cardName=cardName, price=price, session=session)
		
@application.route('/account', methods=['GET', 'POST'])
def account():
	if 'username' in session:
		info = getAccountInfo(session)
		orders = getOrders(session)
		return render_template('account.html', info=info, orders=orders, session=session)
	else:
		return redirect(url_for('login'))
		
@application.route('/editInfo', methods=['GET', 'POST']) #probably getting rid of this to save time
def editInfo():
	if 'username' in session:
		return render_template('editInfo.html', session=session) 
	else:
		return redirect(url_for('login'))

@application.route('/order', methods=['GET', 'POST'])
def order():
	if 'username' in session:
		orderID = request.form['orderID']
		trackNo = request.form['trackNo']
		items = viewOrderItems(orderID)
		total = round(viewOrderTotal(orderID)[0], 2)
		orderInfo = viewOrder(orderID)
		# Test tracking XML request below by plugging it into browser URL
		# http://production.shippingapis.com/ShippingAPI.dll?API=TrackV2&XML=<TrackRequest USERID="007UNIVE4922"><TrackID ID="9300189843901275198715"></TrackID></TrackRequest>
		
		usps_ep = 'http://production.shippingapis.com/ShippingAPI.dll?API=TrackV2&XML=<TrackRequest USERID="007UNIVE4922"><TrackID ID="' + trackNo + '"></TrackID></TrackRequest>'
		response = requests.get(usps_ep)
		tracking = xmltodict.parse(response.content)		
		print(tracking)
		return render_template('order.html', orderID=orderID, trackNo=trackNo, items=items, total=total, tracking=tracking, orderInfo=orderInfo, session=session) 
	else:
		return redirect(url_for('login'))
		
@application.route('/confirm', methods=['GET', 'POST'])
def confirm():
	if 'username' in session:
		user = session['username']
		createOrder(user)
		orderID = getLastOrderID()
		print(orderID)
		createOrderItems(user, orderID)
		clearCart(session)
		return render_template('confirm.html', session=session) 
	else:
		return redirect(url_for('login'))
		
if __name__ == "__main__":
		#application.config['SESSION_TYPE'] = 'filesystem'
    application.run(debug=True)
	








	