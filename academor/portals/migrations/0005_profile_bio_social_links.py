from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0004_teacher_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='bio',
            field=models.TextField(blank=True, verbose_name='Bio'),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='facebook',
            field=models.URLField(blank=True, verbose_name='Facebook URL'),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='instagram',
            field=models.URLField(blank=True, verbose_name='Instagram URL'),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='linkedin',
            field=models.URLField(blank=True, verbose_name='LinkedIn URL'),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='youtube',
            field=models.URLField(blank=True, verbose_name='YouTube URL'),
        ),
        migrations.AddField(
            model_name='teacherprofile',
            name='facebook',
            field=models.URLField(blank=True, verbose_name='Facebook URL'),
        ),
        migrations.AddField(
            model_name='teacherprofile',
            name='instagram',
            field=models.URLField(blank=True, verbose_name='Instagram URL'),
        ),
        migrations.AddField(
            model_name='teacherprofile',
            name='linkedin',
            field=models.URLField(blank=True, verbose_name='LinkedIn URL'),
        ),
        migrations.AddField(
            model_name='teacherprofile',
            name='youtube',
            field=models.URLField(blank=True, verbose_name='YouTube URL'),
        ),
    ]
