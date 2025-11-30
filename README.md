# Quiz Event Application

This is a Django-based web application for hosting and participating in quizzes and events.

## Features
- User Authentication (Login, Registration, Logout)
- Browse & Participate in Quizzes
- View and participate in Events
- Modern responsive design using Tailwind CSS
- **REST API** with Django REST Framework
- **JWT Authentication** for API access
- API endpoints for quizzes, events, submissions, and user management

## Requirements
- Python 3.8+
- pip
- Django (recommended version: 3.2+)
- (Optional) Virtualenv for isolated installations

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/meeraahir/Quiz-Event-Application
   cd "Quiz Event Application"
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

5. **(Optional) Load Initial Data**
   ```bash
   python manage.py loaddata QuizEvent/quiz/fixtures/initial_data.json
   ```

6. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access the App**
   Open your browser and go to `http://127.0.0.1:8000/`

---

## API Usage

The application provides a REST API for programmatic access. All API endpoints are prefixed with `/api/`.

### Authentication
1. **Register a new user:**
   ```bash
   POST /api/register/
   Body: {"username": "user", "email": "user@example.com", "password": "password123", "confirm_password": "password123"}
   ```

2. **Login to get JWT token:**
   ```bash
   POST /api/login/
   Body: {"username": "user", "password": "password123"}
   Response: {"access": "<token>", "refresh": "<token>", "message": "Login successful"}
   ```

3. **Or use JWT token endpoint:**
   ```bash
   POST /api/token/
   Body: {"username": "user", "password": "password123"}
   ```

### API Endpoints
- **Quizzes:** 
  - `GET /api/quizzes/` - List all quizzes
  - `GET /api/quizzes/<id>/` - Get quiz details
  - `POST /api/quiz/create/` - Create a new quiz
  - `POST /api/quiz/submit/` - Submit quiz answers
- **Events:** 
  - `GET /api/events/` - List all events
  - `GET /api/events/<id>/` - Get event details
  - `POST /api/event/create/` - Create a new event
- **Submissions:** `GET /api/submissions/` - List quiz submissions
- **User Answers:** `GET /api/user-answers/` - List user answers
- **Questions:** `POST /api/question/create/` - Create a new question
- **Answers:** `POST /api/answer/create/` - Create a new answer

**Note:** Include JWT token in Authorization header: `Authorization: Bearer <access_token>`

For detailed API documentation with request/response examples, see `QuizEventApp_Documentation.md`.

---

## Project Structure
- `QuizEvent/` : Main Django project folder
- `quiz/`      : Core quiz & events app (includes API views and serializers)
- `templates/` : HTML templates
- `static/`    : Static files (CSS, JS)

---

## License
This project is for educational purposes.
