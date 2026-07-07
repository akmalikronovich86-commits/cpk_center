from django.contrib import admin, messages
from django.db import models
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.formats.base_formats import XLSX
from django.db.models import Window, F
from django.db.models.functions import RowNumber
from .models import TrainingYear, StudentRecord


class StudentRecordResource(resources.ModelResource):
    xtm = fields.Field(column_name='XTM', attribute='xtm')
    full_name = fields.Field(column_name='Malaka oshiruvchilar', attribute='full_name')
    position = fields.Field(column_name='Lavozimi', attribute='position')
    passport = fields.Field(column_name='Pasport', attribute='passport')
    birth_date = fields.Field(column_name="Tug'ilgan sana", attribute='birth_date')
    group = fields.Field(column_name='Guruhi', attribute='group')
    branch = fields.Field(column_name='Hududiy filiali nomi', attribute='branch')
    district_power = fields.Field(column_name='Tuman elektr taminoti', attribute='district_power')
    phone = fields.Field(column_name='Telefon raqami', attribute='phone')
    grade = fields.Field(column_name='Yakuniy bahosi', attribute='grade')
    topic = fields.Field(column_name='Mustaqil talim mavzusi', attribute='topic')
    period = fields.Field(column_name='Malaka oshirish muddati', attribute='period')

    class Meta:
        model = StudentRecord
        exclude = ('id', 'created_at')
        import_id_fields = ()

    def __init__(self, *args, **kwargs):
        self.year_id = kwargs.pop('year_id', None)
        self.request = kwargs.pop('request', None)
        self.duplicate_warnings = []
        super().__init__(*args, **kwargs)

    def skip_row(self, instance, original, row, import_validation_errors=None):
        if not instance.full_name or not instance.passport:
            return True
        if row.get('_skip_duplicate'):
            return True
        return super().skip_row(instance, original, row, import_validation_errors)

    def before_save_instance(self, instance, *args, **kwargs):
        if self.year_id:
            instance.training_year_id = self.year_id

    def before_import_row(self, row, row_number=None, **kwargs):
        full_name = str(row.get('Malaka oshiruvchilar', '')).strip()
        passport = str(row.get('Pasport', '')).strip()
        if not full_name or not passport:
            return
        if self.year_id:
            exists = StudentRecord.objects.filter(
                training_year_id=self.year_id
            ).filter(
                models.Q(full_name__iexact=full_name) |
                models.Q(passport__iexact=passport)
            ).exists()
            if exists:
                self.duplicate_warnings.append(f"{full_name} ({passport})")
                row['_skip_duplicate'] = True

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        if not dry_run and self.request and self.duplicate_warnings:
            existing = self.request.session.get('import_duplicate_warnings', [])
            existing.extend(self.duplicate_warnings)
            self.request.session['import_duplicate_warnings'] = existing


@admin.register(StudentRecord)
class StudentRecordAdmin(ImportExportModelAdmin):
    change_list_template = 'admin/groups/studentrecord/change_list.html'
    resource_class = StudentRecordResource

    def tartib_raqami(self, obj):
        """Простая нумерация по ID"""
        return obj.id if obj.id else '—'
    tartib_raqami.short_description = "T/r"
    tartib_raqami.admin_order_field = 'id'

    list_display = ('user_link', 'tartib_raqami', 'full_name', 'passport', 'phone', 'group', 'branch', 'training_year')

    def user_link(self, obj):
        if obj.user:
            from django.utils.html import format_html
            return format_html(
                '<a href="/admin/groups/studentrecord/{}/change/">{}</a>',
                obj.id,
                f'{obj.user.username} ({obj.user.email or "нет email"})'
            )
        return "— (bog'lanmagan)"
    user_link.short_description = 'Foydalanuvchi'
    user_link.admin_order_field = 'user__username'
    list_filter = ('training_year', 'group', 'branch')
    search_fields = ('full_name', 'passport', 'phone')
    ordering = ('full_name',)
    import_formats = (XLSX,)
    export_formats = (XLSX,)
    readonly_fields = ('id', 'created_at')

    def user_info(self, obj):
        """Отображение информации о пользователе"""
        if obj.user:
            return f"{obj.user.username} ({obj.user.email or 'нет email'})"
        return "— (не связан)"
    user_info.short_description = "Foydalanuvchi"
    user_info.admin_order_field = 'user__username'

    fieldsets = (
        ('Asosiy malumotlar', {'fields': ('id', 'user', 'full_name', 'passport', 'xtm', 'birth_date')}),
        ('Guruh va filial', {'fields': ('group', 'branch', 'district_power', 'phone')}),
        ('Natijalar', {'fields': ('position', 'grade', 'topic', 'period', 'training_year')}),
    )

    def changelist_view(self, request, extra_context=None):
        year_id = request.GET.get('training_year__id__exact')
        if year_id:
            request.session['import_year_id'] = year_id
        warnings = request.session.pop('import_duplicate_warnings', [])
        if warnings:
            unique_warnings = list(dict.fromkeys(warnings))
            for w in unique_warnings[:15]:
                messages.warning(request, f"Otkazib yuborildi (dublikat): {w}")
        return super().changelist_view(request, extra_context=extra_context)

    def get_import_resource_kwargs(self, request, *args, **kwargs):
        kwargs = super().get_import_resource_kwargs(request, *args, **kwargs)
        year_id = request.session.get('import_year_id')
        if not year_id:
            year_id = request.GET.get('training_year__id__exact')
        if year_id:
            kwargs['year_id'] = year_id
            kwargs['request'] = request
            try:
                year = TrainingYear.objects.get(id=year_id)
                messages.success(request, f"Import yili: {year.name}")
            except TrainingYear.DoesNotExist:
                pass
        else:
            messages.error(request, "Yil tanlanmagan!")
        return kwargs


@admin.register(TrainingYear)
class TrainingYearAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
