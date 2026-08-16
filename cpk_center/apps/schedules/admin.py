from django.contrib import admin

from .models import Attendance, Schedule

admin.site.register(Schedule)
admin.site.register(Attendance)
