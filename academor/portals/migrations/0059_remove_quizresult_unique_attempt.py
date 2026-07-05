from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0058_quiz_is_reading_reading_models'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='quizresult',
            name='portals_quiz_result_one_per_student',
        ),
    ]
