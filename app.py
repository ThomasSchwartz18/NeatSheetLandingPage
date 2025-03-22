from flask import Flask, request, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email
import sqlite3
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random key for CSRF

# Form class
class EmailForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])

# Ensure database is created
with sqlite3.connect('waitlist.db') as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS waitlist (email TEXT PRIMARY KEY)')

@app.route('/', methods=['GET'])
def index():
    form = EmailForm()
    success = request.args.get('success', False)
    return render_template('index.html', form=form, success=success)

@app.route('/signup', methods=['POST'])
def signup():
    form = EmailForm(request.form)
    if form.validate_on_submit():
        email = form.email.data
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not recaptcha_response:
            return "Please complete the CAPTCHA", 400

        # Retrieve the secret key from environment variables
        recaptcha_secret = os.environ.get('RECAPTCHA_SECRET')
        if not recaptcha_secret:
            return "Server misconfiguration", 500

        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {'secret': recaptcha_secret, 'response': recaptcha_response}
        response = requests.post(verify_url, data=payload)
        result = response.json()
        if not result.get('success'):
            return "CAPTCHA verification failed", 400

        try:
            with sqlite3.connect('waitlist.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT OR IGNORE INTO waitlist (email) VALUES (?)', (email,))
                conn.commit()
            return redirect(url_for('index', success=True))
        except sqlite3.Error as e:
            return f'Error saving email: {e}', 500
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)