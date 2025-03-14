# RCCIIT Professor Review System

![Project Status](https://img.shields.io/badge/status-active-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.0%2B-red)

A comprehensive web application for RCCIIT (RCC Institute of Information Technology) that enables students to provide structured feedback on professors and their teaching methods. This system helps the Head of Department (HOD) make data-driven decisions to improve teaching quality.

## ✨ Features

### For Students
- **Secure Authentication**: Login with institutional email (@rcciit.org.in)
- **Course-Specific Reviews**: Submit detailed reviews for professors based on courses
- **Star Rating System**: Rate professors on multiple customizable criteria
- **Anonymous Feedback**: Provide honest feedback without fear of repercussions

### For HOD
- **Professor Management**: Register new professors and manage their course assignments
- **Course Management**: Add and organize courses in the system
- **Feedback Analysis**: View comprehensive analytics on professor performance
- **Review Management**: See detailed reviews with ratings and comments
- **Custom Criteria**: Define and manage evaluation criteria for reviews

## 🖥️ Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-Migrate
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript, Font Awesome
- **Database**: SQLite (development), supports PostgreSQL (production)
- **Authentication**: Custom email/password authentication

## 📝 Prerequisites

- Python 3.7 or higher
- Pip package manager
- Internet connection (for CDN resources)

## 🚀 Installation and Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/rcciit-review-system.git
   cd rcciit-review-system
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   - Create a `.env` file in the root directory
   - Add the following environment variables:
     ```
     SECRET_KEY=your_secret_key
     DATABASE_URL=sqlite:///rcciit_review.db
     FLASK_APP=app.py
     FLASK_ENV=development
     ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   flask run
   ```

7. **Access the application**
   - Open your browser and navigate to `http://127.0.0.1:5000`
   - Login with the HOD account (default credentials):
     - Email: hod@rcciit.org.in
     - Password: hodadmin123

## 📊 System Workflow

1. **HOD Setup**:
   - Register professors
   - Add courses
   - Assign professors to courses
   - Define review criteria

2. **Student Review Process**:
   - Login with institutional email
   - View courses for their semester and section
   - Select a professor to review
   - Rate on various criteria
   - Submit additional comments

3. **Feedback Analysis**:
   - HOD can view all reviews
   - Analyze professor performance
   - Identify strengths and areas for improvement

## 🔒 Security Features

- Password hashing with Werkzeug security
- CSRF protection with Flask-WTF
- Role-based access control
- Input validation and sanitization
- Institutional email validation (@rcciit.org.in)

## 🧪 Testing

```bash
# Run tests
python -m unittest discover tests
```

## 📁 Project Structure

```
rcciit-review-system/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── models.py           # Database models
├── forms.py            # Form definitions
├── static/             # Static files (CSS, JS)
├── templates/          # HTML templates
│   ├── auth/           # Authentication templates
│   ├── hod/            # HOD dashboard templates
│   ├── student/        # Student dashboard templates
│   └── base.html       # Base template
├── migrations/         # Database migrations
├── tests/              # Test files
└── requirements.txt    # Project dependencies
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- RCCIIT Administration for supporting this initiative
- All students and professors who contributed feedback
- The Flask and SQLAlchemy communities

## 📞 Contact

For any questions or suggestions, please reach out to:
- Project Maintainer: [Your Name](mailto:your.email@example.com)
- RCCIIT IT Department: [IT Department](mailto:it@rcciit.org.in)

---

Made with ❤️ for RCCIIT by [Your Name]
