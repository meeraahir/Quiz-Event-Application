from django.urls import path

from .views import *

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
