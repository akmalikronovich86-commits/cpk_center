from django.contrib import admin
from apps.core.admin_actions import MassActionsMixin
from .models import Course, AcademicGroup, Enrollment, Topic


@admin.register(Course)
class CourseAdmin(MassActionsMixin, admin.ModelAdmin):
    list_display = ('title', 'code', 'duration_hours', 'lecturer', 'is_active', 'created_at')
    list_filter = ('is_active', 'lecturer')
    search_fields = ('title', 'code')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'code', 'description', 'duration_hours')
        }),
        ('Mas\'ul shaxslar', {
            'fields': ('lecturer', 'is_active')
        }),
        ('Tizim ma\'lumotlari', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Topic)
class TopicAdmin(MassActionsMixin, admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')


@admin.register(AcademicGroup)
class AcademicGroupAdmin(MassActionsMixin, admin.ModelAdmin):
    list_display = ('name', 'course')
    list_filter = ('course',)
    search_fields = ('name', 'course__title')


@admin.register(Enrollment)
class EnrollmentAdmin(MassActionsMixin, admin.ModelAdmin):
    list_display = ('student', 'group', 'course_title', 'enrolled_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('student__full_name', 'student__username', 'group__course__title')
    list_select_related = ('student', 'group', 'group__course')

    def course_title(self, obj):
        if obj.group and obj.group.course:
            return obj.group.course.title
        return '-'
    course_title.short_description = 'Kurs'
