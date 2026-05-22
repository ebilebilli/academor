from django.db import migrations, models


def seed_about_why_items(apps, schema_editor):
    AboutWhyItem = apps.get_model('projects', 'AboutWhyItem')
    if AboutWhyItem.objects.exists():
        return
    AboutWhyItem.objects.bulk_create([
        AboutWhyItem(
            order=1,
            icon='fa-chalkboard-teacher',
            title_az='Peşəkar müəllim heyəti',
            title_en='Professional teaching team',
            title_ru='Профессиональная команда преподавателей',
            text_az='Təcrübəli müəllimlər və müasir sinif mühiti.',
            text_en='Experienced teachers and a modern classroom environment.',
            text_ru='Опытные преподаватели и современная учебная среда.',
        ),
        AboutWhyItem(
            order=2,
            icon='fa-globe-americas',
            title_az='Beynəlxalq imkanlar',
            title_en='International opportunities',
            title_ru='Международные возможности',
            text_az='Xaricdə təhsil və dil imtahanlarına hazırlıq.',
            text_en='Study abroad pathways and exam preparation support.',
            text_ru='Обучение за рубежом и подготовка к экзаменам.',
        ),
        AboutWhyItem(
            order=3,
            icon='fa-chart-line',
            title_az='Müasir tədris metodları',
            title_en='Modern learning methods',
            title_ru='Современные методы обучения',
            text_az='Praktiki dərslər və real nəticəyə yönəlmiş proqramlar.',
            text_en='Practical lessons focused on measurable progress.',
            text_ru='Практические занятия с измеримым результатом.',
        ),
        AboutWhyItem(
            order=4,
            icon='fa-handshake',
            title_az='Fərdi yanaşma',
            title_en='Personal approach',
            title_ru='Индивидуальный подход',
            text_az='Hər tələbənin məqsədinə uyğun dəstək və məsləhət.',
            text_en='Guidance tailored to each student’s goals.',
            text_ru='Поддержка с учётом целей каждого студента.',
        ),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0058_contact_email_2_email_3'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutWhyItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(default='fa-star', help_text='Font Awesome 5 class, e.g. fa-graduation-cap', max_length=80, verbose_name='Icon (Font Awesome)')),
                ('title_az', models.CharField(max_length=160, verbose_name='Title (AZ)')),
                ('title_en', models.CharField(blank=True, max_length=160, verbose_name='Title (EN)')),
                ('title_ru', models.CharField(blank=True, max_length=160, verbose_name='Title (RU)')),
                ('text_az', models.CharField(blank=True, max_length=280, verbose_name='Text (AZ)')),
                ('text_en', models.CharField(blank=True, max_length=280, verbose_name='Text (EN)')),
                ('text_ru', models.CharField(blank=True, max_length=280, verbose_name='Text (RU)')),
                ('order', models.PositiveIntegerField(db_index=True, default=0)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
            ],
            options={
                'verbose_name': 'Why Academor item',
                'verbose_name_plural': 'Why Academor items',
                'ordering': ('order', 'id'),
            },
        ),
        migrations.RunPython(seed_about_why_items, migrations.RunPython.noop),
    ]
