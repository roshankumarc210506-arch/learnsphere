"""
Database initialization script for LearnSphere
Creates tables and populates with sample data
"""

from app import app, db, User, StudentProfile, QuizQuestion, Announcement, Notification
import json
from datetime import datetime, timedelta

def init_database():
    """Initialize database with tables and sample data"""
    
    with app.app_context():
        print("\n" + "="*60)
        print("🗄️  LearnSphere Database Initialization")
        print("="*60)
        
        # Create all tables
        print("\n📋 Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Check if data already exists
        if User.query.first():
            print("\n⚠️  Database already populated. Skipping initialization.")
            print("   Use 'python reset_db.py' to reset the database.")
            return
        
        print("\n👥 Creating demo users...")
        
        # Create demo teacher
        teacher = User(
            username='teacher',
            role='teacher',
            name='Professor Smith'
        )
        teacher.set_password('1234')
        db.session.add(teacher)
        db.session.commit()
        print("✓ Teacher created (username: teacher, password: 1234)")
        
        # Create demo students
        students_data = [
            {
                'username': 'student',
                'name': 'Alex Johnson',
                'weak_topics': ['Calculus', 'Statistics'],
                'quiz_scores': {'Algebra': 0.85, 'Geometry': 0.75},
                'completed_modules': ['Algebra'],
                'streak': 5,
                'achievements': ['first_step', 'streak_starter'],
                'study_time': 7200
            },
            {
                'username': 'chaitanya',
                'name': 'Chaitanya Kumar',
                'weak_topics': ['Statistics'],
                'quiz_scores': {'Algebra': 0.95, 'Geometry': 0.9, 'Calculus': 0.88},
                'completed_modules': ['Algebra', 'Geometry', 'Calculus'],
                'streak': 15,
                'achievements': ['first_step', 'streak_starter', 'quiz_whiz'],
                'study_time': 15000
            },
            {
                'username': 'priya',
                'name': 'Priya Sharma',
                'weak_topics': ['Geometry', 'Calculus'],
                'quiz_scores': {'Algebra': 0.8, 'Statistics': 0.85},
                'completed_modules': ['Algebra', 'Statistics'],
                'streak': 7,
                'achievements': ['first_step', 'streak_starter'],
                'study_time': 9500
            }
        ]
        
        for student_data in students_data:
            student = User(
                username=student_data['username'],
                role='student',
                name=student_data['name']
            )
            student.set_password('1234')
            db.session.add(student)
            db.session.commit()
            
            # Create student profile
            profile = StudentProfile(
                user_id=student.id,
                weak_topics=json.dumps(student_data['weak_topics']),
                quiz_scores=json.dumps(student_data['quiz_scores']),
                completed_modules=json.dumps(student_data['completed_modules']),
                final_test_score=None,
                streak=student_data['streak'],
                achievements=json.dumps(student_data['achievements']),
                study_time=student_data['study_time'],
                notes=json.dumps({}),
                bookmarks=json.dumps([]),
                last_login_date=(datetime.utcnow() - timedelta(days=1)).date()
            )
            db.session.add(profile)
            
            # Add welcome notification
            notif = Notification(
                user_id=student.id,
                title='Welcome to LearnSphere! 🎉',
                message='Start your learning journey by exploring modules and taking quizzes.',
                read=False
            )
            db.session.add(notif)
            
            print(f"✓ Student created: {student_data['username']} (password: 1234)")
        
        db.session.commit()
        
        # Create quiz questions
        print("\n📝 Creating quiz questions...")
        questions_data = [
            # Algebra Questions
            {
                'topic': 'Algebra',
                'question': 'Solve: 2x + 5 = 15',
                'options': ['x=5', 'x=10', 'x=2.5'],
                'correct_answer': 'x=5',
                'difficulty': 'easy',
                'hint': 'Isolate the variable x by performing inverse operations.',
                'explanation': 'First subtract 5 from both sides: 2x = 10. Then divide both sides by 2: x = 5.'
            },
            {
                'topic': 'Algebra',
                'question': 'What is the slope of the line y = 3x - 7?',
                'options': ['3', '-7', '7'],
                'correct_answer': '3',
                'difficulty': 'easy',
                'hint': 'The equation is in slope-intercept form: y = mx + b',
                'explanation': 'In the form y = mx + b, m is the slope and b is the y-intercept. Here, m = 3.'
            },
            {
                'topic': 'Algebra',
                'question': 'Factor the expression: x² - 4',
                'options': ['(x-2)(x+2)', '(x-2)(x-2)', '(x+4)(x-1)'],
                'correct_answer': '(x-2)(x+2)',
                'difficulty': 'medium',
                'hint': 'This is a difference of squares pattern.',
                'explanation': 'The difference of squares formula is a² - b² = (a-b)(a+b). Here, x² - 4 = x² - 2² = (x-2)(x+2).'
            },
            {
                'topic': 'Algebra',
                'question': 'Simplify: 3(x + 2) - 2(x - 1)',
                'options': ['x + 8', 'x + 4', '5x + 8'],
                'correct_answer': 'x + 8',
                'difficulty': 'medium',
                'hint': 'Distribute first, then combine like terms.',
                'explanation': '3(x+2) - 2(x-1) = 3x + 6 - 2x + 2 = x + 8'
            },
            {
                'topic': 'Algebra',
                'question': 'If f(x) = 2x + 3, what is f(5)?',
                'options': ['13', '10', '8'],
                'correct_answer': '13',
                'difficulty': 'easy',
                'hint': 'Substitute x = 5 into the function.',
                'explanation': 'f(5) = 2(5) + 3 = 10 + 3 = 13'
            },
            
            # Calculus Questions
            {
                'topic': 'Calculus',
                'question': 'What is the derivative of x²?',
                'options': ['2x', 'x', 'x³/3'],
                'correct_answer': '2x',
                'difficulty': 'easy',
                'hint': 'Use the power rule for derivatives.',
                'explanation': 'The power rule states d/dx(x^n) = nx^(n-1). For x², the derivative is 2x^(2-1) = 2x.'
            },
            {
                'topic': 'Calculus',
                'question': 'What is the integral of 3x² dx?',
                'options': ['x³ + C', '6x + C', '3x³ + C'],
                'correct_answer': 'x³ + C',
                'difficulty': 'medium',
                'hint': 'Use the reverse power rule.',
                'explanation': 'The integral of x^n is (x^(n+1))/(n+1). For 3x², it becomes 3 * (x³/3) + C = x³ + C.'
            },
            {
                'topic': 'Calculus',
                'question': 'What is the derivative of sin(x)?',
                'options': ['cos(x)', '-cos(x)', 'tan(x)'],
                'correct_answer': 'cos(x)',
                'difficulty': 'medium',
                'hint': 'This is a standard trigonometric derivative.',
                'explanation': 'The derivative of sin(x) is cos(x). This is a fundamental rule in calculus.'
            },
            {
                'topic': 'Calculus',
                'question': 'What is the limit of (x² - 1)/(x - 1) as x approaches 1?',
                'options': ['2', '1', 'undefined'],
                'correct_answer': '2',
                'difficulty': 'hard',
                'hint': 'Factor the numerator first.',
                'explanation': '(x²-1)/(x-1) = (x+1)(x-1)/(x-1) = x+1. As x→1, the limit is 2.'
            },
            
            # Statistics Questions
            {
                'topic': 'Statistics',
                'question': 'What is the mean of the numbers 2, 4, 6?',
                'options': ['4', '3', '5'],
                'correct_answer': '4',
                'difficulty': 'easy',
                'hint': 'The mean is the average of the numbers.',
                'explanation': 'The sum is 2+4+6=12. The count is 3. The mean is 12 / 3 = 4.'
            },
            {
                'topic': 'Statistics',
                'question': 'What measure of central tendency is the middle value in a sorted dataset?',
                'options': ['Median', 'Mean', 'Mode'],
                'correct_answer': 'Median',
                'difficulty': 'easy',
                'hint': 'Think "middle".',
                'explanation': 'The median is the value separating the higher half from the lower half of a data sample.'
            },
            {
                'topic': 'Statistics',
                'question': 'What is the mode of the dataset: 3, 5, 5, 7, 9?',
                'options': ['5', '3', '7'],
                'correct_answer': '5',
                'difficulty': 'easy',
                'hint': 'The mode is the most frequent value.',
                'explanation': 'The mode is the value that appears most frequently. Here, 5 appears twice.'
            },
            {
                'topic': 'Statistics',
                'question': 'In a normal distribution, what percentage of data falls within one standard deviation?',
                'options': ['68%', '95%', '99.7%'],
                'correct_answer': '68%',
                'difficulty': 'medium',
                'hint': 'This is part of the 68-95-99.7 rule.',
                'explanation': 'In a normal distribution, approximately 68% of data falls within one standard deviation of the mean.'
            },
            
            # Geometry Questions
            {
                'topic': 'Geometry',
                'question': 'What is the area of a circle with radius r?',
                'options': ['πr²', '2πr', 'πr'],
                'correct_answer': 'πr²',
                'difficulty': 'easy',
                'hint': 'Area involves squaring the radius.',
                'explanation': 'The formula for the area of a circle is A = πr².'
            },
            {
                'topic': 'Geometry',
                'question': 'The sum of the angles in a triangle is:',
                'options': ['180°', '90°', '360°'],
                'correct_answer': '180°',
                'difficulty': 'easy',
                'hint': 'A fundamental property of Euclidean geometry.',
                'explanation': 'The sum of the interior angles of any triangle is always 180 degrees.'
            },
            {
                'topic': 'Geometry',
                'question': 'What is the volume of a cube with side length s?',
                'options': ['s³', 's²', '6s²'],
                'correct_answer': 's³',
                'difficulty': 'easy',
                'hint': 'Volume involves three dimensions.',
                'explanation': 'The volume of a cube is side × side × side = s³.'
            },
            {
                'topic': 'Geometry',
                'question': 'What is the Pythagorean theorem?',
                'options': ['a² + b² = c²', 'a + b = c', 'a² - b² = c²'],
                'correct_answer': 'a² + b² = c²',
                'difficulty': 'easy',
                'hint': 'Relates the sides of a right triangle.',
                'explanation': 'In a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides.'
            },
            {
                'topic': 'Geometry',
                'question': 'What is the circumference of a circle with radius r?',
                'options': ['2πr', 'πr²', 'πr'],
                'correct_answer': '2πr',
                'difficulty': 'easy',
                'hint': 'Circumference is the distance around the circle.',
                'explanation': 'The circumference formula is C = 2πr or C = πd, where d is the diameter.'
            }
        ]
        
        question_count = 0
        for q_data in questions_data:
            question = QuizQuestion(
                topic=q_data['topic'],
                question=q_data['question'],
                correct_answer=q_data['correct_answer'],
                difficulty=q_data['difficulty'],
                hint=q_data['hint'],
                explanation=q_data['explanation'],
                created_by=teacher.id
            )
            question.set_options(q_data['options'])
            db.session.add(question)
            question_count += 1
        
        db.session.commit()
        print(f"✓ {question_count} questions created across multiple topics")
        
        # Create a sample announcement
        print("\n📢 Creating sample announcement...")
        announcement = Announcement(
            teacher_id=teacher.id,
            title='Welcome to LearnSphere!',
            content='Welcome students! This platform uses AI to personalize your learning experience. Start by taking quizzes to identify your strengths and weaknesses.',
            priority='normal'
        )
        db.session.add(announcement)
        db.session.commit()
        print("✓ Announcement created")
        
        # Print summary
        print("\n" + "="*60)
        print("✅ Database initialization complete!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   • Users created: {User.query.count()}")
        print(f"   • Students: {User.query.filter_by(role='student').count()}")
        print(f"   • Teachers: {User.query.filter_by(role='teacher').count()}")
        print(f"   • Questions: {QuizQuestion.query.count()}")
        print(f"   • Topics: {len(set([q.topic for q in QuizQuestion.query.all()]))}")
        print(f"   • Announcements: {Announcement.query.count()}")
        
        print("\n🔐 Demo Credentials:")
        print("   Teacher: username='teacher', password='1234'")
        print("   Student: username='student', password='1234'")
        print("   Student: username='chaitanya', password='1234'")
        print("   Student: username='priya', password='1234'")
        
        print("\n🚀 You can now start the application with:")
        print("   python app.py")
        print("="*60 + "\n")


if __name__ == '__main__':
    init_database()"""
Database initialization script for LearnSphere
Creates tables and populates with sample data
"""

from app import app, db, User, StudentProfile, QuizQuestion, Announcement
import json
from datetime import datetime, timedelta

def init_database():
    """Initialize database with tables and sample data"""
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print("Database already populated. Skipping initialization.")
            return
        
        print("Populating database with sample data...")
        
        # Create demo teacher
        teacher = User(
            username='teacher',
            role='teacher',
            name='Professor Smith'
        )
        teacher.set_password('1234')
        db.session.add(teacher)
        db.session.commit()
        
        # Create demo students
        students_data = [
            {'username': 'student', 'name': 'Alex Johnson', 'weak_topics': ['Calculus', 'Statistics']},
            {'username': 'chaitanya', 'name': 'Chaitanya Kumar', 'weak_topics': ['Statistics']},
            {'username': 'priya', 'name': 'Priya Sharma', 'weak_topics': ['Geometry', 'Calculus']}
        ]
        
        for student_data in students_data:
            student = User(
                username=student_data['username'],
                role='student',
                name=student_data['name']
            )
            student.set_password('1234')
            db.session.add(student)
            db.session.commit()
            
            # Create student profile
            profile = StudentProfile(
                user_id=student.id,
                weak_topics=json.dumps(student_data['weak_topics']),
                quiz_scores=json.dumps({'Algebra': 0.85, 'Geometry': 0.75}),
                completed_modules=json.dumps(['Algebra']),
                final_test_score=None,
                streak=3,
                achievements=json.dumps(['first_step']),
                study_time=7200,
                notes=json.dumps({}),
                bookmarks=json.dumps([]),
                last_login_date=(datetime.utcnow() - timedelta(days=1)).date()
            )
            db.session.add(profile)
        
        db.session.commit()
        
        # Create quiz questions
        questions_data = [
            {
                'topic': 'Algebra',
                'question': 'Solve: 2x + 5 = 15',
                'options': ['x=5', 'x=10', 'x=2.5'],
                'correct_answer': 'x=5',
                'difficulty': 'easy',
                'hint': 'Isolate the variable x by performing inverse operations.',
                'explanation': 'First subtract 5 from both sides: 2x = 10. Then divide both sides by 2: x = 5.'
            },
            {
                'topic': 'Algebra',
                'question': 'What is the slope of the line y = 3x - 7?',
                'options': ['3', '-7', '7'],
                'correct_answer': '3',
                'difficulty': 'easy',
                'hint': 'The equation is in slope-intercept form: y = mx + b',
                'explanation': 'In the form y = mx + b, m is the slope and b is the y-intercept. Here, m = 3.'
            },
            {
                'topic': 'Algebra',
                'question': 'Factor the expression: x² - 4',
                'options': ['(x-2)(x+2)', '(x-2)(x-2)', '(x+4)(x-1)'],
                'correct_answer': '(x-2)(x+2)',
                'difficulty': 'medium',
                'hint': 'This is a difference of squares pattern.',
                'explanation': 'The difference of squares formula is a² - b² = (a-b)(a+b). Here, x² - 4 = x² - 2² = (x-2)(x+2).'