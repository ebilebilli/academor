from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0032_replace_question_bank_with_category_questions'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='pool_resource_name',
            field=models.CharField(
                blank=True,
                help_text='When set, random questions are drawn only from category pool rows with this resource name. Leave empty to use the entire category pool.',
                max_length=255,
                verbose_name='Pool resource filter',
            ),
        ),
        migrations.AddField(
            model_name='quiz',
            name='resource_slug',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Stable key from the JSON resource file (e.g. a1_quiz_1). Set when loaded from resources.',
                max_length=128,
                verbose_name='Resource slug',
            ),
        ),
        migrations.AddConstraint(
            model_name='quiz',
            constraint=models.UniqueConstraint(
                condition=models.Q(('resource_slug', ''), _negated=True),
                fields=('category', 'resource_slug'),
                name='portals_quiz_category_resource_slug_uniq',
            ),
        ),
    ]
