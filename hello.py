import os
import io
import base64
import qrcode
import pyotp
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask, render_template, request, redirect, url_for, jsonify, session

# --- Load Environment Variables ---
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("Supabase URL or Key not found. Check your .env file.")

# --- Initialize ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)
app.secret_key = 'replace_this_with_a_random_secret_key'

# --- Routes ---

@app.route("/")
def home():
    return render_template('login.html')


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        full_name = request.form["name"]
        password = request.form["password"]

        # 1. Insert user into Supabase
        response = supabase.table("Users").insert({
            "email": email,
            "full_name": full_name,
            "password": password  # ⚠️ In real apps: hash this!
        }).execute()

        # 2. Generate TOTP secret
        secret = pyotp.random_base32()

        # 3. Save secret into Supabase for this user
        supabase.table("Users").update({"totp_secret": secret}).eq("email", email).execute()

        # 4. Generate otpauth URL for Google Authenticator
        otpauth_url = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="MyFlaskApp")

        # 5. Generate QR code as base64 for template
        img = qrcode.make(otpauth_url)
        buf = io.BytesIO()
        img.save(buf, "PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        # Store email in session for verification step
        session['pending_user'] = email
        session['pending_secret'] = secret
        session['qr_b64'] = qr_b64

        return redirect(url_for('verify_totp'))

    return render_template("signup.html")

# New endpoint for verifying Google Authenticator code after signup
@app.route("/verify-totp", methods=["GET", "POST"])
def verify_totp():
    email = session.get('pending_user')
    secret = session.get('pending_secret')
    qr_b64 = session.get('qr_b64')
    if not email or not secret or not qr_b64:
        return redirect(url_for('signup'))
    if request.method == "POST":
        token = request.form["token"]
        print(f"[DEBUG] Verifying token: {token} with secret: {secret}")
        totp = pyotp.TOTP(secret)
        is_valid = totp.verify(token)
        print(f"[DEBUG] Verification result: {is_valid}")
        if is_valid:
            # Optionally mark user as verified in DB here
            session.pop('pending_user', None)
            session.pop('pending_secret', None)
            session.pop('qr_b64', None)
            return redirect(url_for('dashboard'))
        else:
            return render_template("verify_totp.html", qr_b64=qr_b64, error=f"Invalid code, try again. [DEBUG] token={token} secret={secret}")
    return render_template("verify_totp.html", qr_b64=qr_b64)

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        token = request.form["token"]

        # 1. Fetch user
        user = supabase.table("Users").select("*").eq("email", email).execute()
        if not user.data:
            return "User not found"

        user = user.data[0]

        # 2. Check password (again: hash in real apps)
        if user["password"] != password:
            return "Wrong password"

        # 3. Verify TOTP
        totp = pyotp.TOTP(user["totp_secret"])
        if not totp.verify(token):
            return "Invalid or expired 2FA code"

        return "Login successful ✅"

    return render_template("signin.html")


@app.route('/dashboard')
def dashboard():
    return "✅ Welcome to your Football Analysis dashboard — 2FA verified!"


@app.route('/login_success')
def login_success():
    return "User signed up successfully! Check your email for confirmation."


if __name__ == "__main__":
    app.run(debug=True)
