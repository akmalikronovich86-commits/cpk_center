from import_export import fields, resources
from import_export.widgets import ManyToManyWidget

from apps.users.models import Module

from .models import Direction


class ModuleResource(resources.ModelResource):
    # Настраиваем поля для экспорта
    directions = fields.Field(
        column_name='Yo\'nalishlar',
        attribute='directions',
        widget=ManyToManyWidget(Direction, field='name', separator=', ')
    )

    module_type = fields.Field(
        column_name='Dars turi',
        attribute='module_type'
    )

    class Meta:
        model = Module
        fields = (
            'id',
            'name',
            'hours',
            'module_type',
            'directions',
            'description',
            'is_active',
            'created_at',
        )
        export_order = fields

    def dehydrate_module_type(self, module):
        """Преобразуем nazariy/amaliy в читаемый вид"""
        return module.get_module_type_display()
