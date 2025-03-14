from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from flask_migrate import Migrate
from sqlalchemy import func
from config import Config
from models import db, User, Teacher, Course, TeacherCourse, ReviewCriterion, Review, Rating
from forms import LoginForm, RegisterForm, ReviewForm, CriterionForm, TeacherCourseForm, CourseForm
from wtforms.fields import SelectField
from wtforms.validators import DataRequired
import re

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create all tables
@app.before_first_request
def create_tables():
    db.create_all()
    # Create HOD user if it doesn't exist
    if User.query.filter_by(email='hod@rcciit.org.in').first() is None:
        hod = User(
            email='hod@rcciit.org.in',
            name='HOD Admin',
            role='hod'
        )
        hod.set_password('hodadmin123')
        db.session.add(hod)
        db.session.commit()

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        if not form.email.data.endswith('@rcciit.org.in'):
            flash('Email must end with @rcciit.org.in', 'danger')
            return render_template('auth/register.html', form=form)

        user = User(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data,
            roll_number=form.roll_number.data,
            semester=int(form.semester.data),
            section=form.section.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Main dashboard router
@app.route('/')
@login_required
def dashboard():
    if current_user.role == 'hod':
        return redirect(url_for('hod_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('student_dashboard'))
    else:
        flash('Invalid user role', 'danger')
        return redirect(url_for('logout'))

# Student routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        abort(403)

    # Get teacher-courses for the student's semester and section
    teacher_courses = TeacherCourse.query.filter_by(
        semester=current_user.semester,
        section=current_user.section
    ).join(Teacher).join(Course).join(User, Teacher.user_id == User.id).all()

    # For debugging - add print statements
    print(f"Current student: Semester {current_user.semester}, Section {current_user.section}")
    print(f"Found {len(teacher_courses)} teacher courses")
    for tc in teacher_courses:
        print(f"Teacher: {tc.teacher.user.name}, Course: {tc.course.name}, Semester: {tc.semester}, Section: {tc.section}")

    # Get student's already submitted reviews
    submitted_reviews = Review.query.filter_by(
        student_id=current_user.id,
        semester=current_user.semester,
        section=current_user.section
    ).all()

    submitted_teacher_ids = [review.teacher_id for review in submitted_reviews]

    return render_template(
        'student/dashboard.html',
        teacher_courses=teacher_courses,
        submitted_teacher_ids=submitted_teacher_ids
    )

@app.route('/student/review/<int:teacher_course_id>', methods=['GET', 'POST'])
@login_required
def submit_review(teacher_course_id):
    if current_user.role != 'student':
        abort(403)

    print(f"Processing review submission for teacher_course_id: {teacher_course_id}")

    teacher_course = TeacherCourse.query.get_or_404(teacher_course_id)
    print(f"Found teacher course: {teacher_course.teacher.user.name} - {teacher_course.course.name}")

    # Verify student can review this teacher-course
    if (teacher_course.semester != current_user.semester or
        teacher_course.section != current_user.section):
        flash('You are not authorized to review this professor', 'danger')
        return redirect(url_for('student_dashboard'))

    # Check if student already submitted review
    existing_review = Review.query.filter_by(
        student_id=current_user.id,
        teacher_id=teacher_course.teacher_id,
        course_id=teacher_course.course_id
    ).first()

    if existing_review:
        flash('You have already submitted a review for this professor and course', 'warning')
        return redirect(url_for('student_dashboard'))

    # Get active criteria
    criteria = ReviewCriterion.query.filter_by(active=True).all()
    print(f"Found {len(criteria)} active criteria")

    if not criteria:
        flash('No review criteria have been set up yet', 'warning')
        return redirect(url_for('student_dashboard'))

    # Create a form
    form = ReviewForm()

    if request.method == 'POST':
        print("Form submitted. Processing...")
        print(f"Form data: {request.form}")

        # Manual validation
        valid_submission = True

        # Check if all criteria have ratings
        for criterion in criteria:
            field_name = f'criterion_{criterion.id}'
            if field_name not in request.form or not request.form[field_name]:
                valid_submission = False
                flash(f'Please provide a rating for {criterion.name}', 'danger')
                break

        if valid_submission:
            try:
                print("Validation passed, creating review")

                # Debug checks
                print(f"Teacher ID: {teacher_course.teacher_id}")
                print(f"Course ID: {teacher_course.course_id}")
                print(f"Student ID: {current_user.id}")

                # Verify these objects exist
                teacher = Teacher.query.get(teacher_course.teacher_id)
                course = Course.query.get(teacher_course.course_id)
                student = User.query.get(current_user.id)

                if not teacher:
                    raise ValueError(f"Teacher with ID {teacher_course.teacher_id} not found")
                if not course:
                    raise ValueError(f"Course with ID {teacher_course.course_id} not found")
                if not student:
                    raise ValueError(f"Student with ID {current_user.id} not found")

                # Create review
                review = Review(
                    student_id=current_user.id,
                    teacher_id=teacher_course.teacher_id,
                    course_id=teacher_course.course_id,
                    semester=current_user.semester,
                    section=current_user.section,
                    comment=form.comment.data if form.comment.data else ""
                )

                db.session.add(review)
                db.session.flush()  # Get the review ID

                # Add ratings for each criterion
                for criterion in criteria:
                    field_name = f'criterion_{criterion.id}'
                    rating_value = int(request.form[field_name])

                    rating = Rating(
                        review_id=review.id,
                        criterion_id=criterion.id,
                        value=rating_value
                    )
                    db.session.add(rating)

                db.session.commit()
                print("Successfully committed review to database")

                flash('Your review has been submitted successfully', 'success')
                return redirect(url_for('student_dashboard'))

            except Exception as e:
                db.session.rollback()
                print(f"Error submitting review: {str(e)}")
                flash(f'An error occurred: {str(e)}', 'danger')

    return render_template(
        'student/review.html',
        form=form,
        teacher=teacher_course.teacher.user,
        course=teacher_course.course,
        criteria=criteria
    )

# HOD routes
@app.route('/hod/dashboard')
@login_required
def hod_dashboard():
    if current_user.role != 'hod':
        abort(403)

    # Count teachers, courses, reviews
    teacher_count = Teacher.query.count()
    course_count = Course.query.count()
    review_count = Review.query.count()
    criterion_count = ReviewCriterion.query.count()

    return render_template(
        'hod/dashboard.html',
        teacher_count=teacher_count,
        course_count=course_count,
        review_count=review_count,
        criterion_count=criterion_count
    )

@app.route('/hod/manage-criteria', methods=['GET', 'POST'])
@login_required
def manage_criteria():
    if current_user.role != 'hod':
        abort(403)

    form = CriterionForm()
    if form.validate_on_submit():
        criterion = ReviewCriterion(
            name=form.name.data,
            description=form.description.data,
            active=True
        )
        db.session.add(criterion)
        db.session.commit()
        flash('Criterion added successfully', 'success')
        return redirect(url_for('manage_criteria'))

    criteria = ReviewCriterion.query.all()
    return render_template('hod/manage_criteria.html', form=form, criteria=criteria)

@app.route('/hod/toggle-criterion/<int:criterion_id>')
@login_required
def toggle_criterion(criterion_id):
    if current_user.role != 'hod':
        abort(403)

    criterion = ReviewCriterion.query.get_or_404(criterion_id)
    criterion.active = not criterion.active
    db.session.commit()

    status = "activated" if criterion.active else "deactivated"
    flash(f'Criterion "{criterion.name}" {status}', 'success')
    return redirect(url_for('manage_criteria'))

@app.route('/hod/delete-criterion/<int:criterion_id>')
@login_required
def delete_criterion(criterion_id):
    if current_user.role != 'hod':
        abort(403)

    criterion = ReviewCriterion.query.get_or_404(criterion_id)

    # Check if criterion has been used in any ratings
    if Rating.query.filter_by(criterion_id=criterion_id).first():
        flash('Cannot delete criterion that has been used in reviews', 'danger')
        return redirect(url_for('manage_criteria'))

    db.session.delete(criterion)
    db.session.commit()
    flash(f'Criterion "{criterion.name}" deleted', 'success')
    return redirect(url_for('manage_criteria'))

@app.route('/hod/manage-teachers', methods=['GET', 'POST'])
@login_required
def manage_teachers():
    if current_user.role != 'hod':
        abort(403)

    # Form for registering a new teacher
    teacher_form = RegisterForm()
    teacher_form.role.choices = [('teacher', 'Teacher')]  # Override the choices

    # Course form
    course_form = CourseForm()

    # Teacher-Course assignment form
    tc_form = TeacherCourseForm()
    
    # Update choices for teacher and course dropdowns
    tc_form.teacher_id.choices = [
        (t.id, f"{t.user.name}") 
        for t in Teacher.query.join(User).order_by(User.name).all()
    ]
    tc_form.course_id.choices = [
        (c.id, f"{c.code} - {c.name}") 
        for c in Course.query.order_by(Course.code).all()
    ]

    if request.method == 'POST':
        # Process teacher registration
        if 'register_teacher' in request.form and teacher_form.validate_on_submit():
            try:
                if not teacher_form.email.data.endswith('@rcciit.org.in'):
                    flash('Email must end with @rcciit.org.in', 'danger')
                else:
                    # Create user account
                    user = User(
                        name=teacher_form.name.data,
                        email=teacher_form.email.data,
                        role='teacher'
                    )
                    # Generate default password
                    default_password = user.email.split('@')[0] + "@123"
                    user.set_password(default_password)
                    db.session.add(user)
                    db.session.flush()  # Get user.id before committing

                    # Create teacher profile
                    teacher = Teacher(
                        user_id=user.id,
                        department='IT'  # Set default department
                    )
                    db.session.add(teacher)
                    db.session.commit()

                    flash(f'Teacher registered successfully. Default password is: {default_password}', 'success')
                    return redirect(url_for('manage_teachers'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error registering teacher: {str(e)}', 'danger')

        # Process course creation
        elif 'add_course' in request.form and course_form.validate_on_submit():
            try:
                # Check if course code already exists
                existing_course = Course.query.filter_by(code=course_form.code.data).first()
                if existing_course:
                    flash('A course with this code already exists', 'danger')
                else:
                    course = Course(
                        name=course_form.name.data,
                        code=course_form.code.data.upper()  # Convert to uppercase
                    )
                    db.session.add(course)
                    db.session.commit()
                    flash('Course added successfully', 'success')
                    return redirect(url_for('manage_teachers'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding course: {str(e)}', 'danger')

        # Process teacher-course assignment
        elif 'assign_teacher' in request.form and tc_form.validate_on_submit():
            try:
                # Check if this combination already exists
                existing = TeacherCourse.query.filter_by(
                    course_id=tc_form.course_id.data,
                    semester=int(tc_form.semester.data),
                    section=tc_form.section.data
                ).first()

                if existing:
                    flash(f'This course already has a teacher assigned for Semester {tc_form.semester.data}, Section {tc_form.section.data}', 'danger')
                else:
                    tc = TeacherCourse(
                        teacher_id=tc_form.teacher_id.data,
                        course_id=tc_form.course_id.data,
                        semester=int(tc_form.semester.data),
                        section=tc_form.section.data
                    )
                    db.session.add(tc)
                    db.session.commit()
                    flash('Teacher assigned to course successfully', 'success')
                    return redirect(url_for('manage_teachers'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error assigning teacher: {str(e)}', 'danger')

    # Get data for display
    teachers = Teacher.query.join(User).order_by(User.name).all()
    courses = Course.query.order_by(Course.code).all()
    teacher_courses = TeacherCourse.query.join(Teacher).join(Course).all()

    return render_template(
        'hod/manage_teachers.html',
        teacher_form=teacher_form,
        course_form=course_form,
        tc_form=tc_form,
        teachers=teachers,
        courses=courses,
        teacher_courses=teacher_courses
    )

@app.route('/hod/delete-teacher-course/<int:tc_id>')
@login_required
def delete_teacher_course(tc_id):
    if current_user.role != 'hod':
        abort(403)

    tc = TeacherCourse.query.get_or_404(tc_id)

    # Check if there are reviews for this assignment
    if Review.query.filter_by(
        teacher_id=tc.teacher_id,
        course_id=tc.course_id,
        semester=tc.semester,
        section=tc.section
    ).first():
        flash('Cannot delete assignment that has received reviews', 'danger')
        return redirect(url_for('manage_teachers'))

    db.session.delete(tc)
    db.session.commit()
    flash('Teacher course assignment deleted', 'success')
    return redirect(url_for('manage_teachers'))

@app.route('/hod/view-reviews')
@login_required
def view_reviews():
    if current_user.role != 'hod':
        abort(403)

    # Get all teachers with their reviews and ratings
    teachers = Teacher.query.join(User).all()

    teacher_stats = []
    for teacher in teachers:
        # Get all reviews for this teacher
        reviews = Review.query.filter_by(teacher_id=teacher.id).all()

        review_data = []
        for review in reviews:
            try:
                # Get the course information
                course = Course.query.get(review.course_id)

                # Get all ratings for this review
                ratings = Rating.query.filter_by(review_id=review.id).join(ReviewCriterion).all()

                # Calculate average rating
                avg_rating = sum(r.value for r in ratings) / len(ratings) if ratings else 0

                # Get student information
                student = User.query.get(review.student_id)

                review_data.append({
                    'student_name': student.name,
                    'course_name': course.name,
                    'course_code': course.code,
                    'semester': review.semester,
                    'section': review.section,
                    'comment': review.comment,
                    'ratings': ratings,
                    'average_rating': round(avg_rating, 2),
                    'date': review.created_at
                })
            except Exception as e:
                print(f"Error processing review {review.id}: {str(e)}")
                continue

        # Calculate overall statistics for the teacher
        all_ratings = Rating.query.join(Review).filter(Review.teacher_id == teacher.id).all()
        overall_avg = sum(r.value for r in all_ratings) / len(all_ratings) if all_ratings else 0

        teacher_stats.append({
            'teacher': teacher,
            'reviews': review_data,
            'review_count': len(reviews),
            'overall_rating': round(overall_avg, 2)
        })

    # Debug print statements
    print(f"Found {len(teacher_stats)} teachers")
    for stats in teacher_stats:
        print(f"Teacher: {stats['teacher'].user.name}")
        print(f"Review count: {stats['review_count']}")
        print(f"Reviews: {len(stats['reviews'])}")

    return render_template('hod/view_reviews.html', teacher_stats=teacher_stats)

@app.route('/hod/teacher-reviews/<int:teacher_id>')
@login_required
def teacher_reviews(teacher_id):
    if current_user.role != 'hod':
        abort(403)

    teacher = Teacher.query.get_or_404(teacher_id)

    # Get all reviews for this teacher
    reviews = Review.query.filter_by(teacher_id=teacher_id).order_by(Review.created_at.desc()).all()

    review_data = []
    for review in reviews:
        # Get the course
        course = Course.query.get(review.course_id)

        # Get the student
        student = User.query.get(review.student_id)

        # Get ratings with criteria
        ratings = Rating.query.filter_by(review_id=review.id).join(ReviewCriterion).all()

        # Calculate average rating
        avg_rating = sum(r.value for r in ratings) / len(ratings) if ratings else 0

        review_data.append({
            'review': review,
            'course': course,
            'student': student,
            'ratings': ratings,
            'average_rating': round(avg_rating, 2)
        })

    return render_template(
        'hod/teacher_reviews.html',
        teacher=teacher,
        review_data=review_data
    )

if __name__ == '__main__':
    app.run(debug=True)
