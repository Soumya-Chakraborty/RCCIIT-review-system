from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'teacher', 'hod'

    # Additional fields for students
    roll_number = db.Column(db.String(20), nullable=True)
    semester = db.Column(db.Integer, nullable=True)
    section = db.Column(db.String(1), nullable=True)

    # Relationships
    reviews = db.relationship('Review', backref='student', lazy=True, foreign_keys='Review.student_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department = db.Column(db.String(50), nullable=False)

    # User relationship
    user = db.relationship('User', backref=db.backref('teacher_profile', uselist=False))

    # Courses taught
    courses = db.relationship('TeacherCourse', backref='teacher', lazy=True)

    # Reviews received
    reviews_received = db.relationship('Review', backref='teacher_reviewed', lazy=True, foreign_keys='Review.teacher_id')

    def __repr__(self):
        return f'<Teacher {self.user.name}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False, unique=True)

    # Teachers teaching this course
    teachers = db.relationship('TeacherCourse', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'

class TeacherCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(1), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('course_id', 'semester', 'section', name='unique_course_sem_sec'),
    )

    def __repr__(self):
        return f'<TeacherCourse {self.teacher.user.name} - {self.course.name} - Sem {self.semester} - Sec {self.section}>'

class ReviewCriterion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True)

    # Ratings for this criterion
    ratings = db.relationship('Rating', backref='criterion', lazy=True)

    def __repr__(self):
        return f'<ReviewCriterion {self.name}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(1), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Individual ratings
    ratings = db.relationship('Rating', backref='review', lazy=True)

    # Course relationship
    course = db.relationship('Course')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'teacher_id', 'course_id', name='one_review_per_student_teacher_course'),
    )

    def __repr__(self):
        return f'<Review #{self.id} by {self.student.name} for {self.teacher_reviewed.user.name}>'

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('review_criterion.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)  # 1 to 5 stars

    __table_args__ = (
        db.UniqueConstraint('review_id', 'criterion_id', name='one_rating_per_criterion_per_review'),
    )

    def __repr__(self):
        return f'<Rating {self.value} stars for criterion {self.criterion.name}>'
