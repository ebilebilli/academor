from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_coursepricepackage_package_tab'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursepricepackage',
            name='package_tab',
            field=models.CharField(
                choices=[
                    ('group_standard', 'Group lessons — Standard'),
                    ('group_intensive', 'Group lessons — Intensive'),
                    ('individual_standard', 'Individual lessons — Standard'),
                    ('individual_intensive', 'Individual lessons — Intensive'),
                    ('full_package_group', 'Full package — Group'),
                    ('full_package_individual', 'Full package — Individual'),
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
