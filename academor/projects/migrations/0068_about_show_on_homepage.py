from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0067_aboutgalleryitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='about',
            name='show_on_homepage',
            field=models.BooleanField(
                default=True,
                help_text='When enabled, the About block is shown on the home page (after the blog hero).',
                verbose_name='Show on homepage',
            ),
        ),
    ]
