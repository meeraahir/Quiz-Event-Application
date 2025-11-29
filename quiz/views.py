from django.contrib.auth import authenticate, login, logout
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
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                form.add_error(None, "User already exists with this username or email.")
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
        return Quiz.objects.annotate(num_questions=Count('questions'))


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

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['quiz'] = self.quiz
        return kwargs

    def form_valid(self, form):
        user = self.request.user
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
                selected_answer = Answer.objects.get(id=int(user_value))
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
                UserAnswer.objects.create(
                    submission=submission,
                    question=question,
                    answer=None,
                    is_correct=False,
                )

        submission.score = score
        submission.save()
        return redirect("quiz_result", submission_id=submission.id)


def quiz_result(request, submission_id):
    submission = get_object_or_404(UserSubmission, id=submission_id)
    return render(request, "quiz_result.html", {"submission": submission})


def event(request):
    upcoming_event = Event.objects.filter(
        date__gte=timezone.now().date()
    ).order_by('date')

    context = {
        'events': upcoming_event
    }
    return render(request, 'event.html', context)