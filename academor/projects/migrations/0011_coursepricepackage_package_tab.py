from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_coursepricepackage_show_on_homepage'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursepricepackage',
            name='package_tab',
            field=models.CharField(
                choices=[
                    ('group_standard', 'Group lessons — Standard'),
                    ('group_intensive', 'Group lessons — Intensive'),
                    ('individual_standard', 'Individual lessons — Standard'),
                    ('individual_intensive', 'Individual lessons — Intensive'),
                    ('full_package', 'Full packages'),
                    ('full_package_installment', 'Full package — Installments'),
                ],
                db_index=True,
                default='group_standard',
                help_text='Which tab on the course payment section shows this package.',
                max_length=32,
                verbose_name='Payment tab',
            ),
        ),
    ]
