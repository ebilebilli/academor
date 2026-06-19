from django.db import migrations, models
import django.core.validators


def remove_home_taglines(apps, schema_editor):
    Tagline = apps.get_model('projects', 'Tagline')
    Tagline.objects.filter(page='home').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_tagline_page_fields'),
    ]

    operations = [
        migrations.RunPython(remove_home_taglines, migrations.RunPython.noop),
        migrations.RemoveField(model_name='tagline', name='body_en'),
        migrations.RemoveField(model_name='tagline', name='body_ru'),
        migrations.RemoveField(model_name='tagline', name='heading_main_az'),
        migrations.RemoveField(model_name='tagline', name='heading_main_en'),
        migrations.RemoveField(model_name='tagline', name='heading_main_ru'),
        migrations.RemoveField(model_name='tagline', name='heading_small_az'),
        migrations.RemoveField(model_name='tagline', name='heading_small_en'),
        migrations.RemoveField(model_name='tagline', name='heading_small_ru'),
        migrations.RenameField(
            model_name='tagline',
            old_name='body_az',
            new_name='text',
        ),
        migrations.AlterField(
            model_name='tagline',
            name='page',
            field=models.CharField(
                choices=[
                    ('about', 'About page'),
                    ('contact', 'Contact page'),
                    ('service', 'Services page'),
                    ('courses', 'Courses page'),
                    ('tests', 'Tests page'),
                    ('abroad', 'Study abroad page'),
                    ('blog', 'Blog page'),
                    ('team', 'Team page'),
                ],
                db_index=True,
                default='about',
                help_text='Inner page whose banner shows this tagline.',
                max_length=20,
                unique=True,
                verbose_name='Page',
            ),
        ),
        migrations.AlterField(
            model_name='tagline',
            name='order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Reserved for admin list sorting.',
                verbose_name='Order',
            ),
        ),
        migrations.AlterField(
            model_name='tagline',
            name='text',
            field=models.TextField(
                blank=True,
                validators=[django.core.validators.MaxLengthValidator(400)],
                verbose_name='Description (AZ)',
            ),
        ),
    ]
