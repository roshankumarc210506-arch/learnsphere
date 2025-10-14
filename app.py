"""
LearnSphere Backend - AI-Powered Adaptive Learning Platform
Complete Flask application with AI integration
"""
"""
LearnSphere Backend - AI-Powered Adaptive Learning Platform
Complete Flask application with AI integration
"""

from flask import Flask, request, jsonify, session, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
from ai_service import AIService

# Initialize Flask app
app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///learnsphere.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

# Initialize extensions
CORS(app, 
    supports_credentials=True, 
    origins=[r"http://localhost:*", r"http://127.0.0.1:*"],
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], 
    allow_headers=['Content-Type', 'Authorization'])

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
db = SQLAlchemy(app)

# Initialize AI Service
ai_service = AIService()

# ==================== DATABASE MODELS ====================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'name': self.name
        }


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    weak_topics = db.Column(db.Text)
    quiz_scores = db.Column(db.Text)
    completed_modules = db.Column(db.Text)
    final_test_score = db.Column(db.Integer)
    streak = db.Column(db.Integer, default=1)
    achievements = db.Column(db.Text)
    study_time = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    bookmarks = db.Column(db.Text)
    last_login_date = db.Column(db.Date)
    
    def get_json_field(self, field_name, default_value):
        data = getattr(self, field_name)
        return json.loads(data) if data else default_value
    
    def set_json_field(self, field_name, value):
        setattr(self, field_name, json.dumps(value))

    def get_weak_topics(self): return self.get_json_field('weak_topics', [])
    def set_weak_topics(self, topics): self.set_json_field('weak_topics', topics)
    
    def get_quiz_scores(self): return self.get_json_field('quiz_scores', {})
    def set_quiz_scores(self, scores): self.set_json_field('quiz_scores', scores)
    
    def get_completed_modules(self): return self.get_json_field('completed_modules', [])
    def set_completed_modules(self, modules): self.set_json_field('completed_modules', modules)
    
    def get_achievements(self): return self.get_json_field('achievements', [])
    def set_achievements(self, achievements): self.set_json_field('achievements', achievements)
    
    def get_notes(self): return self.get_json_field('notes', {})
    def set_notes(self, notes): self.set_json_field('notes', notes)
    
    def get_bookmarks(self): return self.get_json_field('bookmarks', [])
    def set_bookmarks(self, bookmarks): self.set_json_field('bookmarks', bookmarks)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'weak_topics': self.get_weak_topics(),
            'quiz_scores': self.get_quiz_scores(),
            'completed_modules': self.get_completed_modules(),
            'final_test_score': self.final_test_score,
            'streak': self.streak,
            'achievements': self.get_achievements(),
            'study_time': self.study_time,
            'notes': self.get_notes(),
            'bookmarks': self.get_bookmarks(),
            'last_login_date': self.last_login_date.isoformat() if self.last_login_date else None
        }


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(20), default='medium')
    hint = db.Column(db.Text)
    explanation = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_options(self):
        return json.loads(self.options)
    
    def set_options(self, options):
        self.options = json.dumps(options)
    
    def to_dict(self, include_answer=False):
        data = {
            'id': self.id,
            'topic': self.topic,
            'q': self.question,
            'options': self.get_options(),
            'difficulty': self.difficulty,
            'hint': self.hint,
            'explanation': self.explanation
        }
        if include_answer:
            data['ans'] = self.correct_answer
        return data


class StudyPlan(db.Model):
    __tablename__ = 'study_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    reminder = db.Column(db.Boolean, default=False)
    notified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'time': self.time.strftime('%H:%M'),
            'title': self.title,
            'reminder': self.reminder,
            'notified': self.notified
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'read': self.read,
            'timestamp': self.created_at.isoformat()
        }


class FinalTest(db.Model):
    __tablename__ = 'final_tests'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    question = db.relationship('QuizQuestion', backref='final_tests')
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'position': self.position,
            'topic': self.question.topic
        }


