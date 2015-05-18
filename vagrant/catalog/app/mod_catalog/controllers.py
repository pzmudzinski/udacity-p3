__author__ = 'piotr'
from flask import Blueprint

blueprint_catalog = Blueprint('catalog', __name__, url_prefix="/catalog")