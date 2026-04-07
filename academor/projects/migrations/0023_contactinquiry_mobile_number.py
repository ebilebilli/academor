from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0022_media_is_footer_background_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactinquiry',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Mobile number'),
        ),
    ]
