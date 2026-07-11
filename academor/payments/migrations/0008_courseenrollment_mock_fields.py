import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0080_ieltsmocktestattempt_credit_consumed'),
        ('projects', '0018_media_portal_background_flag'),
        ('payments', '0007_customer_mock_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseenrollment',
            name='course',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='enrollments',
                to='projects.service',
            ),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='customer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='enrollments',
                to='portals.customerprofile',
                verbose_name='Customer',
            ),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='mock_package',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='enrollments',
                to='portals.mocktestpackage',
                verbose_name='Mock test package',
            ),
        ),
    ]
