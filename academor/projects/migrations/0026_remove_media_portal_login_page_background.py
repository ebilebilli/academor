from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0025_media_portal_login_page_background'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='is_portal_login_page_background_image',
        ),
    ]
