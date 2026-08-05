from django import forms
from .models import KPIReport, KPIValue, IjroTask
from datetime import date

class KPIReportForm(forms.ModelForm):
    class Meta:
        model = KPIReport
        fields = ['period_start', 'period_end']
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            today = date.today()
            self.fields['period_start'].initial = today.replace(day=1)
            self.fields['period_end'].initial = today

class KPIValueForm(forms.ModelForm):
    class Meta:
        model = KPIValue
        fields = ['actual_value', 'evidence', 'attachment']
        widgets = {
            'actual_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'evidence': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

class IjroTaskForm(forms.ModelForm):
    class Meta:
        model = IjroTask
        fields = ['task_number', 'title', 'description', 'assigned_by', 'deadline', 'status', 'result', 'incoming_file', 'completed_file']
        widgets = {
            'task_number': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_by': forms.TextInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'result': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'incoming_file': forms.FileInput(attrs={'class': 'form-control-file', 'id': 'id_incoming_file'}),
            'completed_file': forms.FileInput(attrs={'class': 'form-control-file', 'id': 'id_completed_file'}),
        }


# ============ ФОРМЫ ДЛЯ УПРАВЛЕНИЯ (Bo'lim boshlig'i) ============

from apps.schedules.models import Schedule, Attendance
from apps.courses.models import Course, AcademicGroup, Topic, Enrollment
from apps.groups.models import StudentRecord, TrainingYear
from apps.users.models import LecturerProfile


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['group', 'course', 'lecturer', 'topic', 'date_start', 'date_end', 'room', 'status', 'notes']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'lecturer': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'date_start': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_end': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masalan: 201-xona'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'code', 'description', 'duration_hours', 'lecturer', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masalan: KRS-001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'lecturer': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AcademicGroupForm(forms.ModelForm):
    class Meta:
        model = AcademicGroup
        fields = ['name', 'course', 'start_date', 'end_date', 'max_students']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['course', 'title', 'description', 'order', 'duration_hours']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class StudentRecordForm(forms.ModelForm):
    class Meta:
        model = StudentRecord
        fields = ['full_name', 'position', 'passport', 'birth_date', 'group', 'branch', 'phone', 'email', 'training_year']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'passport': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.TextInput(attrs={'class': 'form-control'}),
            'group': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'training_year': forms.Select(attrs={'class': 'form-control'}),
        }


class LecturerProfileForm(forms.ModelForm):
    class Meta:
        model = LecturerProfile
        fields = ['user', 'specialization', 'experience_years']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }
