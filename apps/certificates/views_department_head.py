from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.users.models import User
from apps.schedules.models import Schedule
from apps.courses.models import Course, AcademicGroup, Enrollment
from .forms import QuickScheduleForm, AcademicGroupForm, AssignLecturerForm


@login_required
def schedule_create(request):
    """Быстрое создание расписания"""
    if request.method == 'POST':
        form = QuickScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.created_by = request.user
            if schedule.status == 'published':
                schedule.published_by = request.user
                schedule.published_at = timezone.now()
            schedule.save()
            messages.success(request, f'Dars jadvali muvaffaqiyatli yaratildi: {schedule.course.title}')
            return redirect('kpi:department_head_kpi_dashboard')
    else:
        form = QuickScheduleForm()
    
    return render(request, 'certificates/schedule_form.html', {'form': form, 'action': 'Yaratish'})


@login_required
def schedule_edit(request, schedule_id):
    """Редактирование расписания"""
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        form = QuickScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            schedule = form.save(commit=False)
            if schedule.status == 'published' and not schedule.published_at:
                schedule.published_by = request.user
                schedule.published_at = timezone.now()
            schedule.save()
            messages.success(request, f'Dars jadvali muvaffaqiyatli yangilandi')
            return redirect('kpi:department_head_kpi_dashboard')
    else:
        form = QuickScheduleForm(instance=schedule)
    
    return render(request, 'certificates/schedule_form.html', {'form': form, 'action': 'Tahrirlash', 'schedule': schedule})


@login_required
def schedule_delete(request, schedule_id):
    """Удаление расписания"""
    schedule = get_object_or_404(Schedule, id=schedule_id)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Dars jadvali o\'chirildi')
        return redirect('kpi:department_head_kpi_dashboard')
    
    return render(request, 'certificates/schedule_confirm_delete.html', {'schedule': schedule})


@login_required
def group_create(request):
    """Создание учебной группы"""
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'O\'quv guruhi muvaffaqiyatli yaratildi: {group.name}')
            return redirect('kpi:department_head_kpi_dashboard')
    else:
        form = AcademicGroupForm()
    
    return render(request, 'certificates/group_form.html', {'form': form, 'action': 'Yaratish'})


@login_required
def group_edit(request, group_id):
    """Редактирование учебной группы"""
    group = get_object_or_404(AcademicGroup, id=group_id)
    
    if request.method == 'POST':
        form = AcademicGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f'O\'quv guruhi muvaffaqiyatli yangilandi')
            return redirect('kpi:department_head_kpi_dashboard')
    else:
        form = AcademicGroupForm(instance=group)
    
    return render(request, 'certificates/group_form.html', {'form': form, 'action': 'Tahrirlash', 'group': group})


@login_required
def group_delete(request, group_id):
    """Удаление учебной группы"""
    group = get_object_or_404(AcademicGroup, id=group_id)
    
    if request.method == 'POST':
        group.delete()
        messages.success(request, 'O\'quv guruhi o\'chirildi')
        return redirect('kpi:department_head_kpi_dashboard')
    
    return render(request, 'certificates/group_confirm_delete.html', {'group': group})


@login_required
def assign_lecturer(request):
    """Назначение лектора на курс"""
    if request.method == 'POST':
        form = AssignLecturerForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            lecturer = form.cleaned_data['lecturer']
            course.lecturer = lecturer
            course.save()
            messages.success(request, f'{lecturer.get_full_name()} {course.title} kursiga o\'qituvchi etib tayinlandi')
            return redirect('kpi:department_head_kpi_dashboard')
    else:
        form = AssignLecturerForm()
    
    return render(request, 'certificates/assign_lecturer_form.html', {'form': form})
