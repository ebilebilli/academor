from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0014_alter_parentprofile_students_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='lesson_date',
            field=models.DateField(blank=True, null=True, verbose_name='Lesson date'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='subject',
            field=models.CharField(
                choices=[
                    ('general_english', 'General English'),
                    ('speaking', 'Speaking'),
                    ('ielts', 'IELTS'),
                    ('gmat', 'GMAT'),
                    ('gre', 'GRE'),
                    ('sat', 'SAT'),
                    ('yos', 'YÖS'),
                    ('ales', 'ALES'),
                    ('study_abroad', 'Study abroad'),
                    ('other', 'Other'),
                ],
                db_index=True,
                max_length=32,
                verbose_name='Service',
            ),
        ),
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='portals/classrooms/pdf/', verbose_name='PDF file')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
            ],
            options={
                'verbose_name': 'Classroom',
                'verbose_name_plural': 'Classrooms',
                'ordering': ('-created_at', 'id'),
            },
        ),
    ]
