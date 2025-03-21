from flask import Flask, render_template, request
from datetime import datetime, date
import json

app = Flask(__name__)

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
""".format(request.host_url)

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
