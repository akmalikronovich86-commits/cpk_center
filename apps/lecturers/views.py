from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
from apps.users.decorators import lecturer_required
from apps.courses.models import Course, AcademicGroup
from apps.schedules.models import Schedule, Attendance
from apps.groups.models import StudentRecord
from apps.materials.models import Material
from apps.users.models import User
import os


# ===== НАВИГАЦИЯ =====
PAGES_ORDER = [
    ('lecturers:lecturer_dashboard', 'Bosh sahifa', '🏠'),
    ('lecturers:lecturer_schedule', 'Dars jadvali', '📅'),
    ('lecturers:lecturer_courses', 'Kurslar', ''),
    ('lecturers:lecturer_students', 'Tinglovchilar', '👥'),
    ('assessments:teacher_students', 'Attestatsiya', '✅'),
    ('lecturers:lecturer_materials', 'Materiallar', '📄'),
    ('lecturers:lecturer_zoom', 'Zoom uchrashuvlar', '📹'),
]

def get_navigation(current_page_name):
    """Возвращает prev/next для навигации"""
    for i, (url, name, icon) in enumerate(PAGES_ORDER):
        if url == current_page_name:
            prev_page = PAGES_ORDER[i-1] if i > 0 else None
            next_page = PAGES_ORDER[i+1] if i < len(PAGES_ORDER) - 1 else None
            return {
                'current_page_name': name,
                'current_icon': icon,
                'prev_page_url': prev_page[0] if prev_page else None,
                'prev_page_name': prev_page[1] if prev_page else None,
                'next_page_url': next_page[0] if next_page else None,
                'next_page_name': next_page[1] if next_page else None,
            }
    return {}

@login_required
@lecturer_required
def lecturer_dashboard(request):
    """Основной дашборд преподавателя"""
    now = timezone.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)
    
    # Начало и конец сегодняшнего дня
    today_start = timezone.make_aware(timezone.datetime(today.year, today.month, today.day, 0, 0, 0))
    today_end = timezone.make_aware(timezone.datetime(today.year, today.month, today.day, 23, 59, 59))
    
    # Начало и конец завтрашнего дня
    tomorrow_start = timezone.make_aware(timezone.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0))
    tomorrow_end = timezone.make_aware(timezone.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59))
    
    # ===== МОИ ДАННЫЕ =====
    # Мои курсы
    my_courses = Course.objects.filter(lecturer=request.user)
    total_courses = my_courses.count()
    
    # Мои группы (через курсы)
    my_groups = AcademicGroup.objects.filter(course__lecturer=request.user)
    total_groups = my_groups.count()
    
    # Мои студенты (через группы - по названию группы)
    my_group_names = my_groups.values_list('name', flat=True)
    my_students = StudentRecord.objects.filter(group__in=my_group_names)
    total_students = my_students.count()
    
    # Моё расписание - сегодня
    today_schedules = Schedule.objects.filter(
        lecturer=request.user,
        date_start__gte=today_start,
        date_start__lte=today_end
    ).order_by('date_start')[:5]
    
    # Моё расписание - завтра
    tomorrow_schedules = Schedule.objects.filter(
        lecturer=request.user,
        date_start__gte=tomorrow_start,
        date_start__lte=tomorrow_end
    ).order_by('date_start')[:5]
    
    # Всего расписаний
    total_schedules = Schedule.objects.filter(lecturer=request.user).count()
    
    # Мои материалы
    my_materials = Material.objects.filter(uploaded_by=request.user)
    total_materials = my_materials.count()
    
    # ===== БЛИЖАЙШИЕ ЗАНЯТИЯ =====
    upcoming_schedules = Schedule.objects.filter(
        lecturer=request.user,
        date_start__gte=now
    ).order_by('date_start')[:10]
    
    context = {
        'today': today,
        'now': now,
        'my_courses': my_courses,
        'total_courses': total_courses,
        'my_groups': my_groups,
        'total_groups': total_groups,
        'total_students': total_students,
        'today_schedules': today_schedules,
        'tomorrow_schedules': tomorrow_schedules,
        'total_schedules': total_schedules,
        'my_materials': my_materials,
        'total_materials': total_materials,
        'upcoming_schedules': upcoming_schedules,
    }
    
    context.update(get_navigation('lecturers:lecturer_dashboard'))
    return render(request, 'lecturers/dashboard.html', context)

@login_required
@lecturer_required
def lecturer_schedule(request):
    """Моё расписание"""
    now = timezone.now()
    today = now.date()
    
    # Фильтры
    date_filter = request.GET.get('date')
    
    schedules = Schedule.objects.filter(lecturer=request.user).select_related(
        'course', 'group'
    ).order_by('date_start')
    
    if date_filter:
        from datetime import datetime
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            day_start = timezone.make_aware(timezone.datetime(filter_date.year, filter_date.month, filter_date.day, 0, 0, 0))
            day_end = timezone.make_aware(timezone.datetime(filter_date.year, filter_date.month, filter_date.day, 23, 59, 59))
            schedules = schedules.filter(date_start__gte=day_start, date_start__lte=day_end)
        except ValueError:
            pass
    
    context = {
        'schedules': schedules,
        'today': today,
    }
    
    context.update(get_navigation('lecturers:lecturer_schedule'))
    return render(request, 'lecturers/schedule.html', context)

