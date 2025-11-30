# Quiz Event Application Documentation

---

## Title Page

**Quiz Event Application**
**Comprehensive User & Developer Documentation**
Version 1.0 | © 2025

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Architecture Overview](#architecture-overview)
5. [Directory Structure](#directory-structure)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [Data Model](#data-model)
9. [URL & API Reference](#url--api-reference)
10. [Customization & Theming](#customization--theming)
11. [Running Tests](#running-tests)
12. [License & Contributing](#license--contributing)
13. [Appendix](#appendix)

---

## Project Overview
The Quiz Event Application is a Django-based web application for managing and participating in quizzes and events. It empowers users to register, login, browse quizzes, submit answers, view scores, and stay updated on upcoming events.

---

## Features
- User registration, login, and logout
- Browse available quizzes
- Take quizzes (supports Multiple Choice and Text questions)
- Instant results/score upon submission
- Participate/view event listings
- Modern responsive UI with Tailwind CSS
- Admin interface for quiz and event management
- Complete REST API with Django REST Framework
- JWT-based API authentication (SimpleJWT)
- API endpoints for quizzes, events, submissions, and user answers
- Modular app structure for easy maintenance

---

## Tech Stack
- **Backend:** Python 3.8+, Django 3.2+ (uses Django 5 for this version), Django REST Framework, SimpleJWT
- **Frontend:** HTML5, Django templates, Tailwind CSS
- **Database:** SQLite3 (default for development)
- **Other:** Node.js (for Tailwind via theme/static_src)

---

## Architecture Overview
- **MVC-based Django app**
- Separation of: Quiz management, User authentication, Event handling
- Modular apps (`quiz`, `theme`)
- REST endpoints for token authentication
- Admin auto-generated via Django admin for authorized management

---

## Directory Structure
- **QuizEvent/**: Main Django project
  - **QuizEvent/**: Django project settings, URLs, WSGI/ASGI
  - **quiz/**: All quiz/event models, views, forms, urls, and templates
  - **theme/**: Custom theming and configuration (Tailwind CSS)
  - **db.sqlite3**: SQLite database
  - **manage.py**: Django management script
  - **requirements.txt**: List of dependencies
  - **templates/**: Shared layout/templates (in theme/static_src/templates as well)

---

## Installation & Setup
### Prerequisites
- Python 3.8 or newer
- pip
- Node.js (for Tailwind CSS)
- Git (for cloning)

### Steps
1. **Clone the repository**
   ```bash
   git clone https://github.com/meeraahir/Quiz-Event-Application
   cd "Quiz Event Application"
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Mac/Linux
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```
5. **(Optional) Load initial quiz data:**
   ```bash
   python manage.py loaddata QuizEvent/quiz/fixtures/initial_data.json
   ```
6. **Run development server:**
   ```bash
   python manage.py runserver
   ```
7. **Visit** [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your web browser

---

## Usage Guide
### For End Users
- **Register** for a new account on the Register page
- **Login** using your username and password
- **Quiz List:** Browse available quizzes and select one to participate
- **Quiz Detail:** Answer all questions and submit
- **Get Results:** View your score and the correct answers post-submission
- **Events:** Check the Events page for upcoming events

*<Insert screenshots here for each step, if available>*

### For Admins
- Access `/admin/` (login as superuser)
- Manage Quizzes, Questions, Answers, Users, and Events from the admin dashboard

---

## Data Model
### Main Entities

| Table            | Fields                                                | Description                            |
|------------------|------------------------------------------------------|----------------------------------------|
| Quiz             | id, title, description, created_at, updated_at        | A quiz containing multiple Questions   |
| Question         | id, quiz(fk), text, question_type, created_at         | Each question belongs to a Quiz        |
| Answer           | id, question(fk), text, is_correct                    | Possible answers to a Question         |
| UserSubmission   | id, quiz(fk), user_name(fk), score, submitted_at      | One user's attempt at a Quiz           |
| UserAnswer      | submission(fk), question(fk), answer(fk), is_correct  | User answer per question per submission|
| Event            | id, title, description, date, location                | Defines events users can join/see      |

### Relationships
- Each Quiz has many Questions
- Each Question can have multiple Answers
- A UserSubmission links a user and a quiz attempt
- UserAnswer ties the submission, question, and selected answer
- Event is standalone
- Uses Django's User model for users

See [`QuizEvent/quiz/models.py`](QuizEvent/quiz/models.py) for detailed class definitions.

---

## URL & API Reference
### Main URLs
| URL                        | View/Class           | Purpose                                 |
|----------------------------|----------------------|-----------------------------------------|
| `/`                        | index                | Home page                               |
| `/register/`               | RegisterView         | User registration                       |
| `/login/`                  | CustomLoginView      | User login                              |
| `/logout/`                 | LogoutView           | Log out                                 |
| `/quiz_list/`              | QuizList             | List all quizzes                        |
| `/quiz/<int:pk>/`          | QuizDetail           | Take a specific quiz                    |
| `/result/<int:submission_id>/` | quiz_result      | View quiz result                        |
| `/events/`                 | event                | List/view events                        |
| `/admin/`                  | Django Admin         | Admin dashboard                         |

### REST API Endpoints

#### Authentication Endpoints
| URL                   | Method | Description                | Auth Required |
|-----------------------|--------|----------------------------|---------------|
| `/api/register/`      | POST   | User registration          | No            |
| `/api/login/`         | POST   | User login (returns JWT)   | No            |
| `/api/token/`         | POST   | Get JWT access token       | No            |
| `/api/token/refresh/` | POST   | Refresh JWT token          | No            |

#### Quiz Endpoints
| URL                    | Method | Description                    | Auth Required |
|------------------------|--------|--------------------------------|---------------|
| `/api/quizzes/`        | GET    | List all quizzes               | Yes           |
| `/api/quizzes/<id>/`   | GET    | Get quiz details with questions| Yes           |
| `/api/quiz/create/`    | POST   | Create a new quiz              | Yes           |
| `/api/quiz/submit/`    | POST   | Submit quiz answers             | Yes           |

#### Event Endpoints
| URL                  | Method | Description              | Auth Required |
|----------------------|--------|--------------------------|---------------|
| `/api/events/`       | GET    | List all events          | Yes           |
| `/api/events/<id>/`  | GET    | Get event details        | Yes           |
| `/api/event/create/` | POST   | Create a new event        | Yes           |

#### Submission Endpoints
| URL                        | Method | Description                    | Auth Required |
|----------------------------|--------|--------------------------------|---------------|
| `/api/submissions/`        | GET    | List user quiz submissions      | Yes           |
| `/api/submissions/<id>/`   | GET    | Get submission details          | Yes           |

#### User Answer Endpoints
| URL                          | Method | Description                    | Auth Required |
|------------------------------|--------|--------------------------------|---------------|
| `/api/user-answers/`         | GET    | List user answers               | Yes           |
| `/api/user-answers/<id>/`    | GET    | Get user answer details         | Yes           |

#### Question Endpoints
| URL                          | Method | Description                    | Auth Required |
|------------------------------|--------|--------------------------------|---------------|
| `/api/question/create/`      | POST   | Create a new question           | Yes           |

#### Answer Endpoints
| URL                          | Method | Description                    | Auth Required |
|------------------------------|--------|--------------------------------|---------------|
| `/api/answer/create/`        | POST   | Create a new answer             | Yes           |

**Note:** All API endpoints (except authentication) require JWT authentication. Include the token in the Authorization header: `Authorization: Bearer <access_token>`

### API Request/Response Examples

#### Create Quiz
**Endpoint:** `POST /api/quiz/create/`

**Request Body:**
```json
{
  "title": "Python Basics Quiz",
  "description": "Test your knowledge of Python fundamentals"
}
```

**Response (201 Created):**
```json
{
  "message": "Quiz created successfully",
  "quiz": {
    "id": 1,
    "title": "Python Basics Quiz",
    "description": "Test your knowledge of Python fundamentals",
    "questions": []
  }
}
```

#### Submit Quiz
**Endpoint:** `POST /api/quiz/submit/`

**Request Body:**
```json
{
  "quiz_id": 1,
  "answers": {
    "1": "5",
    "2": "What is Python? Python is a programming language."
  }
}
```
*Note: For MCQ questions, provide the answer ID as a string. For TEXT questions, provide the answer text directly.*

**Response (201 Created):**
```json
{
  "message": "Quiz submitted successfully",
  "submission": {
    "id": 1,
    "quiz": {...},
    "user_name": 1,
    "score": 8,
    "submitted_at": "2025-01-15T10:30:00Z",
    "user_answers": [...]
  }
}
```

#### Create Question
**Endpoint:** `POST /api/question/create/`

**Request Body:**
```json
{
  "quiz_id": 1,
  "text": "What is the capital of France?",
  "question_type": "MCQ"
}
```
*Note: `question_type` must be either "MCQ" or "TEXT".*

**Response (201 Created):**
```json
{
  "message": "Question created successfully",
  "question": {
    "id": 1,
    "text": "What is the capital of France?",
    "question_type": "MCQ",
    "answers": []
  }
}
```

#### Create Answer
**Endpoint:** `POST /api/answer/create/`

**Request Body:**
```json
{
  "question_id": 1,
  "text": "Paris",
  "is_correct": true
}
```

**Response (201 Created):**
```json
{
  "message": "Answer created successfully",
  "answer": {
    "id": 1,
    "text": "Paris",
    "is_correct": true
  }
}
```

#### Create Event
**Endpoint:** `POST /api/event/create/`

**Request Body:**
```json
{
  "title": "Python Workshop 2025",
  "description": "Learn Python from scratch",
  "date": "2025-02-15",
  "location": "Conference Hall A"
}
```

**Response (201 Created):**
```json
{
  "message": "Event created successfully",
  "event": {
    "id": 1,
    "title": "Python Workshop 2025",
    "description": "Learn Python from scratch",
    "date": "2025-02-15",
    "location": "Conference Hall A"
  }
}
```

---

## Customization & Theming
- Uses Tailwind CSS for rapid, utility-first styling
- Main styling in `theme/static_src/src/styles.css`
- For customization:
  - Edit or extend Tailwind config/postcss.config.js
  - Add your own CSS in the same folder
- Django template inheritance and block overrides in HTML
- All templates and their layouts can be found in `quiz/templates/` and `theme/templates/`

---

## Running Tests
This project comes with a basic Django test skeleton. To run tests:
```bash
python manage.py test
```
Add more tests in `QuizEvent/quiz/tests.py` as the project grows.

---

## License & Contributing
- **License:** For educational purposes only (feel free to add an OSI license if required)
- **Contributions:** Submit issues or pull requests via GitHub or your project repo
- Contact maintainer: `<Your Name/Email here>`

---

## Appendix
- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs/installation)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

*End of Documentation*

---
