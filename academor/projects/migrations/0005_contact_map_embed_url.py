from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_media_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="map_embed_url",
            field=models.TextField(
                blank=True,
                help_text="iframe src dəyəri (məs. https://www.google.com/maps/embed?pb=...)",
                null=True,
                verbose_name="Google Maps embed URL",
            ),
        ),
    ]
