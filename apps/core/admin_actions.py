from django.http import HttpResponse
from datetime import datetime
import openpyxl

class MassActionsMixin:
    """Миксин для массовых действий: экспорт в Excel + изменение статуса"""
    
    actions = ["export_to_excel", "make_active", "make_inactive"]
    
    def export_to_excel(self, request, queryset):
        """Экспорт выбранных записей в Excel"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self.model._meta.verbose_name_plural
        
        # Заголовки: берём human-readable названия полей
        headers = []
        fields = self.model._meta.fields
        for f in fields:
            if f.name not in ['password', 'last_login']:  # исключаем чувствительные поля
                headers.append(f.verbose_name.title() if hasattr(f, 'verbose_name') else f.name)
        ws.append(headers)
        
        # Данные
        for obj in queryset:
            row = []
            for f in fields:
                if f.name not in ['password', 'last_login']:
                    val = getattr(obj, f.name)
                    row.append(str(val) if val is not None else "")
            ws.append(row)
        
        # Авто-ширина колонок
        for col in ws.columns:
            max_len = max((len(str(cell.value or "")) for cell in col), default=0)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
        
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"{self.model._meta.verbose_name_plural}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        wb.save(response)
        
        self.message_user(request, f"{queryset.count()} записей экспортировано в Excel")
        return response
    export_to_excel.short_description = "📥 Tanlanganlarni Excelga eksport qilish"
    
    def make_active(self, request, queryset):
        """Активировать выбранные записи"""
        if hasattr(queryset.first(), 'is_active'):
            count = queryset.update(is_active=True)
            self.message_user(request, f"✅ Активировано: {count}")
        else:
            self.message_user(request, "⚠️  Ushbu modelda is_active maydoni mavjud emas", level="warning")
    make_active.short_description = "✅ Tanlanganlarni faollashtirish"
    
    def make_inactive(self, request, queryset):
        """Деактивировать выбранные записи"""
        if hasattr(queryset.first(), 'is_active'):
            count = queryset.update(is_active=False)
            self.message_user(request, f"⏸️ Деактивировано: {count}")
        else:
            self.message_user(request, "⚠️  Ushbu modelda is_active maydoni mavjud emas", level="warning")
    make_inactive.short_description = "⏸️ Tanlanganlarni faolsizlashtirish"