class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    teacher = db.relationship('User', backref='announcements')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'teacher_name': self.teacher.name,
            'created_at': self.created_at.isoformat()
        }


# ==================== DECORATORS ====================

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        user = User.query.get(session['user_id'])
        if not user or user.role != 'teacher':
            return jsonify({'error': 'Teacher access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ==================== HELPER FUNCTIONS ====================

def update_student_streak(profile):
    today = datetime.utcnow().date()
    
    if profile.last_login_date == today:
        return
    
    if profile.last_login_date:
        yesterday = today - timedelta(days=1)
        if profile.last_login_date == yesterday:
            profile.streak += 1
        else:
            profile.streak = 1
    else:
        profile.streak = 1
    
    profile.last_login_date = today
    
    if profile.streak >= 3:
        achievements = profile.get_achievements()
        if 'streak_starter' not in achievements:
            achievements.append('streak_starter')
            profile.set_achievements(achievements)
            add_notification(profile.user_id, 'Achievement Unlocked! 🔥', 
                           'You earned the "Streak Starter" badge for logging in 3 days in a row!')
    
    db.session.commit()


def check_achievements(profile, scores):
    achievements = profile.get_achievements()
    new_achievements = False
    
    completed = profile.get_completed_modules()
    if len(completed) >= 1 and 'first_step' not in achievements:
        achievements.append('first_step')
        add_notification(profile.user_id, 'Achievement Unlocked! 👟', 
                       'You earned the "First Step" badge!')
        new_achievements = True
    
    if 'quiz_whiz' not in achievements:
        for score in scores.values():
            if score >= 1.0:
                achievements.append('quiz_whiz')
                add_notification(profile.user_id, 'Achievement Unlocked! ⭐', 
                               'You earned the "Quiz Whiz" badge for scoring 100%!')
                new_achievements = True
                break
    
    if profile.final_test_score == 100 and 'perfectionist' not in achievements:
        achievements.append('perfectionist')
        add_notification(profile.user_id, 'Achievement Unlocked! 👑', 
                       'You earned the "Perfectionist" badge!')
        new_achievements = True
    
    if new_achievements:
        profile.set_achievements(achievements)
        db.session.commit()


def add_notification(user_id, title, message):
    notif = Notification(user_id=user_id, title=title, message=message)
    db.session.add(notif)
    try:
        db.session.commit()
    except:
        db.session.rollback()


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def validate_registration_data(data):
    """Validate registration input data"""
    if not isinstance(data, dict):
        return False, "Invalid request format"
    
    required_fields = ['username', 'password', 'role']
    if not all(field in data for field in required_fields):
        return False, "Missing required fields"
        
    if not isinstance(data['username'], str) or len(data['username']) < 3:
        return False, "Username must be at least 3 characters long"
        
    if not isinstance(data['password'], str) or len(data['password']) < 4:
        return False, "Password must be at least 4 characters long"
        
    if data['role'] not in ['student', 'teacher']:
        return False, "Invalid role specified"
        
    return True, None

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    is_valid, error_message = validate_registration_data(data)
    if not is_valid:
        app.logger.warning(f'Invalid registration attempt: {error_message}')
        return jsonify({'error': error_message}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    user = User(
        username=data['username'],
        role=data['role'],
        name=data.get('name', data['username'].capitalize())
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    if user.role == 'student':
        first_topic = QuizQuestion.query.first()
        profile = StudentProfile(
            user_id=user.id,
            weak_topics=json.dumps([first_topic.topic if first_topic else 'Algebra']),
            quiz_scores=json.dumps({}),
            completed_modules=json.dumps([]),
            achievements=json.dumps([]),
            notes=json.dumps({}),
            bookmarks=json.dumps([]),
            last_login_date=datetime.utcnow().date()
        )
        db.session.add(profile)
        db.session.commit()
    
    session['user_id'] = user.id
    return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if user.role != data.get('role'):
        return jsonify({'error': 'Invalid role for this user'}), 401
    
    session['user_id'] = user.id
    
    if user.role == 'student' and user.student_profile:
        update_student_streak(user.student_profile)
    
    return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return jsonify({'error': 'User not found'}), 401
    return jsonify({'user': user.to_dict()}), 200


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'authenticated': False}), 200
    user = User.query.get(user_id)
    if not user:
        return jsonify({'authenticated': False}), 200
    return jsonify({'authenticated': True, 'role': user.role, 'user': user.to_dict()}), 200


# ==================== STUDENT ENDPOINTS ====================

@app.route('/api/student/profile', methods=['GET'])
@login_required
def get_student_profile():
    user = User.query.get(session['user_id'])
    if user.role != 'student':
        return jsonify({'error': 'Student access only'}), 403
    
    profile = user.student_profile
    if not profile:
        first_topic = QuizQuestion.query.first()
        profile = StudentProfile(
            user_id=user.id,
            weak_topics=json.dumps([first_topic.topic if first_topic else 'Algebra']),
            last_login_date=datetime.utcnow().date()
        )
        db.session.add(profile)
        db.session.commit()

    return jsonify({
        'user': user.to_dict(),
        'profile': profile.to_dict()
    }), 200


@app.route('/api/student/profile', methods=['PUT'])
@login_required
def update_student_profile():
    user = User.query.get(session['user_id'])
    if user.role != 'student':
        return jsonify({'error': 'Student access only'}), 403
    
    data = request.get_json()
    profile = user.student_profile
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    if 'completed_modules' in data:
        profile.set_completed_modules(data['completed_modules'])
    if 'quiz_scores' in data:
        profile.set_quiz_scores(data['quiz_scores'])
    if 'final_test_score' in data:
        profile.final_test_score = data['final_test_score']
    if 'study_time' in data:
        profile.study_time = data['study_time']
    if 'achievements' in data:
        profile.set_achievements(data['achievements'])
    if 'bookmarks' in data:
        profile.set_bookmarks(data['bookmarks'])
    if 'notes' in data:
        profile.set_notes(data['notes'])
    
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'profile': profile.to_dict()}), 200


