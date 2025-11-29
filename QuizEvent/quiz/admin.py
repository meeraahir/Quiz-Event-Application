from django.contrib import admin
from .models import Quiz, Question, Answer, UserSubmission, UserAnswer, Event

# Register your models here.

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(UserSubmission)
admin.site.register(UserAnswer)
admin.site.register(Event)
