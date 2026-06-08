from django.db import migrations, models
import django.db.models.deletion


DEFAULT_ADVANTAGES = [
    {
        'order': 1,
        'icon': 'fa-certificate',
        'title_az': 'Beynəlxalq Diplom',
        'title_en': 'International Diploma',
        'title_ru': 'Международный диплом',
    },
    {
        'order': 2,
        'icon': 'fa-briefcase',
        'title_az': 'Karyera İmkanları',
        'title_en': 'Career Opportunities',
        'title_ru': 'Карьерные возможности',
    },
    {
        'order': 3,
        'icon': 'fa-language',
        'title_az': 'Dil Bacarıqları',
        'title_en': 'Language Skills',
        'title_ru': 'Языковые навыки',
    },
    {
        'order': 4,
        'icon': 'fa-globe-americas',
        'title_az': 'Qlobal Şəbəkə',
        'title_en': 'Global Network',
        'title_ru': 'Глобальная сеть',
    },
    {
        'order': 5,
        'icon': 'fa-hand-holding-usd',
        'title_az': 'Stipendiya Dəstəyi',
        'title_en': 'Scholarship Support',
        'title_ru': 'Поддержка стипендий',
    },
    {
        'order': 6,
        'icon': 'fa-passport',
        'title_az': 'Viza Yardımı',
        'title_en': 'Visa Assistance',
        'title_ru': 'Помощь с визой',
    },
]


def seed_study_abroad_advantages(apps, schema_editor):
    StudyAbroadSection = apps.get_model('projects', 'StudyAbroadSection')
    StudyAbroadAdvantage = apps.get_model('projects', 'StudyAbroadAdvantage')

    section = StudyAbroadSection.objects.first()
    if section is None:
        section = StudyAbroadSection.objects.create(
            advantages_title_az='Xaricdə Təhsilin Üstünlükləri',
            advantages_title_en='Advantages of Studying Abroad',
            advantages_title_ru='Преимущества обучения за рубежом',
        )
    else:
        updated = False
        if not (section.advantages_title_az or '').strip():
            section.advantages_title_az = 'Xaricdə Təhsilin Üstünlükləri'
            updated = True
        if not (section.advantages_title_en or '').strip():
            section.advantages_title_en = 'Advantages of Studying Abroad'
            updated = True
        if not (section.advantages_title_ru or '').strip():
            section.advantages_title_ru = 'Преимущества обучения за рубежом'
            updated = True
        if updated:
            section.save(update_fields=[
                'advantages_title_az',
                'advantages_title_en',
                'advantages_title_ru',
            ])

    if StudyAbroadAdvantage.objects.filter(section_id=section.id).exists():
        return

    StudyAbroadAdvantage.objects.bulk_create([
        StudyAbroadAdvantage(section=section, **row)
        for row in DEFAULT_ADVANTAGES
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0076_review_message_max_length_276'),
    ]

    operations = [
        migrations.AddField(
            model_name='studyabroadsection',
            name='advantages_title_az',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Advantages heading (AZ)'),
        ),
        migrations.AddField(
            model_name='studyabroadsection',
            name='advantages_title_en',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Advantages heading (EN)'),
        ),
        migrations.AddField(
            model_name='studyabroadsection',
            name='advantages_title_ru',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Advantages heading (RU)'),
        ),
        migrations.CreateModel(
            name='StudyAbroadAdvantage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.CharField(default='fa-star', help_text='Font Awesome 5 class, e.g. fa-certificate', max_length=80, verbose_name='Icon (Font Awesome)')),
                ('title_az', models.CharField(max_length=160, verbose_name='Label (AZ)')),
                ('title_en', models.CharField(blank=True, max_length=160, verbose_name='Label (EN)')),
                ('title_ru', models.CharField(blank=True, max_length=160, verbose_name='Label (RU)')),
                ('order', models.PositiveIntegerField(db_index=True, default=0)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='advantage_items', to='projects.studyabroadsection', verbose_name='Section')),
            ],
            options={
                'verbose_name': 'Study abroad advantage',
                'verbose_name_plural': 'Study abroad advantages',
                'ordering': ('order', 'id'),
            },
        ),
        migrations.RunPython(seed_study_abroad_advantages, migrations.RunPython.noop),
    ]
