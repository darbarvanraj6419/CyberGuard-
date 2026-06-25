from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key' # Needed for sessions

# ==========================================
# CLOUD DATABASE SETUP (NEON POSTGRESQL)
# ==========================================
db_url = os.environ.get('DATABASE_URL')

if db_url:
    # Fix for SQLAlchemy requiring the pure-python 'pg8000' driver
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+pg8000://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # Fallback to local SQLite if testing on your computer
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

# --- NEW EXTENSIONS ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    level = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    recommendations = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==========================================
# INITIALIZE DATABASE FOR GUNICORN
# ==========================================
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Check email and password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    latest_quiz = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.created_at.desc()).first()
    return render_template('dashboard.html', user=current_user, latest_quiz=latest_quiz)

@app.route('/password-checker')
def password_checker():
    return render_template('password_checker.html')

@app.route('/scam-detector')
def scam_detector():
    return render_template('scam_detector.html')

@app.route('/analyze-message', methods=['POST'])
def analyze_message():
    data = request.json
    message = data.get('message', '').lower()
    
    # Scam detection heuristics (Regex & Keywords)
    risk_score = 0
    threats = []
    
    if re.search(r'\b(urgent|immediate action required|suspended)\b', message):
        risk_score += 30
        threats.append("Urgency/Fear Tactics detected")
    if re.search(r'\b(upi pin|otp|password|cvv)\b', message):
        risk_score += 40
        threats.append("Credential theft attempt")
    if re.search(r'\b(lottery|winner|prize|claim)\b', message):
        risk_score += 30
        threats.append("Fake Prize/Lottery scam")
    if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message):
        risk_score += 20
        threats.append("Contains URLs (Verify before clicking)")
        
    risk_score = min(risk_score, 100)
    level = "High" if risk_score >= 70 else "Medium" if risk_score >= 40 else "Low"
    
    return jsonify({
        "score": risk_score,
        "level": level,
        "threats": threats,
        "recommendation": "Do not click links or share details." if risk_score > 40 else "Message seems safe, but stay vigilant."
    })

@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html')

@app.route('/submit-quiz', methods=['POST'])
@login_required
def submit_quiz():
    data = request.json
    score = data.get('score', 0)
    
    level = "Beginner"
    if score >= 81: level = "Cyber Champion"
    elif score >= 61: level = "Excellent"
    elif score >= 41: level = "Good"
    elif score >= 21: level = "Average"
    
    # Save to DB
    new_result = QuizResult(user_id=current_user.id, score=score, level=level)
    db.session.add(new_result)
    
    # Generate Report Text
    recs = f"Based on your score of {score}%, you are at the {level} level. Focus on reviewing modules in the Learning Hub."
    new_report = Report(user_id=current_user.id, score=score, recommendations=recs)
    db.session.add(new_report)
    
    db.session.commit()
    return jsonify({"success": True, "redirect": url_for('report')})

@app.route('/report')
@login_required
def report():
    latest_report = Report.query.filter_by(user_id=current_user.id).order_by(Report.created_at.desc()).first()
    latest_quiz = QuizResult.query.filter_by(user_id=current_user.id).order_by(QuizResult.created_at.desc()).first()
    return render_template('report.html', report=latest_report, quiz=latest_quiz)

@app.route('/learning-hub')
def learning_hub():
    return render_template('learning_hub.html')

if __name__ == '__main__':
    app.run(debug=True)
