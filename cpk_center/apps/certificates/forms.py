from django import forms

from apps.courses.models import AcademicGroup, Course
from apps.schedules.models import Schedule
from apps.users.models import User


class QuickScheduleForm(forms.ModelForm):
    """Форма для быстрого создания расписания"""
    class Meta:
        model = Schedule
        fields = ['group', 'course', 'lecturer', 'topic', 'date_start', 'date_end', 'room', 'status']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'course': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'lecturer': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'date_start': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'date_end': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masalan: 201-xona'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только активных лекторов
        self.fields['lecturer'].queryset = User.objects.filter(role='lecturer', is_active=True)
        # Фильтруем только активные курсы
        self.fields['course'].queryset = Course.objects.filter(is_active=True)
        # Фильтруем только активные группы
        self.fields['group'].queryset = AcademicGroup.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        date_start = cleaned_data.get('date_start')
        date_end = cleaned_data.get('date_end')

        if date_start and date_end:
            if date_end <= date_start:
                raise forms.ValidationError('Tugash vaqti boshlanish vaqtidan keyin bo\'lishi kerak')

        return cleaned_data


class AcademicGroupForm(forms.ModelForm):
    """Форма для создания/редактирования учебной группы"""
    class Meta:
        model = AcademicGroup
        fields = ['name', 'course', 'start_date', 'end_date', 'max_students']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masalan: Python-2024-01'}),
            'course': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError('Tugash sanasi boshlanish sanasidan keyin bo\'lishi kerak')

        return cleaned_data


class AssignLecturerForm(forms.Form):
    """Форма для назначения лектора на курс"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Kurs'
    )
    lecturer = forms.ModelChoiceField(
        queryset=User.objects.filter(role='lecturer', is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='O\'qituvchi'
    )

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        lecturer = cleaned_data.get('lecturer')

        # Проверяем, не назначен ли уже лектор на этот курс
        if course and lecturer:
            if course.lecturer == lecturer:
                raise forms.ValidationError('Bu o\'qituvchi allaqachon shu kursga tayinlangan')

        return cleaned_data
