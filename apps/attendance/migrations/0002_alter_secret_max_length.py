from django.db import migrations, models
import secrets


class Migration(migrations.Migration):
    dependencies = [('attendance', '0001_initial')]
    operations = [
        migrations.AlterField(
            model_name='attendancetoken',
            name='secret',
            field=models.CharField(default=secrets.token_urlsafe, max_length=64, verbose_name='Maxfiy kalit'),
        ),
    ]
