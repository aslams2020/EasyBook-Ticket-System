# checkout.py
from flask import Blueprint, render_template

# Define the blueprint
checkout_blueprint = Blueprint('checkout', __name__)

# Define a route for the blueprint
@checkout_blueprint.route('/checkout')
def checkout():
    return render_template('checkout.html')
