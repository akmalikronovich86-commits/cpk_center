from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.decorators import lecturer_required
from apps.zoom_integration.models import ZoomMeeting, ZoomRecording
from apps.schedules.models import Schedule
from apps.courses.models import Course
from .forms import ZoomMeetingForm
from django.utils import timezone


# ===== ZOOM MEETING CRUD =====

@login_required
@lecturer_required
def zoom_meeting_create(request):
    """Создание новой Zoom встречи"""
    if request.method == 'POST':
        form = ZoomMeetingForm(request.POST, lecturer=request.user)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.teacher = request.user
            
            # Устанавливаем тему по умолчанию
            if not meeting.topic:
                if meeting.schedule:
                    meeting.topic = f"{meeting.schedule.course.title} - {meeting.schedule.topic.title if meeting.schedule.topic else 'Dars'}"
                elif meeting.course:
                    meeting.topic = meeting.course.title
            
            meeting.save()
            messages.success(request, f'Zoom uchrashuv muvaffaqiyatli yaratildi: {meeting.topic}')
            return redirect('lecturers:lecturer_zoom')
    else:
        form = ZoomMeetingForm(lecturer=request.user)
    
    return render(request, 'lecturers/zoom_meeting_form.html', {'form': form, 'action': 'Yaratish'})


@login_required
@lecturer_required
def zoom_meeting_edit(request, meeting_id):
    """Редактирование Zoom встречи"""
    meeting = get_object_or_404(ZoomMeeting, id=meeting_id, teacher=request.user)
    
    if request.method == 'POST':
        form = ZoomMeetingForm(request.POST, instance=meeting, lecturer=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Zoom uchrashuv muvaffaqiyatli yangilandi: {meeting.topic}')
            return redirect('lecturers:lecturer_zoom')
    else:
        form = ZoomMeetingForm(instance=meeting, lecturer=request.user)
    
    return render(request, 'lecturers/zoom_meeting_form.html', {'form': form, 'action': 'Tahrirlash', 'meeting': meeting})


@login_required
@lecturer_required
def zoom_meeting_delete(request, meeting_id):
    """Удаление Zoom встречи"""
    meeting = get_object_or_404(ZoomMeeting, id=meeting_id, teacher=request.user)
    
    if request.method == 'POST':
        meeting.delete()
        messages.success(request, 'Zoom uchrashuv o\'chirildi')
        return redirect('lecturers:lecturer_zoom')
    
    return render(request, 'lecturers/zoom_meeting_confirm_delete.html', {'meeting': meeting})


@login_required
@lecturer_required
def zoom_meeting_start(request, meeting_id):
    """Начать встречу (получение URL)"""
    meeting = get_object_or_404(ZoomMeeting, id=meeting_id, teacher=request.user)
    
    # TODO: Интеграция с Zoom API для получения URL
    # Пока просто перенаправляем на join_url если он есть
    if meeting.zoom_join_url:
        return redirect(meeting.zoom_join_url)
    else:
        messages.warning(request, 'Zoom URL hali mavjud emas')
        return redirect('lecturers:lecturer_zoom')


@login_required
@lecturer_required
def zoom_recordings(request):
    """Просмотр записей Zoom встреч (только просмотр)"""
    # Получаем все записи встреч этого лектора
    recordings = ZoomRecording.objects.filter(
        meeting__teacher=request.user
    ).select_related('meeting', 'meeting__course').order_by('-created_at')
    
    context = {
        'recordings': recordings,
        'total_recordings': recordings.count(),
    }
    
    return render(request, 'lecturers/zoom_recordings.html', context)
