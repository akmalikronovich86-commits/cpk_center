"""
Davomat QR-kod ko'rinishlari
"""
import base64
import io

import qrcode
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.schedules.models import Schedule
from .models import AttendanceToken


@login_required
def generate_qr(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    user = request.user
    lecturer = getattr(schedule, 'lecturer', None)
    is_lecturer = lecturer and getattr(lecturer, 'user_id', None) == user.id
    staff_roles = ('admin', 'director', 'methodist', 'department_head')
    if not (is_lecturer or user.is_staff or user.is_superuser or user.role in staff_roles):
        raise PermissionDenied("Siz bu darsga ruxsatga ega emassiz")

    active_token = AttendanceToken.objects.filter(
        schedule=schedule, is_used=False, expires_at__gt=timezone.now()
    ).order_by('-created_at').first()
    if not active_token:
        active_token = AttendanceToken.objects.create(schedule=schedule)

    scan_url = request.build_absolute_uri(f'/attendance/scan/?token={active_token.token}')

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(scan_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    minutes_left = int((active_token.expires_at - timezone.now()).total_seconds() // 60)

    return render(request, 'attendance/qr_page.html', {
        'schedule': schedule, 'qr_b64': qr_b64,
        'token': active_token, 'minutes_left': minutes_left, 'scan_url': scan_url,
    })


def scan_attendance(request):
    token_str = request.GET.get('token')
    if not token_str:
        return render(request, 'attendance/scan_result.html', {
            'status': 'error', 'message': "QR-kod noto'g'ri. Token topilmadi."})

    try:
        token = AttendanceToken.objects.get(token=token_str)
    except (AttendanceToken.DoesNotExist, Exception):
        return render(request, 'attendance/scan_result.html', {
            'status': 'error', 'message': "QR-kod haqiqiy emas."})

    if not request.user.is_authenticated:
        return redirect(f"/login/?next={request.get_full_path()}")

    user = request.user
    lecturer = getattr(token.schedule, 'lecturer', None)
    is_lecturer = lecturer and getattr(lecturer, 'user_id', None) == user.id
    if not (is_lecturer or user.is_staff or user.is_superuser):
        return render(request, 'attendance/scan_result.html', {
            'status': 'error',
            'message': "Siz bu dars o'qituvchisi emassiz. Davomatni boshlay olmaysiz."})

    if token.is_used:
        return render(request, 'attendance/scan_result.html', {
            'status': 'warning',
            'message': f"Bu dars allaqachon boshlangan ({token.used_at.strftime('%H:%M %d.%m.%Y')}).",
            'token': token})

    if not token.is_active():
        return render(request, 'attendance/scan_result.html', {
            'status': 'error', 'message': "QR-kod muddati o'tgan. Yangi QR-kod yarating."})

    if request.method == 'POST':
        token.use(user)
        schedule = token.schedule
        if hasattr(schedule, 'status'):
            schedule.status = 'in_progress'
            schedule.save(update_fields=['status'])
        return render(request, 'attendance/scan_result.html', {
            'status': 'success',
            'message': "Dars muvaffaqiyatli boshlandi! Davomat qayd etildi.",
            'token': token, 'schedule': schedule})

    return render(request, 'attendance/scan_confirm.html', {
        'token': token, 'schedule': token.schedule})
