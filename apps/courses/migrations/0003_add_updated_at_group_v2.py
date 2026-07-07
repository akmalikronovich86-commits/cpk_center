from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0002_add_created_at_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
        ),
    ]
