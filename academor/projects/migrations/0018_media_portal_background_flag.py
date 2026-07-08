from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0017_sale_remove_apply_flags"),
    ]

    operations = [
        migrations.AddField(
            model_name="media",
            name="is_portal_page_background_image",
            field=models.BooleanField(
                default=False, verbose_name="Portal page background image"
            ),
        ),
    ]

