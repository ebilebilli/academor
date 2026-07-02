from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0034_remove_random_pool_inline_quiz_questions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='teacher',
        ),
    ]
