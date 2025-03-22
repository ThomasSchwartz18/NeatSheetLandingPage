from flask import Flask, request, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random key for CSRF

# Set up Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Form class
class EmailForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])

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
        try:
            # Insert the email into the "waitlist" table in Supabase
            response = supabase.table("waitlist").insert({"email": email}).execute()
            print(response)  # Optional: log the full response for debugging
            if not response.error:
                return redirect(url_for('index', success=True))
            else:
                return f"Error saving email: {response.error}", 500
        except Exception as e:
            return f"Error saving email: {str(e)}", 500
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
