# Quiz Event Application

This is a Django-based web application for hosting and participating in quizzes and events.

## Features
- User Authentication (Login, Registration, Logout)
- Browse & Participate in Quizzes
- View and participate in Events
- Modern responsive design using Tailwind CSS

## Requirements
- Python 3.8+
- pip
- Django (recommended version: 3.2+)
- (Optional) Virtualenv for isolated installations

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <your_repo_url>
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

## Project Structure
- `QuizEvent/` : Main Django project folder
- `quiz/`      : Core quiz & events app
- `templates/` : HTML templates
- `static/`    : Static files (CSS, JS)

---

## License
This project is for educational purposes.
