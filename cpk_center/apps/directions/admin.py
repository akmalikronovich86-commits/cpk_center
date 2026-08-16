from django.contrib import admin
from django.db.models import Sum
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX

from apps.users.models import Module

from .forms import CustomClearableFileInput, StudyProgramForm
from .models import Direction, StudyProgram
from .resources import ModuleResource


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    change_list_template = 'admin/directions/change_list.html'
    list_display = ("direction_name_link", "code_badge", "is_active_badge")
    search_fields = ("name", "code")
    ordering = ("name",)
    list_filter = ("is_active",)

    def direction_name_link(self, obj):
        """Кликабельное название направления"""
        from django.urls import reverse
        url = reverse('admin:directions_direction_change', args=[obj.pk])
        return mark_safe('<a href="' + url + '" style="color:#417690; font-weight:500; text-decoration:none;">' + obj.name + '</a>')
    direction_name_link.short_description = "Yo'nalish nomi"
    direction_name_link.allow_tags = True

    def code_badge(self, obj):
        """Бейдж с кодом"""
        return mark_safe('<span style="background:#e8f0f5; color:#417690; padding:4px 10px; border-radius:3px; font-size:11px; font-weight:bold;">' + obj.code + '</span>')
    code_badge.short_description = "Kodi"
    code_badge.allow_tags = True

    def is_active_badge(self, obj):
        """Бейдж статуса"""
        if obj.is_active:
            return mark_safe('<span style="background:#28a745; color:white; padding:4px 10px; border-radius:3px; font-size:11px; font-weight:bold;">Faol</span>')
        else:
            return mark_safe('<span style="background:#dc3545; color:white; padding:4px 10px; border-radius:3px; font-size:11px; font-weight:bold;">Nofaol</span>')
    is_active_badge.short_description = "Holati"
    is_active_badge.allow_tags = True



@admin.register(StudyProgram)
class StudyProgramAdmin(admin.ModelAdmin):
    form = StudyProgramForm
    change_list_template = 'admin/directions/studyprogram/change_list.html'
    list_display = ("short_name", "direction_badge", "academic_year_badge", "file_icon", "created_at_short")

    def formfield_for_dbfield(self, db_field, **kwargs):
        """Принудительно применяем кастомный виджет для поля file"""
        if db_field.name == 'file':
            kwargs['widget'] = CustomClearableFileInput
        return super().formfield_for_dbfield(db_field, **kwargs)

    search_fields = ("name", "direction__name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    list_filter = ("direction", "academic_year")

    def short_name(self, obj):
        """Кликабельное название программы"""
        if obj.name:
            from django.urls import reverse
            url = reverse('admin:directions_studyprogram_change', args=[obj.pk])
            return mark_safe('<a href="' + url + '" style="color:#417690; font-weight:500; text-decoration:none;">' + obj.name + '</a>')
        return "—"
    short_name.short_description = "Dastur nomi"
    short_name.allow_tags = True

    def tartib_raqami(self, obj):
        """Порядковый номер (пересчитывается JavaScript)"""
        return obj.id
    tartib_raqami.short_description = "T/r"

    def direction_badge(self, obj):
        """Направление в виде бейджа"""
        if obj.direction:
            return mark_safe(f'<span style="background:#e8f0f5; color:#417690; padding:4px 10px; border-radius:3px; font-size:11px; font-weight:bold;">{obj.direction.name}</span>')
        return "—"
    direction_badge.short_description = "Yo'nalish"
    direction_badge.allow_tags = True

    def academic_year_badge(self, obj):
        """Учебный год в виде бейджа"""
        if obj.academic_year:
            return mark_safe(f'<span style="background:#79aec8; color:white; padding:4px 10px; border-radius:3px; font-size:12px; font-weight:bold;">{obj.academic_year}</span>')
        return "—"
    academic_year_badge.short_description = "O'quv yili"
    academic_year_badge.allow_tags = True

    def file_icon(self, obj):
        """Иконка файла"""
        if obj.file:
            return mark_safe("<a href='" + obj.file.url + "' target='_blank' style='color:#417690; font-size:18px; text-decoration:none;' title='Faylni korish'>📄</a>")
        return '<span style="color:#ccc;">—</span>'
    file_icon.short_description = "Fayl"
    file_icon.allow_tags = True

    def created_at_short(self, obj):
        """Короткая дата"""
        if obj.created_at:
            return obj.created_at.strftime("%d.%m.%Y %H:%M")
        return "—"
    created_at_short.short_description = "Sana"
    created_at_short.admin_order_field = 'created_at'

    class Media:
        css = {
            'all': ('admin/css/custom_studyprogram.css',)
        }
        js = ('admin/js/custom_file_widget.js',)


@admin.register(Module)
class ModuleAdmin(ImportExportModelAdmin):
    list_display = ("name", "hours", "module_type", "get_directions", "is_active", "created_at")
    list_filter = ("module_type", "is_active", "directions")
    search_fields = ("name", "directions__name")
    ordering = ("-created_at",)
    fields = ("name", "hours", "module_type", "description", "directions", "is_active")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("directions",)
    resource_class = ModuleResource
    export_formats = (XLSX,)
    import_formats = ()
    change_list_template = 'admin/directions/module/change_list.html'  # Явно указываем шаблон

    def get_queryset(self, request):
        """Добавляем статистику в контекст"""
        qs = super().get_queryset(request)
        params = dict(request.GET.items())

        if 'module_type__exact' in params:
            qs = qs.filter(module_type=params['module_type__exact'])
        if 'is_active__exact' in params:
            qs = qs.filter(is_active=params['is_active__exact'] == 'True')
        if 'directions__id__exact' in params:
            qs = qs.filter(directions__id=params['directions__id__exact'])

        return qs

    def changelist_view(self, request, extra_context=None):
        """Добавляем итоговую статистику по часам"""
        qs = self.get_queryset(request)

        # Общая статистика
        total_hours = qs.aggregate(total=Sum('hours'))['total'] or 0
        nazariy_hours = qs.filter(module_type='nazariy').aggregate(total=Sum('hours'))['total'] or 0
        amaliy_hours = qs.filter(module_type='amaliy').aggregate(total=Sum('hours'))['total'] or 0

        # Количество модулей
        total_modules = qs.count()
        nazariy_modules = qs.filter(module_type='nazariy').count()
        amaliy_modules = qs.filter(module_type='amaliy').count()

        # Процентное соотношение
        nazariy_percent = round((nazariy_hours / total_hours * 100), 1) if total_hours > 0 else 0
        amaliy_percent = round((amaliy_hours / total_hours * 100), 1) if total_hours > 0 else 0

        extra_context = extra_context or {}
        extra_context['module_stats'] = {
            'total_hours': total_hours,
            'nazariy_hours': nazariy_hours,
            'amaliy_hours': amaliy_hours,
            'total_modules': total_modules,
            'nazariy_modules': nazariy_modules,
            'amaliy_modules': amaliy_modules,
            'nazariy_percent': nazariy_percent,
            'amaliy_percent': amaliy_percent,
        }
        return super().changelist_view(request, extra_context=extra_context)

    def get_directions(self, obj):


        """Выводит названия направлений списком"""


        dirs = list(obj.directions.all())


        if dirs:


            if len(dirs) > 1:


                return mark_safe("<br>".join([f"<span style='background:#e8f0f5;color:#417690;padding:3px 8px;border-radius:3px;font-size:12px;'>{d.name}</span>" for d in dirs]))


            else:


                return dirs[0].name


        return "—"


    get_directions.short_description = "Yo'nalishlar"


    get_directions.allow_tags = True



