from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0064_ielts_mock_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonattachment',
            name='video_url',
            field=models.URLField(blank=True, verbose_name='Video URL'),
        ),
        migrations.AlterField(
            model_name='lessonattachment',
            name='file',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='portals/lessons/attachments/',
                verbose_name='File',
            ),
        ),
        migrations.AlterField(
            model_name='lessonattachment',
            name='kind',
            field=models.CharField(
                choices=[('pdf', 'PDF'), ('image', 'Image'), ('video', 'Video')],
                max_length=16,
                verbose_name='Type',
            ),
        ),
    ]
