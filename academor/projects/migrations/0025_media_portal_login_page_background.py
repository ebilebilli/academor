from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0024_alter_tagline_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='is_portal_login_page_background_image',
            field=models.BooleanField(
                default=False,
                verbose_name='Portal login page background image',
            ),
        ),
    ]
