from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0072_rename_hours_to_lesson_minutes'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecategory',
            name='card_icon',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Default — open book'),
                    ('fa-book-open', 'General English / language course'),
                    ('fa-language', 'English / language learning'),
                    ('fa-comments', 'Speaking / conversation'),
                    ('fa-microphone-alt', 'Speaking practice / Only Speaking'),
                    ('fa-headphones', 'Listening practice'),
                    ('fa-pen', 'Writing skills'),
                    ('fa-certificate', 'IELTS / certificate program'),
                    ('fa-file-alt', 'Exam preparation (general)'),
                    ('fa-chart-line', 'GMAT / GRE / test strategy'),
                    ('fa-calculator', 'GMAT — quantitative'),
                    ('fa-graduation-cap', 'GRE / university admission test'),
                    ('fa-university', 'YÖS / university placement'),
                    ('fa-user-graduate', 'ALES / academic exam'),
                    ('fa-pencil-alt', 'SAT / standardized test'),
                    ('fa-globe-americas', 'Study abroad'),
                    ('fa-plane-departure', 'Study abroad / international'),
                    ('fa-laptop', 'Online lessons'),
                    ('fa-users', 'Group classes'),
                    ('fa-user', 'Private / individual lessons'),
                    ('fa-briefcase', 'Business English'),
                    ('fa-child', 'Kids / young learners'),
                    ('fa-chalkboard-teacher', 'Teaching / instruction'),
                    ('fa-star', 'Featured / premium program'),
                ],
                default='',
                help_text='Font Awesome 5 icon on service cards (home page and courses list). Choose a preset matching the program (IELTS, GMAT, Speaking, etc.).',
                max_length=80,
                verbose_name='Card icon',
            ),
        ),
    ]