@app.route('/api/student/quiz', methods=['GET'])
@login_required
def get_personalized_quiz():
    user = User.query.get(session['user_id'])
    if user.role != 'student':
        return jsonify({'error': 'Student access only'}), 403
    
    profile = user.student_profile
    weak_topics = profile.get_weak_topics() or ['Algebra']
    
    quiz_data = {}
    for topic in weak_topics:
        questions = QuizQuestion.query.filter_by(topic=topic).limit(5).all()
        quiz_data[topic] = [q.to_dict(include_answer=True) for q in questions]
    
    return jsonify({'quiz': quiz_data}), 200


@app.route('/api/student/submit-quiz', methods=['POST'])
@login_required
def submit_quiz():
    user = User.query.get(session['user_id'])
    if user.role != 'student':
        return jsonify({'error': 'Student access only'}), 403
    
    data = request.get_json()
    profile = user.student_profile
    
    scores_update = data.get('scores', {})
    current_scores = profile.get_quiz_scores()
    current_scores.update(scores_update)
    profile.set_quiz_scores(current_scores)
    
    # Update weak topics
    new_weak_topics = [topic for topic, score in current_scores.items() if score < 0.7]
    profile.set_weak_topics(list(set(new_weak_topics)))
    
    completed_modules = data.get('completed_modules', [])
    profile.set_completed_modules(list(set(profile.get_completed_modules() + completed_modules)))
    
    check_achievements(profile, current_scores)
    db.session.commit()
    
    return jsonify({'message': 'Quiz submitted', 'profile': profile.to_dict()}), 200


