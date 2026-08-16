from django import forms

from apps.courses.models import AcademicGroup, Course, Topic
from apps.materials.models import Material
from apps.schedules.models import Schedule


class MaterialForm(forms.ModelForm):
    """Форма для загрузки/редактирования материала"""
    class Meta:
        model = Material
        fields = ['title', 'description', 'type', 'course', 'file', 'is_published', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Material nomi'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tavsif'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tartib'}),
        }

    def __init__(self, *args, **kwargs):
        self.lecturer = kwargs.pop('lecturer', None)
        super().__init__(*args, **kwargs)

        if self.lecturer:
            self.fields['course'].queryset = Course.objects.filter(lecturer=self.lecturer)


class ScheduleForm(forms.ModelForm):
    """Форма для редактирования расписания"""
    class Meta:
        model = Schedule
        fields = ['group', 'course', 'topic', 'date_start', 'date_end', 'room', 'status']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'date_start': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_end': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'room': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auditoriya'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.lecturer = kwargs.pop('lecturer', None)
        super().__init__(*args, **kwargs)

        if self.lecturer:
            self.fields['course'].queryset = Course.objects.filter(lecturer=self.lecturer)
            self.fields['group'].queryset = AcademicGroup.objects.filter(course__lecturer=self.lecturer)
            self.fields['topic'].queryset = Topic.objects.filter(course__lecturer=self.lecturer)
