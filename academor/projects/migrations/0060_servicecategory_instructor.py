from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0059_aboutwhyitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecategory',
            name='instructor',
            field=models.ForeignKey(
                blank=True,
                help_text='Team member shown on the course detail page (Instructor tab).',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='service_categories',
                to='projects.team',
                verbose_name='Instructor',
            ),
        ),
    ]