@app.route('/api/student/leaderboard', methods=['GET'])
@login_required
def get_leaderboard():
    students = User.query.filter_by(role='student').all()
    leaderboard = []
    
    for student in students:
        if student.student_profile:
            profile = student.student_profile
            scores = profile.get_quiz_scores()
            avg_score = (sum(scores.values()) / len(scores)) if scores else 0
            
            leaderboard.append({
                'id': student.id,
                'name': student.name,
                'username': student.username,
                'score': round(avg_score * 100),
                'completed': len(profile.get_completed_modules()),
                'streak': profile.streak
            })
    
    leaderboard.sort(key=lambda x: (x['score'], x['streak']), reverse=True)
    return jsonify({'leaderboard': leaderboard}), 200


# ==================== AI ENDPOINTS ====================

@app.route('/api/ai-tutor/chat', methods=['POST'])
@login_required
def ai_tutor_chat():
    if not ai_service.is_available():
        return jsonify({'error': 'AI service not configured'}), 503
    
    data = request.get_json()
    user = User.query.get(session['user_id'])
    profile = user.student_profile if user.role == 'student' else None
    
    context = {
        'name': user.name,
        'weak_topics': profile.get_weak_topics() if profile else [],
        'quiz_scores': profile.get_quiz_scores() if profile else {}
    }
    
    try:
        response = ai_service.chat_with_tutor(
            message=data['message'],
            context=context,
            history=data.get('history', [])
        )
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': f'AI error: {str(e)}'}), 500


@app.route('/api/ai/generate-questions', methods=['POST'])
@teacher_required
def generate_questions():
    if not ai_service.is_available():
        return jsonify({'error': 'AI service not configured'}), 503
    
    data = request.get_json()
    topic = data.get('topic', 'Algebra')
    difficulty = data.get('difficulty', 'medium')
    count = data.get('count', 5)
    
    try:
        questions = ai_service.generate_quiz_questions(topic, difficulty, count)
        
        # Save to database
        user_id = session['user_id']
        saved_questions = []
        
        for q_data in questions:
            question = QuizQuestion(
                topic=q_data['topic'],
                question=q_data['question'],
                correct_answer=q_data['correct_answer'],
                difficulty=q_data['difficulty'],
                hint=q_data.get('hint', ''),
                explanation=q_data.get('explanation', ''),
                created_by=user_id
            )
            question.set_options(q_data['options'])
            db.session.add(question)
            saved_questions.append(question)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(saved_questions)} questions generated',
            'questions': [q.to_dict(include_answer=True) for q in saved_questions]
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Generation failed: {str(e)}'}), 500


@app.route('/api/ai/analyze-performance', methods=['POST'])
@login_required
def analyze_performance():
    if not ai_service.is_available():
        return jsonify({'error': 'AI service not configured'}), 503
    
    user = User.query.get(session['user_id'])
    if user.role != 'student':
        return jsonify({'error': 'Student access only'}), 403
    
    profile = user.student_profile
    try:
        analysis = ai_service.analyze_student_performance(
            quiz_scores=profile.get_quiz_scores(),
            weak_topics=profile.get_weak_topics()
        )
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== STUDY PLAN ENDPOINTS ====================

@app.route('/api/study-plans', methods=['GET'])
@login_required
def get_study_plans():
    user_id = session['user_id']
    plans = StudyPlan.query.filter_by(user_id=user_id).order_by(StudyPlan.date, StudyPlan.time).all()
    return jsonify({'plans': [plan.to_dict() for plan in plans]}), 200


@app.route('/api/study-plans', methods=['POST'])
@login_required
def create_study_plan():
    data = request.get_json()
    user_id = session['user_id']
    
    try:
        plan = StudyPlan(
            user_id=user_id,
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            time=datetime.strptime(data['time'], '%H:%M').time(),
            title=data['title'],
            reminder=data.get('reminder', False)
        )
        db.session.add(plan)
        db.session.commit()
        return jsonify({'message': 'Study plan created', 'plan': plan.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/study-plans/<int:plan_id>', methods=['DELETE'])
@login_required
def delete_study_plan(plan_id):
    user_id = session['user_id']
    plan = StudyPlan.query.filter_by(id=plan_id, user_id=user_id).first()
    
    if not plan:
        return jsonify({'error': 'Plan not found'}), 404
    
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'message': 'Plan deleted'}), 200


