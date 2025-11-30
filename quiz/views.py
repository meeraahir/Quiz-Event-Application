from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django import forms
from django.db.models import Count
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, FormView

from .models import Quiz, UserAnswer, Answer, UserSubmission, Event
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import RegisterForm, LoginForm


# Create your views here.

def index(request):
    return render(request, 'home.html')


class RegisterView(View):
    template_name = "register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            username = username.strip() if username else ""
            email = email.strip().lower() if email else ""

            if not username:
                form.add_error("username", "Username is required.")
                return render(request, self.template_name, {"form": form})

            if not email:
                form.add_error("email", "Email is required.")
                return render(request, self.template_name, {"form": form})

            if User.objects.filter(username__iexact=username).exists():
                form.add_error("username", "A user with this username already exists.")
                return render(request, self.template_name, {"form": form})

            if User.objects.filter(email__iexact=email).exists():
                form.add_error("email", "A user with this email already exists.")
                return render(request, self.template_name, {"form": form})

            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully")
            return redirect("login")
        return render(request, self.template_name, {"form": form})


class CustomLoginView(LoginView):
    template_name = "login.html"
    authentication_form = LoginForm

    def form_valid(self, form):
        messages.success(self.request, "Login Successful")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home')


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Logout Successful")
        return redirect("login")


class QuizList(ListView, LoginRequiredMixin):
    model = Quiz
    template_name = 'quiz_list.html'
    context_object_name = 'quizzes'

    login_url = '/login/'

    def get_queryset(self):
        return Quiz.objects.annotate(num_questions=Count('questions')).filter(num_questions__gt=0)


class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        quiz = kwargs.pop('quiz')
        super().__init__(*args, **kwargs)
        for question in quiz.questions.all():
            if question.question_type == 'MCQ':
                choices = [(answer.id, answer.text) for answer in question.answers.all()]
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    widget=forms.RadioSelect,
                    required=True
                )
            elif question.question_type == 'TEXT':
                self.fields[f'question_{question.id}'] = forms.CharField(
                    label=question.text,
                    widget=forms.TextInput(attrs={'class': 'border p-2 w-full'}),
                    required=True
                )


class QuizDetail(LoginRequiredMixin, FormView):
    template_name = "quiz_details.html"
    form_class = QuizForm
    login_url = "/login/"

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, pk=kwargs['pk'])

        if UserSubmission.objects.filter(quiz=self.quiz, user_name=request.user).exists():
            messages.warning(request, "You have already completed this quiz.")
            return redirect("quiz_list")

        if not self.quiz.questions.exists():
            messages.error(request, "This quiz has no questions available.")
            return redirect("quiz_list")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['quiz'] = self.quiz
        return kwargs

    def form_valid(self, form):
        user = self.request.user

        if UserSubmission.objects.filter(quiz=self.quiz, user_name=user).exists():
            messages.warning(self.request, "You have already completed this quiz.")
            return redirect("quiz_list")

        if not self.quiz.questions.exists():
            messages.error(self.request, "This quiz has no questions available.")
            return redirect("quiz_list")

        submission = UserSubmission.objects.create(
            quiz=self.quiz,
            user_name=user,
            score=0
        )
        score = 0

        for question in self.quiz.questions.all():
            field = f"question_{question.id}"
            user_value = form.cleaned_data.get(field)

            if question.question_type == "MCQ":
                if user_value is None:
                    messages.error(self.request, f"Please answer question: {question.text[:50]}...")
                    submission.delete()
                    return redirect("quiz_detail", pk=self.quiz.id)

                user_value = str(user_value).strip() if user_value else ""

                if user_value == '':
                    messages.error(self.request, f"Please answer question: {question.text[:50]}...")
                    submission.delete()
                    return redirect("quiz_detail", pk=self.quiz.id)

                try:
                    answer_id = int(user_value)
                except (ValueError, TypeError):
                    messages.error(self.request, f"Invalid answer format for question: {question.text[:50]}. Expected a numeric answer ID.")
                    submission.delete()  # Clean up incomplete submission
                    return redirect("quiz_detail", pk=self.quiz.id)

                if answer_id <= 0:
                    messages.error(self.request, f"Answer ID must be a positive integer for question: {question.text[:50]}...")
                    submission.delete()
                    return redirect("quiz_detail", pk=self.quiz.id)

                try:
                    selected_answer = Answer.objects.get(id=answer_id)
                except Answer.DoesNotExist:
                    messages.error(self.request,
                                   f"Selected answer does not exist for question: {question.text[:50]}...")
                    submission.delete()
                    return redirect("quiz_detail", pk=self.quiz.id)

                if selected_answer.question != question:
                    messages.error(self.request, f"Invalid answer selected. Answer does not belong to question: {question.text[:50]}...")
                    submission.delete()  # Clean up incomplete submission
                    return redirect("quiz_detail", pk=self.quiz.id)

                correct = selected_answer.is_correct

                if correct:
                    score += 1
                UserAnswer.objects.create(
                    submission=submission,
                    question=question,
                    answer=selected_answer,
                    is_correct=correct,
                )
            else:
                if not user_value:
                    messages.error(self.request, f"Please provide an answer for: {question.text[:50]}...")
                    submission.delete()
                    return redirect("quiz_detail", pk=self.quiz.id)

                user_value = user_value.strip() if isinstance(user_value, str) else str(user_value)

                if user_value == '':
                    messages.error(self.request, f"Please provide an answer for: {question.text[:50]}...")
                    submission.delete()
                    return redirect("quiz_detail", pk=self.quiz.id)

                if len(user_value) > 1000:
                    messages.error(self.request, f"Text answer is too long. Maximum 1000 characters allowed for question: {question.text[:50]}...")
                    submission.delete()
                    return redirect("quiz_detail", pk=self.quiz.id)

                if len(user_value) < 1:
                    messages.error(self.request, f"Text answer cannot be empty for question: {question.text[:50]}...")
                    submission.delete()
                    return redirect("quiz_detail", pk=self.quiz.id)

                placeholder_answer = question.answers.first()

                UserAnswer.objects.create(
                    submission=submission,
                    question=question,
                    answer=placeholder_answer,
                    is_correct=False,
                )

        submission.score = score
        submission.save()
        return redirect("quiz_result", submission_id=submission.id)


@login_required(login_url='/login/')
def quiz_result(request, submission_id):
    submission = get_object_or_404(UserSubmission, id=submission_id)
    if submission.user_name != request.user:
        messages.error(request, "You do not have permission to view this quiz result.")
        return redirect("quiz_list")

    return render(request, "quiz_result.html", {"submission": submission})


def event(request):
    upcoming_event = Event.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date')

    context = {
        'events': upcoming_event
    }
    return render(request, 'event.html', context)
