from flask import Flask, render_template, request
from datetime import datetime, date
import json
import os

app = Flask(__name__)

def log_visitor_ip():
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    path = request.path
    user_agent = request.headers.get('User-Agent', 'Unknown')
    referrer = request.headers.get('Referer', 'Direct')
    
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    with open(os.path.join(log_dir, 'visitor_log.txt'), 'a') as f:
        f.write(f"{timestamp} | {ip_address} | {path} | {user_agent} | {referrer}\n")

@app.context_processor
def inject_now():
    return {'now': datetime.now}

@app.before_request
def before_request():
    log_visitor_ip()

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

if __name__ == "__main__":    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
    )
