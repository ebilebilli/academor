import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_payment_course_fields'),
        ('projects', '0084_media_sale'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer_email', models.EmailField(blank=True, db_index=True, max_length=254)),
                ('buyer_name', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(choices=[('active', 'Active'), ('cancelled', 'Cancelled')], db_index=True, default='active', max_length=20)),
                ('buyer_phone', models.CharField(blank=True, max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='enrollments', to='projects.service')),
                ('price_package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrollments', to='projects.coursepricepackage', verbose_name='Price package')),
                ('payment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='enrollment', to='payments.payment')),
            ],
            options={
                'verbose_name': 'Course enrollment',
                'verbose_name_plural': 'Course enrollments',
                'ordering': ['-created_at'],
            },
        ),
    ]
