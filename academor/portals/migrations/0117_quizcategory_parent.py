# Generated manually for QuizCategory parent self-FK

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0116_abandon_customer_in_progress_mocks'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizcategory',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    'Optional parent. Nested categories appear under the parent on the quizzes page; '
                    'top-level categories (no parent) keep the previous behaviour.'
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='children',
                to='portals.quizcategory',
                verbose_name='Parent category',
            ),
        ),
    ]
