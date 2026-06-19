from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_remove_coursepricepackage_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagline',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Active'),
        ),
        migrations.AddField(
            model_name='tagline',
            name='order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Lower numbers appear first (home carousel).',
                verbose_name='Order',
            ),
        ),
        migrations.AddField(
            model_name='tagline',
            name='page',
            field=models.CharField(
                choices=[
                    ('home', 'Home page (hero carousel)'),
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
                default='home',
                help_text='Which page banner shows this tagline. Home allows multiple rows for the hero carousel.',
                max_length=20,
                verbose_name='Page',
            ),
        ),
        migrations.AlterModelOptions(
            name='tagline',
            options={
                'ordering': ('page', 'order', 'pk'),
                'verbose_name': 'Tagline',
                'verbose_name_plural': 'Taglines',
            },
        ),
    ]
