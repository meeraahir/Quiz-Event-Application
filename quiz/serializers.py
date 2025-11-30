from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Quiz, Question, Answer, UserSubmission, UserAnswer, Event


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_2 = serializers.CharField(write_only=True, required=True)  # confirm password

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_2']

    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError("Username is required.")

        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")

        if len(value) > 150:
            raise serializers.ValidationError("Username must be at most 150 characters long.")

        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")

        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")

        value = value.strip().lower()

        if len(value) > 254:
            raise serializers.ValidationError("Email address is too long.")

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError("Please enter a valid email address.")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        return value

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password is required.")

        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if len(value) > 128:
            raise serializers.ValidationError("Password must be at most 128 characters long.")

        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")

        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number.")

        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))

        return value

    def validate(self, attrs):
        password = attrs.get('password', '')
        password_2 = attrs.get('password_2', '')

        if not password_2:
            raise serializers.ValidationError({'password_2': 'Please confirm your password.'})

        if password != password_2:
            raise serializers.ValidationError({'password': 'Passwords do not match. Please try again.'})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "question_type", "answers"]

    def validate(self, attrs):
        quiz = attrs.get("quiz")
        text = attrs.get("text")

        if Question.objects.filter(quiz=quiz, text__iexact=text).exists():
            raise serializers.ValidationError(
                {"detail": "This question already exists for this quiz."}
            )

        return attrs


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "questions"]


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = "__all__"


class UserSubmissionSerializer(serializers.ModelSerializer):
    user_answers = UserAnswerSerializer(many=True, read_only=True)
    quiz = QuizSerializer(read_only=True)

    class Meta:
        model = UserSubmission
        fields = ["id", "quiz", "user_name", "score", "submitted_at", "user_answers"]


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class QuizCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['title', 'description']

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Quiz title is required.")

        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError("Quiz title must be at least 3 characters long.")

        if len(value) > 255:
            raise serializers.ValidationError("Quiz title must be at most 255 characters long.")

        return value

    def validate_description(self, value):
        if value is not None:
            value = value.strip() if isinstance(value, str) else value
            if isinstance(value, str) and len(value) > 5000:
                raise serializers.ValidationError("Description must be at most 5000 characters long.")

        return value


class QuestionCreateSerializer(serializers.ModelSerializer):
    quiz_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Question
        fields = ['quiz_id', 'text', 'question_type']

    def validate_quiz_id(self, value):
        if value is None:
            raise serializers.ValidationError("Quiz ID is required.")

        if not isinstance(value, int):
            raise serializers.ValidationError("Quiz ID must be an integer.")

        if value <= 0:
            raise serializers.ValidationError("Quiz ID must be a positive integer.")

        try:
            quiz = Quiz.objects.get(id=value)
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz does not exist.")

        return value

    def validate_text(self, value):
        if not value:
            raise serializers.ValidationError("Question text is required.")

        value = value.strip()

        if len(value) < 5:
            raise serializers.ValidationError("Question text must be at least 5 characters long.")

        if len(value) > 2000:
            raise serializers.ValidationError("Question text must be at most 2000 characters long.")

        return value

    def validate_question_type(self, value):
        if not value:
            raise serializers.ValidationError("Question type is required.")

        valid_types = ['MCQ', 'TEXT']
        if value not in valid_types:
            raise serializers.ValidationError(f"Question type must be one of: {', '.join(valid_types)}")

        return value

    def validate(self, attrs):
        quiz_id = attrs.get('quiz_id')
        text = attrs.get('text').strip()

        if Question.objects.filter(quiz_id=quiz_id, text__iexact=text).exists():
            raise serializers.ValidationError(
                {"detail": "This question already exists for this quiz."}
            )

        return attrs

    def create(self, validated_data):
        quiz_id = validated_data.pop('quiz_id')
        quiz = Quiz.objects.get(id=quiz_id)
        return Question.objects.create(quiz=quiz, **validated_data)


class AnswerCreateSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Answer
        fields = ['question_id', 'text', 'is_correct']

    def validate_question_id(self, value):
        if value is None:
            raise serializers.ValidationError("Question ID is required.")

        if not isinstance(value, int):
            raise serializers.ValidationError("Question ID must be an integer.")

        if value <= 0:
            raise serializers.ValidationError("Question ID must be a positive integer.")

        try:
            question = Question.objects.get(id=value)
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question does not exist.")

        return value

    def validate_text(self, value):
        if not value:
            raise serializers.ValidationError("Answer text is required.")

        value = value.strip()

        if len(value) < 1:
            raise serializers.ValidationError("Answer text cannot be empty.")

        if len(value) > 255:
            raise serializers.ValidationError("Answer text must be at most 255 characters long.")

        return value

    def validate_is_correct(self, value):
        if value is None:
            raise serializers.ValidationError("is_correct field is required.")

        if not isinstance(value, bool):
            raise serializers.ValidationError("is_correct must be a boolean value.")

        return value

    def validate(self, data):
        question_id = data.get('question_id')
        is_correct = data.get('is_correct', False)

        if question_id:
            try:
                question = Question.objects.get(id=question_id)

                if question.question_type == 'MCQ' and is_correct:
                    existing_correct = Answer.objects.filter(question=question, is_correct=True).exists()
                    if existing_correct:
                        raise serializers.ValidationError(
                            "This question already has a correct answer. MCQ questions should have only one correct answer."
                        )
            except Question.DoesNotExist:
                pass

        return data

    def create(self, validated_data):
        question_id = validated_data.pop('question_id')
        question = Question.objects.get(id=question_id)
        answer = Answer.objects.create(question=question, **validated_data)
        return answer


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location']

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Event title is required.")

        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError("Event title must be at least 3 characters long.")

        if len(value) > 255:
            raise serializers.ValidationError("Event title must be at most 255 characters long.")

        return value

    def validate_description(self, value):
        if value is not None:
            value = value.strip() if isinstance(value, str) else value
            if isinstance(value, str) and len(value) > 5000:
                raise serializers.ValidationError("Description must be at most 5000 characters long.")

        return value

    def validate_date(self, value):
        if not value:
            raise serializers.ValidationError("Event date is required.")

        return value

    def validate_location(self, value):
        if not value:
            raise serializers.ValidationError("Event location is required.")

        value = value.strip()

        if len(value) < 3:
            raise serializers.ValidationError("Event location must be at least 3 characters long.")

        if len(value) > 255:
            raise serializers.ValidationError("Event location must be at most 255 characters long.")

        return value


class QuizSubmissionSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    answers = serializers.DictField(
        child=serializers.CharField(allow_blank=False),
        help_text="Dictionary with question_id as key and answer_id (for MCQ) or text (for TEXT) as value"
    )

    def validate_quiz_id(self, value):
        if value is None:
            raise serializers.ValidationError("Quiz ID is required.")

        if not isinstance(value, int):
            raise serializers.ValidationError("Quiz ID must be an integer.")

        if value <= 0:
            raise serializers.ValidationError("Quiz ID must be a positive integer.")

        try:
            quiz = Quiz.objects.get(id=value)
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz does not exist.")

        return value

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("Answers dictionary cannot be empty.")

        if not isinstance(value, dict):
            raise serializers.ValidationError("Answers must be a dictionary.")

        return value

    def validate(self, data):
        quiz_id = data.get('quiz_id')
        answers = data.get('answers', {})

        if not quiz_id:
            raise serializers.ValidationError("Quiz ID is required.")

        if not answers:
            raise serializers.ValidationError("Answers are required.")

        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            raise serializers.ValidationError("Quiz does not exist.")

        if not quiz.questions.exists():
            raise serializers.ValidationError("This quiz has no questions available.")

        quiz_questions = quiz.questions.all()
        question_ids = set(str(q.id) for q in quiz_questions)
        answer_keys = set(answers.keys())

        if len(answers) > len(quiz_questions):
            raise serializers.ValidationError(
                "Too many answers provided. Please provide answers only for questions in this quiz.")

        for question in quiz_questions:
            question_key = str(question.id)
            if question_key not in answers:
                raise serializers.ValidationError(f"Please answer question: {question.text[:50]}...")

            answer_value = answers[question_key]

            if answer_value is None:
                raise serializers.ValidationError(f"Answer cannot be null for question: {question.text[:50]}...")

            if not isinstance(answer_value, str):
                raise serializers.ValidationError(f"Answer must be a string for question: {question.text[:50]}...")

            answer_value = answer_value.strip()

            if question.question_type == 'MCQ':
                # Validate MCQ answer
                if not answer_value or answer_value == '':
                    raise serializers.ValidationError(f"Please answer question: {question.text[:50]}...")

                try:
                    answer_id = int(answer_value)
                except (ValueError, TypeError):
                    raise serializers.ValidationError(
                        f"Invalid answer format for question: {question.text[:50]}. Expected a numeric answer ID.")

                if answer_id <= 0:
                    raise serializers.ValidationError(
                        f"Answer ID must be a positive integer for question: {question.text[:50]}...")

                try:
                    selected_answer = Answer.objects.get(id=answer_id)
                except Answer.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Selected answer does not exist for question: {question.text[:50]}...")

                if selected_answer.question != question:
                    raise serializers.ValidationError(
                        f"Invalid answer selected. Answer does not belong to question: {question.text[:50]}...")

            elif question.question_type == 'TEXT':
                if not answer_value or answer_value == '':
                    raise serializers.ValidationError(f"Please provide an answer for: {question.text[:50]}...")

                if len(answer_value) > 1000:
                    raise serializers.ValidationError(
                        f"Text answer is too long. Maximum 1000 characters allowed for question: {question.text[:50]}...")

                if len(answer_value) < 1:
                    raise serializers.ValidationError(
                        f"Text answer cannot be empty for question: {question.text[:50]}...")
            else:
                raise serializers.ValidationError(f"Unknown question type for question: {question.text[:50]}...")

        return data
