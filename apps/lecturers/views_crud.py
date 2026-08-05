from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.decorators import lecturer_required
from apps.materials.models import Material
from apps.schedules.models import Schedule
from .forms import MaterialForm, ScheduleForm


# ===== MATERIAL CRUD =====

@login_required
@lecturer_required
def material_edit(request, material_id):
    """Редактирование материала"""
    material = get_object_or_404(Material, id=material_id, uploaded_by=request.user)
    
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material, lecturer=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material muvaffaqiyatli yangilandi')
            return redirect('lecturers:lecturer_materials')
    else:
        form = MaterialForm(instance=material, lecturer=request.user)
    
    return render(request, 'lecturers/material_form.html', {'form': form, 'action': 'Tahrirlash', 'material': material})


@login_required
@lecturer_required
def material_delete(request, material_id):
    """Удаление материала"""
    material = get_object_or_404(Material, id=material_id, uploaded_by=request.user)
    
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material o\'chirildi')
        return redirect('lecturers:lecturer_materials')
    
    return render(request, 'lecturers/material_confirm_delete.html', {'material': material})


# ===== SCHEDULE (только редактирование и удаление) =====

@login_required
@lecturer_required
def schedule_edit(request, schedule_id):
    """Редактирование занятия"""
    schedule = get_object_or_404(Schedule, id=schedule_id, lecturer=request.user)
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule, lecturer=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dars muvaffaqiyatli yangilandi')
            return redirect('lecturers:lecturer_schedule')
    else:
        form = ScheduleForm(instance=schedule, lecturer=request.user)
    
    return render(request, 'lecturers/schedule_form.html', {'form': form, 'action': 'Tahrirlash', 'schedule': schedule})


@login_required
@lecturer_required
def schedule_delete(request, schedule_id):
    """Удаление занятия"""
    schedule = get_object_or_404(Schedule, id=schedule_id, lecturer=request.user)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'Dars o\'chirildi')
        return redirect('lecturers:lecturer_schedule')
    
    return render(request, 'lecturers/schedule_confirm_delete.html', {'schedule': schedule})
