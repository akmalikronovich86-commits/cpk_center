from django import forms
from .models import StudyProgram


class CustomClearableFileInput(forms.ClearableFileInput):
    """Кастомный виджет для загрузки файла"""
    template_name = 'admin/widgets/custom_file_input.html'


class StudyProgramForm(forms.ModelForm):
    """Форма для учебной программы с улучшенным виджетом файла"""
    class Meta:
        model = StudyProgram
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Применяем кастомный виджет для поля файла
        if 'file' in self.fields:
            self.fields['file'].widget = CustomClearableFileInput(attrs={
                'class': 'custom-file-input',
            })
