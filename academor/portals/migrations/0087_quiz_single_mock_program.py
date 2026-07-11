from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0086_customer_program_mock_credits'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='quiz',
            constraint=models.CheckConstraint(
                condition=~models.Q(is_ielts=True, is_sat=True),
                name='portals_quiz_single_mock_program',
            ),
        ),
    ]
