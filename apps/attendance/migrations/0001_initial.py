import django.db.models.deletion
import secrets
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('schedules', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='AttendanceToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('is_used', models.BooleanField(default=False, verbose_name='Ishlatilgan')),
                ('used_at', models.DateTimeField(blank=True, null=True, verbose_name='Ishlatilgan vaqt')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')),
                ('expires_at', models.DateTimeField(verbose_name='Amal qilish muddati')),
                ('secret', models.CharField(default=secrets.token_urlsafe, max_length=64, verbose_name='Maxfiy kalit')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_tokens', to='schedules.schedule', verbose_name='Dars')),
                ('used_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attended_tokens', to=settings.AUTH_USER_MODEL, verbose_name='Ishlatgan')),
            ],
            options={
                'verbose_name': 'Davomat QR tokeni',
                'verbose_name_plural': 'Davomat QR tokenlari',
            },
        ),
        migrations.AddIndex(
            model_name='attendancetoken',
            index=models.Index(fields=['token'], name='attendance__token_e1c78b_idx'),
        ),
    ]
