from flask import Flask, render_template, request, make_response
from datetime import datetime, date
import json
import os
import requests
import threading
import time
from functools import lru_cache
import geoip2.database
from geoip2.errors import AddressNotFoundError

app = Flask(__name__)

_geo_reader = None

def get_geo_reader():
    global _geo_reader
    if _geo_reader is None:
        db_path = os.path.join(os.path.dirname(__file__), 'geodb', 'GeoLite2-City.mmdb')
        try:
            _geo_reader = geoip2.database.Reader(db_path)
        except FileNotFoundError:
            print(f"GeoIP database file not found at {db_path}")
            return None
    return _geo_reader

def get_geo_location(ip_address):
    reader = get_geo_reader()
    if not reader:
        return "GeoIP DB Missing"
    
    try:
        response = reader.city(ip_address)
        city = response.city.name or 'Unknown'
        country = response.country.name or 'Unknown'
        return f"{city}, {country}"
    except (AddressNotFoundError, ValueError):
        return "Unknown Location"
    except Exception as e:
        print(f"GeoIP error for {ip_address}: {e}")
        return "Unknown"

def write_log_entry(log_data):
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    with open(os.path.join(log_dir, 'visitor_log.txt'), 'a') as f:
        f.write(log_data)

def log_visitor_ip():
    if request.path.startswith('/static/'):
        return
    
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    path = request.path
    user_agent = request.headers.get('User-Agent', 'Unknown')
    referrer = request.headers.get('Referer', 'Direct')
    
    def background_logging(ip, ts, pth, ua, ref):
        geo_location = get_geo_location(ip)
        log_data = f"{ts} | {ip} | {geo_location} | {pth} | {ua} | {ref}\n"
        write_log_entry(log_data)
    
    thread = threading.Thread(
        target=background_logging,
        args=(ip_address, timestamp, path, user_agent, referrer)
    )
    thread.daemon = True
    thread.start()

@app.context_processor
def inject_now():
    return {'now': datetime.now}

@app.before_request
def before_request():
    log_visitor_ip()
    blocked_paths = ['.git', '.env', '__pycache__']
    if any(path in request.path for path in blocked_paths):
        return "Not Found", 404

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/music')
def music():
    return render_template('music.html')

@app.route('/farm')
def farm():
    return render_template('farm.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/sitemap.xml')
def sitemap():
    host_url = request.host_url.rstrip('/')
    today = date.today().strftime('%Y-%m-%d')
    pages = [
        {'loc': host_url + '/', 'lastmod': today},
        {'loc': host_url + '/music', 'lastmod': today},
        {'loc': host_url + '/farm', 'lastmod': today},
        {'loc': host_url + '/about', 'lastmod': today},
        {'loc': host_url + '/contact', 'lastmod': today},
    ]
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = app.response_class(sitemap_xml, mimetype='application/xml')
    return response

@app.route('/robots.txt')
def robots():
    return """
User-agent: *
Allow: /
Sitemap: {}sitemap.xml
Sitemap: {}sitemap.json
""".format(request.host_url, request.host_url)

@app.route('/sitemap.json')
def sitemap_json():
    host_url = request.host_url.rstrip('/')
    today = date.today().strftime('%Y-%m-%d')
    pages = [
        {'url': host_url + '/', 'lastmod': today, 'title': 'Keerthi Gowda - Software Engineer'},
        {'url': host_url + '/music', 'lastmod': today, 'title': 'Keerthi Gowda'},
        {'url': host_url + '/farm', 'lastmod': today, 'title': 'Keerthi Gowda'},
        {'url': host_url + '/about', 'lastmod': today, 'title': 'Keerthi Gowda'},
        {'url': host_url + '/contact', 'lastmod': today, 'title': 'Keerthi Gowda'},
    ]
    return app.response_class(
        response=json.dumps(pages),
        status=200,
        mimetype='application/json'
    )

@app.route('/.well-known/traffic-advice')
def traffic_advice():
    advice = {
        "user-agent": "*",
        "optimize-for-first-visit": True
    }
    return app.response_class(
        response=json.dumps(advice),
        status=200,
        mimetype='application/json'
    )

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    return response

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == "__main__":    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False  # Change this for production
    )
