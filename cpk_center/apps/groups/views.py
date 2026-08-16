from django.db.models import Count
from django.shortcuts import render

from .models import StudentRecord, TrainingYear


def student_statistics(request):
    """Статистика обучившихся по годам и должностям"""
    # Получаем все доступные годы
    years = TrainingYear.objects.values_list('name', flat=True).distinct().order_by('-name')

    # Получаем выбранный год из GET параметров
    selected_year = request.GET.get('year', '')

    # Фильтруем записи по году
    if selected_year:
        queryset = StudentRecord.objects.filter(training_year__name=selected_year)
    else:
        queryset = StudentRecord.objects.all()

    # Общее количество слушателей (после фильтрации)
    total_students = queryset.count()

    # Статистика по должностям (после фильтрации)
    positions_data = (
        queryset
        .values('position')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Добавляем процентное соотношение
    positions = []
    for item in positions_data:
        if item['position']:
            percentage = round((item['count'] / total_students * 100), 1) if total_students > 0 else 0
            positions.append({
                'lavozim': item['position'],
                'count': item['count'],
                'percentage': percentage,
            })

    # Получаем список слушателей С ГОДОМ ОБУЧЕНИЯ (после фильтрации!)
    students = (
        queryset
        .select_related('training_year')
        .values('full_name', 'position', 'group', 'training_year__name', 'branch', 'district_power')
        .order_by('full_name')
    )

    # Преобразуем в список словарей для удобства
    students_list = []
    for s in students:
        students_list.append({
            'full_name': s['full_name'] or '—',
            'position': s['position'] or '—',
            'group': s['group'] or '—',
            'training_year': s['training_year__name'] or '—',
            'branch': s['branch'] or '—',
        })

    context = {
        'years': years,
        'selected_year': selected_year,
        'total_students': total_students,
        'positions': positions,
        'students': students_list,
        'title': 'Ma\'lumotlar bazasi statistikasi',
    }

    return render(request, 'admin/groups/statistics/student_stats.html', context)
