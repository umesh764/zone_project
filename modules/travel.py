from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
from modules.models import db, TravelCity, Airline, Flight, Train, BusOperator, Bus, Hotel, HotelRoom, Cab, HolidayPackage, TravelBooking, TravelPassenger, TravelInsurance, PriceAlert, TravelReview
import uuid
import random
import json
from datetime import datetime, timedelta
import math

travel_bp = Blueprint('travel', __name__)

# ============================================
# HOME ROUTES
# ============================================

@travel_bp.route('/travel')
def travel_home():
    """Travel Home Page"""
    cities = TravelCity.query.limit(6).all()
    return render_template('travel_home.html', cities=cities)

@travel_bp.route('/travel/search')
def travel_search():
    """Search for travel options"""
    trip_type = request.args.get('type', 'flight')
    from_city = request.args.get('from')
    to_city = request.args.get('to')
    date = request.args.get('date')
    
    return render_template('travel_search.html', 
                         trip_type=trip_type,
                         from_city=from_city,
                         to_city=to_city,
                         date=date)

@travel_bp.route('/travel/planner')
def trip_planner():
    """AI Trip Planner"""
    destination = request.args.get('destination', 'Mumbai')
    duration = int(request.args.get('duration', 3))
    
    # Simple itinerary
    itinerary = []
    for day in range(1, duration + 1):
        itinerary.append({
            'day': day,
            'morning': f'Visit local attraction in {destination}',
            'afternoon': 'Lunch at local restaurant',
            'evening': 'Explore market',
            'night': 'Return to hotel'
        })
    
    return render_template('trip_planner.html', 
                         itinerary=itinerary,
                         destination=destination,
                         duration=duration)