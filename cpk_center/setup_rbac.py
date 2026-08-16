"""
Полная настройка ролей и прав доступа (RBAC)
"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cpk_center.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from apps.certificates.models import Certificate
from apps.courses.models import Course, Enrollment
from apps.groups.models import StudentRecord
from apps.materials.models import Material
from apps.schedules.models import Attendance, Schedule
from apps.users.models import StudentProfile, User
from apps.zoom_integration.models import ZoomMeeting, ZoomRecording


def setup_roles():
    print("🔧 Начинаем настройку ролей и прав...")

    # 1. Создаем/обновляем группы
    admin_group, _ = Group.objects.get_or_create(name='Администратор')
    director_group, _ = Group.objects.get_or_create(name='Директор')
    department_head_group, _ = Group.objects.get_or_create(name='Начальник отдела')
    methodist_group, _ = Group.objects.get_or_create(name='Методист')
    lecturer_group, _ = Group.objects.get_or_create(name='Преподаватель')
    student_group, _ = Group.objects.get_or_create(name='Слушатель')

    print("✅ Группы созданы/обновлены")

    # 2. Права для АДМИНИСТРАТОРА (полный доступ)
    admin_perms = Permission.objects.all()
    admin_group.permissions.set(admin_perms)
    print(f"✅ Администратор: {admin_group.permissions.count()} прав (полный доступ)")

    # 3. Права для ДИРЕКТОРА (полный доступ, кроме управления суперпользователями)
    director_perms = Permission.objects.exclude(
        content_type__app_label='auth',
        codename__in=['change_user']
    )
    director_group.permissions.set(director_perms)
    print(f"✅ Директор: {director_group.permissions.count()} прав (без изменения пользователей)")

    # 4. Права для НАЧАЛЬНИКА ОТДЕЛА
    # Расписание, преподаватели, отчетность, посещаемость
    schedule_ct = ContentType.objects.get_for_model(Schedule)
    attendance_ct = ContentType.objects.get_for_model(Attendance)
    user_ct = ContentType.objects.get_for_model(User)

    department_head_perms = Permission.objects.filter(
        content_type__in=[schedule_ct, attendance_ct, user_ct],
        codename__in=[
            'add_schedule', 'change_schedule', 'view_schedule',
            'add_attendance', 'change_attendance', 'view_attendance',
            'view_user',
        ]
    )
    department_head_group.permissions.set(department_head_perms)
    print(f"✅ Начальник отдела: {department_head_group.permissions.count()} прав")

    # 5. Права для МЕТОДИСТА
    # Регистрация слушателей, запись на курсы, учет
    student_ct = ContentType.objects.get_for_model(StudentRecord)
    course_ct = ContentType.objects.get_for_model(Course)
    enrollment_ct = ContentType.objects.get_for_model(Enrollment)
    student_profile_ct = ContentType.objects.get_for_model(StudentProfile)

    methodist_perms = Permission.objects.filter(
        content_type__in=[student_ct, course_ct, enrollment_ct, student_profile_ct],
        codename__in=[
            'add_studentrecord', 'change_studentrecord', 'view_studentrecord',
            'view_course', 'add_enrollment', 'change_enrollment', 'view_enrollment',
            'add_studentprofile', 'change_studentprofile', 'view_studentprofile', 'delete_studentprofile',
        ]
    )
    methodist_group.permissions.set(methodist_perms)
    print(f"✅ Методист: {methodist_group.permissions.count()} прав")

    # 6. Права для ПРЕПОДАВАТЕЛЯ
    # Группы по расписанию, онлайн-занятия, оценивание, тесты, материалы
    material_ct = ContentType.objects.get_for_model(Material)
    zoom_ct = ContentType.objects.get_for_model(ZoomMeeting)
    zoom_rec_ct = ContentType.objects.get_for_model(ZoomRecording)

    lecturer_perms = Permission.objects.filter(
        content_type__in=[material_ct, zoom_ct, zoom_rec_ct, schedule_ct, attendance_ct],
        codename__in=[
            'add_material', 'change_material', 'view_material', 'delete_material',
            'add_zoommeeting', 'change_zoommeeting', 'view_zoommeeting',
            'view_zoomrecording',
            'view_schedule', 'view_attendance',
        ]
    )
    lecturer_group.permissions.set(lecturer_perms)
    print(f"✅ Преподаватель: {lecturer_group.permissions.count()} прав")

    # 7. Права для СЛУШАТЕЛЯ (студента)
    # Только просмотр своих сертификатов, материалов и записей
    cert_ct = ContentType.objects.get_for_model(Certificate)

    student_perms = Permission.objects.filter(
        content_type__in=[cert_ct, material_ct, zoom_rec_ct],
        codename__in=['view_certificate', 'view_material', 'view_zoomrecording']
    )
    student_group.permissions.set(student_perms)
    print(f"✅ Слушатель: {student_group.permissions.count()} прав")

    print("\n🎉 Настройка ролей завершена!")

def sync_users_with_groups():
    """Синхронизация пользователей с группами на основе их ролей"""
    print("\n🔄 Синхронизация пользователей с группами...")

    role_to_group = {
        'admin': 'Администратор',
        'director': 'Директор',
        'department_head': 'Начальник отдела',
        'methodist': 'Методист',
        'lecturer': 'Преподаватель',
        'student': 'Слушатель',
    }

    for user in User.objects.all():
        if user.role in role_to_group:
            group_name = role_to_group[user.role]
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
                print(f"  ✅ {user.username} → {group_name}")
            except Group.DoesNotExist:
                print(f"  ⚠️ Группа {group_name} не найдена")

    print("✅ Синхронизация завершена")

def create_test_users():
    """Создание тестовых пользователей для каждой роли"""
    print("\n👥 Создание тестовых пользователей...")

    test_users = [
        {
            'username': 'director_test',
            'password': 'director123',
            'email': 'director@test.uz',
            'role': 'director',
            'is_staff': True,
            'is_superuser': True,
            'full_name': 'Тестовый Директор'
        },
        {
            'username': 'dept_head_test',
            'password': 'dept123',
            'email': 'dept@test.uz',
            'role': 'department_head',
            'is_staff': True,
            'is_superuser': False,
            'full_name': 'Тестовый Начальник отдела'
        },
        {
            'username': 'methodist_test',
            'password': 'methodist123',
            'email': 'methodist@test.uz',
            'role': 'methodist',
            'is_staff': True,
            'is_superuser': False,
            'full_name': 'Тестовый Методист'
        },
        {
            'username': 'lecturer_test',
            'password': 'lecturer123',
            'email': 'lecturer@test.uz',
            'role': 'lecturer',
            'is_staff': True,
            'is_superuser': False,
            'full_name': 'Тестовый Преподаватель'
        },
    ]

    role_to_group = {
        'director': 'Директор',
        'department_head': 'Начальник отдела',
        'methodist': 'Методист',
        'lecturer': 'Преподаватель',
    }

    for user_data in test_users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'role': user_data['role'],
                'is_staff': user_data['is_staff'],
                'is_superuser': user_data['is_superuser'],
                'full_name': user_data['full_name'],
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()

            group_name = role_to_group.get(user_data['role'])
            if group_name:
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    pass

            print(f"  ✅ Создан: {user.username} ({user.role}) - пароль: {user_data['password']}")
        else:
            print(f"  ℹ️ Уже существует: {user.username}")

    print("✅ Тестовые пользователи созданы")

if __name__ == '__main__':
    setup_roles()
    sync_users_with_groups()
    create_test_users()
    print("\n🎊 Все готово!")
