__author__ = 'piotr'

from flask import render_template, url_for, redirect
from app import app
from httplib import NOT_FOUND

@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('catalog.home'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), NOT_FOUND