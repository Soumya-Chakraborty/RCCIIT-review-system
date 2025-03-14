from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError, Optional
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Regexp(r'.*@rcciit\.org\.in$', message="Email must end with @rcciit.org.in")
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher')])
    password = PasswordField('Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm Password', validators=[Optional(), EqualTo('password')])
    roll_number = StringField('Roll Number', validators=[Optional()])
    semester = SelectField('Semester', choices=[(str(i), str(i)) for i in range(1, 9)], validators=[Optional()])
    section = SelectField('Section', choices=[('A', 'A'), ('B', 'B')], validators=[Optional()])
    submit = SubmitField('Register')

    def validate(self):
        if not super().validate():
            return False

        if self.role.data == 'student':
            if not self.password.data:
                self.password.errors = ['Password is required for students']
                return False
            if not self.roll_number.data:
                self.roll_number.errors = ['Roll Number is required for students']
                return False
            if not self.semester.data:
                self.semester.errors = ['Semester is required for students']
                return False
            if not self.section.data:
                self.section.errors = ['Section is required for students']
                return False

        return True

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please log in instead.')

class ReviewForm(FlaskForm):
    teacher_course_id = HiddenField('Teacher Course ID')  # Remove DataRequired validator
    comment = TextAreaField('Additional Comments', validators=[Optional()])
    submit = SubmitField('Submit Review')

    # Dynamic fields for rating criteria will be added in the route

class CriterionForm(FlaskForm):
    name = StringField('Criterion Name', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Criterion')

class TeacherCourseForm(FlaskForm):
    teacher_id = SelectField('Teacher', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    semester = SelectField('Semester', 
                         choices=[(str(i), f'Semester {i}') for i in range(1, 9)],
                         validators=[DataRequired()])
    section = SelectField('Section',
                         choices=[('A', 'Section A'), ('B', 'Section B')],
                         validators=[DataRequired()])
    submit = SubmitField('Assign Teacher')

class CourseForm(FlaskForm):
    name = StringField('Course Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message="Course name must be between 3 and 100 characters")
    ])
    code = StringField('Course Code', validators=[
        DataRequired(),
        Length(min=2, max=20, message="Course code must be between 2 and 20 characters"),
        Regexp(r'^[A-Z0-9-]+$', message="Course code must contain only uppercase letters, numbers, and hyphens")
    ])
    submit = SubmitField('Add Course')
