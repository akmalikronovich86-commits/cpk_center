from django.contrib import admin

from .models import ExamQuestion, ExamResult, TestSession

admin.site.register(ExamQuestion)
admin.site.register(ExamResult)
admin.site.register(TestSession)
