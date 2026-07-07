from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0006_alter_studentrecord_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name_name='studentrecord',
            name='passport',
            field=models.CharField(max_length=50, blank=True, null=True, verbose_name="Pasport"),
        ),
    ]