@login_required
@lecturer_required
def lecturer_courses(request):
    """Мои курсы"""
    courses = Course.objects.filter(lecturer=request.user)
    
    context = {
        'courses': courses,
        'total_courses': courses.count(),
    }
    
    context.update(get_navigation('lecturers:lecturer_courses'))
    return render(request, 'lecturers/courses.html', context)

@login_required
@lecturer_required
def lecturer_students(request):
    """Мои студенты (через группы моих курсов)"""
    my_groups = AcademicGroup.objects.filter(course__lecturer=request.user)
    my_group_names = my_groups.values_list('name', flat=True)
    
    students = StudentRecord.objects.filter(
        group__in=my_group_names
    ).order_by('full_name')
    
    # Фильтры
    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(full_name__icontains=search) |
            Q(xtm__icontains=search) |
            Q(phone__icontains=search)
        )
    
    context = {
        'students': students,
        'total_students': students.count(),
        'my_groups': my_groups,
    }
    
    context.update(get_navigation('lecturers:lecturer_students'))
    return render(request, 'lecturers/students.html', context)

@login_required
@lecturer_required
def lecturer_materials(request):
    """Мои учебные материалы"""
    materials = Material.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    
    context = {
        'materials': materials,
        'total_materials': materials.count(),
    }
    
    context.update(get_navigation('lecturers:lecturer_materials'))
    return render(request, 'lecturers/materials.html', context)

@login_required
@lecturer_required
def upload_material(request):
    """Загрузка нового материала преподавателем"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        material_type = request.POST.get('material_type', 'document')
        course_id = request.POST.get('course')
        
        # Получаем курс
        if course_id:
            try:
                course = Course.objects.get(id=course_id, lecturer=request.user)
            except Course.DoesNotExist:
                messages.error(request, "Kurs topilmadi yoki siz bu kursga ma'ruzachi emassiz")
                return redirect('lecturers:upload_material')
        else:
            course = None
        
        # Обрабатываем файл
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            messages.error(request, "Fayl yuklanmadi. Iltimos, faylni tanlang")
            return redirect('lecturers:upload_material')
        
        # Создаём материал
        material = Material.objects.create(
            title=title or uploaded_file.name,
            description=description,
            type=material_type,
            course=course,
            uploaded_by=request.user,
            file=uploaded_file,
            is_published=True  # Сразу публикуем
        )
        
        messages.success(request, f"Material muvaffaqiyatli yuklandi: {material.title}")
        return redirect('lecturers:lecturer_materials')
    
    # GET запрос - показываем форму
    my_courses = Course.objects.filter(lecturer=request.user)
    
    context = {
        'my_courses': my_courses,
    }
    
    return render(request, 'lecturers/upload_material.html', context)



@login_required
@lecturer_required
def lecturer_attendance(request):
    """Просмотр посещаемости (только просмотр)"""
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    
    # Мои занятия за последние 30 дней
    my_schedules = Schedule.objects.filter(
        lecturer=request.user,
        date_start__gte=last_30_days
    ).select_related('course', 'group').order_by('-date_start')
    
    # Статистика посещаемости
    attendance_stats = []
    for schedule in my_schedules:
        attendances = Attendance.objects.filter(schedule=schedule)
        total = attendances.count()
        present = attendances.filter(status='present').count()
        absent = attendances.filter(status='absent').count()
        late = attendances.filter(status='late').count()
        
        attendance_stats.append({
            'schedule': schedule,
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'attendance_rate': (present / total * 100) if total > 0 else 0
        })
    
    context = {
        'attendance_stats': attendance_stats,
        'total_schedules': my_schedules.count(),
    }
    
    return render(request, 'lecturers/attendance.html', context)


@login_required
@lecturer_required
def lecturer_attendance_detail(request, schedule_id):
    """Детальная посещаемость конкретного занятия"""
    schedule = get_object_or_404(Schedule, id=schedule_id, lecturer=request.user)
    attendances = Attendance.objects.filter(schedule=schedule).select_related('student')
    
    context = {
        'schedule': schedule,
        'attendances': attendances,
    }
    
    return render(request, 'lecturers/attendance_detail.html', context)

@login_required
@lecturer_required
def lecturer_zoom(request):
    """Мои Zoom встречи"""
    try:
        from apps.zoom_integration.models import ZoomMeeting
        
        meetings = ZoomMeeting.objects.filter(
            teacher=request.user
        ).order_by('-start_time')
    except ImportError:
        meetings = []
    
    context = {
        'meetings': meetings,
        'total_meetings': meetings.count() if hasattr(meetings, 'count') else 0,
    }
    
    context.update(get_navigation('lecturers:lecturer_zoom'))
    return render(request, 'lecturers/zoom.html', context)
