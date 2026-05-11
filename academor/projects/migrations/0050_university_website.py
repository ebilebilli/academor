from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0049_university_sync_columns_from_partial_0048'),
    ]

    operations = [
        migrations.AddField(
            model_name='university',
            name='website',
            field=models.URLField(blank=True, max_length=300, null=True, verbose_name='Website URL'),
        ),
    ]
