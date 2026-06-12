import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        ('projects', '0084_media_sale'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='product_type',
            field=models.CharField(
                choices=[('course', 'Course'), ('generic', 'Generic')],
                db_index=True,
                default='generic',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='buyer_email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='payment',
            name='buyer_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='payment',
            name='buyer_phone',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AddField(
            model_name='payment',
            name='enrollment_completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
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
        migrations.AddField(
            model_name='payment',
            name='price_package',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='payments',
                to='projects.coursepricepackage',
                verbose_name='Price package',
            ),
        ),
    ]