# ==================== NOTIFICATION ENDPOINTS ====================

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    user_id = session['user_id']
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return jsonify({'notifications': [n.to_dict() for n in notifications]}), 200


@app.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    data = request.get_json()
    user_id = session['user_id']
    
    if data and 'id' in data:
        notification = Notification.query.filter_by(id=data['id'], user_id=user_id).first()
        if notification:
            notification.read = True
            db.session.commit()
            return jsonify({'message': 'Notification marked as read'}), 200
        return jsonify({'error': 'Notification not found'}), 404
    
    Notification.query.filter_by(user_id=user_id, read=False).update({'read': True})
    db.session.commit()
    return jsonify({'message': 'All notifications marked as read'}), 200


# ==================== TEACHER ENDPOINTS ====================

@app.route('/api/teacher/students', methods=['GET'])
@teacher_required
def get_all_students():
    students = User.query.filter_by(role='student').all()
    result = []
    
    for student in students:
        if student.student_profile:
            profile = student.student_profile
            scores = profile.get_quiz_scores()
            avg_score = (sum(scores.values()) / len(scores)) if scores else 0
            
            result.append({
                'id': student.id,
                'username': student.username,
                'name': student.name,
                'weak_topics': profile.get_weak_topics(),
                'quiz_scores': scores,
                'completed_modules': profile.get_completed_modules(),
                'final_test_score': profile.final_test_score,
                'avg_score': round(avg_score * 100),
                'streak': profile.streak,
                'achievements': profile.get_achievements(),
                'study_time': profile.study_time
            })
    
    return jsonify({'students': result}), 200


@app.route('/api/teacher/questions', methods=['GET'])
@teacher_required
def get_all_questions():
    questions = QuizQuestion.query.all()
    return jsonify({'questions': [q.to_dict(include_answer=True) for q in questions]}), 200


