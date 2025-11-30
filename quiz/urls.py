from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .api import (
    QuizViewSet, EventViewSet, UserSubmissionViewSet, UserAnswerViewSet, 
    QuizSubmissionApi, RegisterViewSet, QuizCreateApi, QuestionCreateApi, 
    AnswerCreateApi, EventCreateApi
)

urlpatterns = [
    path('', index, name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('quiz_list/', QuizList.as_view(), name='quiz_list'),
    path('quiz/<int:pk>/', QuizDetail.as_view(), name='quiz_detail'),
    path('result/<int:submission_id>/', quiz_result, name='quiz_result'),
    path('events/', event, name='events'),
]

router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='api-register'),
router.register(r'quizzes', QuizViewSet, basename='api-quiz')
router.register(r'events', EventViewSet, basename='api-event')
router.register(r'submissions', UserSubmissionViewSet, basename='api-submission')
router.register(r'user-answers', UserAnswerViewSet, basename='api-useranswer')

api_urlpatterns = [
    path('quiz/submit/', QuizSubmissionApi.as_view(), name='api-quiz-submit'),
    path('quiz/create/', QuizCreateApi.as_view(), name='api-quiz-create'),
    path('question/create/', QuestionCreateApi.as_view(), name='api-question-create'),
    path('answer/create/', AnswerCreateApi.as_view(), name='api-answer-create'),
    path('event/create/', EventCreateApi.as_view(), name='api-event-create'),
    path('', include(router.urls)),
]

urlpatterns += [
    path('api/', include((api_urlpatterns, 'quiz'), namespace='api')),
]
