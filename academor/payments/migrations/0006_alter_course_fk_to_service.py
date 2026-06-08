import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0078_rename_service_remove_highlight_instructor'),
        ('payments', '0005_payment_price_package'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='course',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='payments',
                to='projects.service',
                verbose_name='Course',
            ),
        ),
        migrations.AlterField(
            model_name='courseenrollment',
            name='course',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='enrollments',
                to='projects.service',
            ),
        ),
    ]