@app.route('/api/teacher/questions', methods=['POST'])
@teacher_required
def create_question():
    data = request.get_json()
    user_id = session['user_id']
    
    required_fields = ['topic', 'question', 'options', 'correct_answer']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if data['correct_answer'] not in data['options']:
        return jsonify({'error': 'Correct answer must be one of the options'}), 400
    
    try:
        question = QuizQuestion(
            topic=data['topic'],
            question=data['question'],
            correct_answer=data['correct_answer'],
            difficulty=data.get('difficulty', 'medium'),
            hint=data.get('hint', ''),
            explanation=data.get('explanation', ''),
            created_by=user_id
        )
        question.set_options(data['options'])
        db.session.add(question)
        db.session.commit()
        
        return jsonify({'message': 'Question created', 'question': question.to_dict(include_answer=True)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/teacher/questions/<int:question_id>', methods=['PUT'])
@teacher_required
def update_question(question_id):
    question = QuizQuestion.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    data = request.get_json()
    
    if 'topic' in data:
        question.topic = data['topic']
    if 'question' in data:
        question.question = data['question']
    if 'options' in data:
        question.set_options(data['options'])
    if 'correct_answer' in data:
        if data['correct_answer'] not in question.get_options():
            return jsonify({'error': 'Correct answer must be one of the options'}), 400
        question.correct_answer = data['correct_answer']
    if 'difficulty' in data:
        question.difficulty = data['difficulty']
    if 'hint' in data:
        question.hint = data['hint']
    if 'explanation' in data:
        question.explanation = data['explanation']
    
    db.session.commit()
    return jsonify({'message': 'Question updated', 'question': question.to_dict(include_answer=True)}), 200


@app.route('/api/teacher/questions/<int:question_id>', methods=['DELETE'])
@teacher_required
def delete_question(question_id):
    question = QuizQuestion.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted'}), 200


@app.route('/api/teacher/final-test', methods=['GET'])
@teacher_required
def get_final_test():
    tests = FinalTest.query.order_by(FinalTest.position).all()
    test_data = []
    
    for t in tests:
        test_data.append({
            'id': t.id,
            'question_id': t.question_id,
            'position': t.position,
            'topic': t.question.topic,
            'question': t.question.to_dict(include_answer=True)
        })
    
    return jsonify({'final_test': test_data}), 200


@app.route('/api/student/final-test', methods=['GET'])
@login_required
def get_student_final_test():
    user = User.query.get(session['user_id'])
    if user.role != 'student':
        return jsonify({'error': 'Student access only'}), 403
    
    tests = FinalTest.query.order_by(FinalTest.position).all()
    test_data = []
    
    for t in tests:
        test_data.append({
            'topic': t.question.topic,
            'index': t.question.id,
            'question': t.question.to_dict(include_answer=False)
        })
    
    return jsonify({'final_test': test_data}), 200


@app.route('/api/teacher/final-test', methods=['POST'])
@teacher_required
def set_final_test():
    data = request.get_json()
    user_id = session['user_id']
    
    if not data.get('question_ids') or not isinstance(data['question_ids'], list):
        return jsonify({'error': 'Question IDs list required'}), 400
    
    valid_ids = {q.id for q in QuizQuestion.query.filter(QuizQuestion.id.in_(data['question_ids'])).all()}
    if len(valid_ids) != len(data['question_ids']):
        return jsonify({'error': 'Invalid question IDs'}), 400
    
    FinalTest.query.delete()
    
    for idx, question_id in enumerate(data['question_ids']):
        test = FinalTest(
            question_id=question_id,
            position=idx,
            created_by=user_id
        )
        db.session.add(test)
    
    db.session.commit()
    return jsonify({'message': 'Final test updated'}), 200


@app.route('/api/teacher/announcements', methods=['GET'])
def get_announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return jsonify({'announcements': [a.to_dict() for a in announcements]}), 200


@app.route('/api/teacher/announcements', methods=['POST'])
@teacher_required
def create_announcement():
    data = request.get_json()
    user_id = session['user_id']
    
    required_fields = ['title', 'content']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Title and content required'}), 400
    
    announcement = Announcement(
        teacher_id=user_id,
        title=data['title'],
        content=data['content'],
        priority=data.get('priority', 'normal')
    )
    
    db.session.add(announcement)
    db.session.commit()
    
    students = User.query.filter_by(role='student').all()
    for student in students:
        notif = Notification(
            user_id=student.id,
            title=f"New Announcement: {data['title']}",
            message=data['content']
        )
        db.session.add(notif)
    
    db.session.commit()
    return jsonify({'message': 'Announcement created', 'announcement': announcement.to_dict()}), 201


@app.route('/api/teacher/analytics', methods=['GET'])
@teacher_required
def get_analytics():
    students = User.query.filter_by(role='student').all()
    
    total_students = len(students)
    total_quiz_scores = []
    topic_performance = {}
    completion_rates = []
    
    for student in students:
        if student.student_profile:
            profile = student.student_profile
            scores = profile.get_quiz_scores()
            
            if scores:
                total_quiz_scores.extend(scores.values())
                
                for topic, score in scores.items():
                    if topic not in topic_performance:
                        topic_performance[topic] = []
                    topic_performance[topic].append(score)
            
            completed = profile.get_completed_modules()
            total_modules = QuizQuestion.query.with_entities(QuizQuestion.topic).distinct().count()
            completion_rate = (len(completed) / total_modules * 100) if total_modules > 0 else 0
            completion_rates.append(completion_rate)
    
    avg_score = (sum(total_quiz_scores) / len(total_quiz_scores) * 100) if total_quiz_scores else 0
    avg_completion = (sum(completion_rates) / len(completion_rates)) if completion_rates else 0
    
    topic_averages = {
        topic: round(sum(scores) / len(scores) * 100, 2)
        for topic, scores in topic_performance.items()
    }
    
    return jsonify({
        'total_students': total_students,
        'average_score': round(avg_score, 2),
        'average_completion': round(avg_completion, 2),
        'topic_performance': topic_averages,
        'total_questions': QuizQuestion.query.count()
    }), 200


# ==================== DATABASE INITIALIZATION ====================

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Setup logging configuration"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/learnsphere.log', 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('LearnSphere startup')

def initialize_database():
    setup_logging()
    db.create_all()
    
    # Create demo users
    if not User.query.filter_by(username='teacher').first():
        print("Creating demo teacher...")
        teacher = User(username='teacher', role='teacher', name='Prof. Smith')
        teacher.set_password('1234')
        db.session.add(teacher)
        db.session.commit()
    
    if not User.query.filter_by(username='student').first():
        print("Creating demo student...")
        student = User(username='student', role='student', name='Alex Johnson')
        student.set_password('1234')
        db.session.add(student)
        db.session.commit()
        
        profile = StudentProfile(
            user_id=student.id,
            weak_topics=json.dumps(['Calculus', 'Statistics']),
            quiz_scores=json.dumps({'Algebra': 0.9, 'Geometry': 0.75}),
            completed_modules=json.dumps(['Algebra']),
            achievements=json.dumps(['first_step']),
            streak=3,
            study_time=7200,
            notes=json.dumps({}),
            bookmarks=json.dumps([]),
            last_login_date=(datetime.utcnow() - timedelta(days=1)).date()
        )
        db.session.add(profile)
        db.session.commit()
    
    # Create default questions
    if QuizQuestion.query.count() == 0:
        print("Adding default questions...")
        default_questions = [
            {
                'topic': 'Algebra',
                'question': 'Solve: 2x + 5 = 15',
                'options': ['x=5', 'x=10', 'x=2.5'],
                'correct_answer': 'x=5',
                'difficulty': 'easy',
                'hint': 'Isolate the variable x.',
                'explanation': 'Subtract 5 from both sides to get 2x = 10, then divide by 2.'
            },
            {
                'topic': 'Algebra',
                'question': 'What is the slope of the line y = 3x - 7?',
                'options': ['3', '-7', '7'],
                'correct_answer': '3',
                'difficulty': 'easy',
                'hint': 'The equation is in slope-intercept form (y = mx + b).',
                'explanation': 'In y = mx + b, m is the slope. Here, m = 3.'
            },
            {
                'topic': 'Algebra',
                'question': 'Factor: x² - 4',
                'options': ['(x-2)(x+2)', '(x-2)(x-2)', '(x+4)(x-1)'],
                'correct_answer': '(x-2)(x+2)',
                'difficulty': 'medium',
                'hint': 'This is a difference of squares.',
                'explanation': 'x² - 4 = x² - 2² = (x-2)(x+2)'
            },
            {
                'topic': 'Calculus',
                'question': 'What is the derivative of x²?',
                'options': ['2x', 'x', 'x³/3'],
                'correct_answer': '2x',
                'difficulty': 'easy',
                'hint': 'Use the power rule.',
                'explanation': 'The power rule: d/dx(x^n) = nx^(n-1). For x², the derivative is 2x.'
            },
            {
                'topic': 'Calculus',
                'question': 'What is the integral of 3x² dx?',
                'options': ['x³ + C', '6x + C', '3x³ + C'],
                'correct_answer': 'x³ + C',
                'difficulty': 'medium',
                'hint': 'Use reverse power rule.',
                'explanation': 'Integral of x^n is x^(n+1)/(n+1). For 3x², it is 3(x³/3) = x³ + C.'
            },
            {
                'topic': 'Statistics',
                'question': 'What is the mean of 2, 4, 6?',
                'options': ['4', '3', '5'],
                'correct_answer': '4',
                'difficulty': 'easy',
                'hint': 'Mean is the average.',
                'explanation': 'Sum = 2+4+6 = 12. Count = 3. Mean = 12/3 = 4.'
            },
            {
                'topic': 'Statistics',
                'question': 'What is the median in a sorted dataset?',
                'options': ['Middle value', 'Average', 'Most frequent'],
                'correct_answer': 'Middle value',
                'difficulty': 'easy',
                'hint': 'Think "middle".',
                'explanation': 'The median is the middle value when data is sorted.'
            },
            {
                'topic': 'Geometry',
                'question': 'Area of a circle with radius r?',
                'options': ['πr²', '2πr', 'πr'],
                'correct_answer': 'πr²',
                'difficulty': 'easy',
                'hint': 'Area involves squaring.',
                'explanation': 'The formula is A = πr².'
            },
            {
                'topic': 'Geometry',
                'question': 'Sum of angles in a triangle?',
                'options': ['180°', '90°', '360°'],
                'correct_answer': '180°',
                'difficulty': 'easy',
                'hint': 'A fundamental property.',
                'explanation': 'The sum of interior angles in any triangle is always 180°.'
            }
        ]
        
        for q_data in default_questions:
            question = QuizQuestion(
                topic=q_data['topic'],
                question=q_data['question'],
                correct_answer=q_data['correct_answer'],
                difficulty=q_data['difficulty'],
                hint=q_data['hint'],
                explanation=q_data['explanation']
            )
            question.set_options(q_data['options'])
            db.session.add(question)
        
        db.session.commit()
        print("✓ Default questions added")


@app.before_request
def init_check():
    if not hasattr(app, '_initialized'):
        with app.app_context():
            initialize_database()
            app._initialized = True

@app.after_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https:; script-src 'self' 'unsafe-inline' https:; connect-src 'self' http://localhost:5000 https:; font-src 'self' https:; worker-src 'self' blob:;"
    return response


# ==================== ERROR HANDLERS ====================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Please log in to access this resource'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': 'You do not have permission to access this resource'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed', 'message': 'The method is not allowed for this endpoint'}), 405

@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({'error': 'Unprocessable entity', 'message': str(error)}), 422

@app.errorhandler(429)
def too_many_requests(error):
    return jsonify({'error': 'Too many requests', 'message': 'Please try again later'}), 429

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Internal Server Error: {str(error)}')
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    app.logger.error(f'Unhandled Exception: {str(error)}')
    db.session.rollback()
    return jsonify({'error': 'Server error', 'message': 'An unexpected error occurred'}), 500


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'ai_service': 'available' if ai_service.is_available() else 'unavailable'
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'total_users': User.query.count(),
        'total_students': User.query.filter_by(role='student').count(),
        'total_teachers': User.query.filter_by(role='teacher').count(),
        'total_questions': QuizQuestion.query.count(),
        'topics': [t[0] for t in db.session.query(QuizQuestion.topic).distinct().all()]
    }), 200


# ==================== STATIC FILE ROUTES ====================

@app.route('/')
def serve_index():
    # First check if database needs initialization
    if not User.query.first():
        with app.app_context():
            initialize_database()
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path, cache_timeout=0)

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    with app.app_context():
        initialize_database()
        print("\n" + "="*50)
        print("🚀 LearnSphere Starting")
        print("="*50)
        print(f"✓ Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"✓ AI Service: {'Enabled' if ai_service.is_available() else 'Disabled'}")
        print(f"✓ Demo credentials: teacher/1234 or student/1234")
        print(f"✓ Open http://localhost:5000 in your browser")
        print("="*50 + "\n")

    # Listen on all interfaces for local dev, so http://localhost:8000 can reach it
    app.run(debug=True, host='0.0.0.0', port=5000)