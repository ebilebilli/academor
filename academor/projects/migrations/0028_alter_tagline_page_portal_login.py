from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0027_media_portal_login_page_background'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagline',
            name='page',
            field=models.CharField(
                choices=[
                    ('about', 'About page'),
                    ('contact', 'Contact page'),
                    ('service', 'Services page'),
                    ('courses', 'Courses page'),
                    ('mock_tests', 'Mock tests page'),
                    ('tests', 'Tests page'),
                    ('abroad', 'Study abroad page'),
                    ('blog', 'Blog page'),
                    ('team', 'Team page'),
                    ('portal_login', 'Portal login page'),
                ],
                db_index=True,
                default='about',
                help_text='Inner page whose banner shows this tagline.',
                max_length=20,
                unique=True,
                verbose_name='Page',
            ),
        ),
    ]
