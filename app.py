from flask import Flask, render_template
from datetime import datetime, date

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

if __name__ == "__main__":    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
    )
