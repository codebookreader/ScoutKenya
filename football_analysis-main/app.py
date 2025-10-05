from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyotp
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

# In-memory user store for demo (replace with DB in production)
users = {}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    if email in users:
        flash('Email already registered!')
        return redirect(url_for('home'))
    # Generate TOTP secret
    totp_secret = pyotp.random_base32()
    users[email] = {'name': name, 'password': password, 'totp_secret': totp_secret}
    session['pending_user'] = email
    return redirect(url_for('verify_totp'))

@app.route('/verify-totp', methods=['GET', 'POST'])
def verify_totp():
    email = session.get('pending_user')
    if not email or email not in users:
        flash('No user to verify.')
        return redirect(url_for('home'))
    totp_secret = users[email]['totp_secret']
    if request.method == 'POST':
        token = request.form['token']
        totp = pyotp.TOTP(totp_secret)
        if totp.verify(token):
            session['user'] = email
            session.pop('pending_user', None)
            flash('Registration complete!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid code, try again.')
    # Generate QR code for Google Authenticator
    totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(name=email, issuer_name="FootballAnalysis")
    img = qrcode.make(totp_uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return render_template('verify_totp.html', qr_b64=qr_b64)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return f"Welcome, {users[session['user']]['name']}! Registration and 2FA complete."

if __name__ == '__main__':
    app.run(debug=True)
