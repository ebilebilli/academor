from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0005_contact_map_embed_url"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="media",
            name="is_footer_background_image",
        ),
        migrations.AddField(
            model_name="media",
            name="is_courses_page_background_image",
            field=models.BooleanField(
                default=False,
                verbose_name="Courses page background image",
            ),
        ),
        migrations.AddField(
            model_name="media",
            name="is_tests_page_background_image",
            field=models.BooleanField(
                default=False,
                verbose_name="Tests pages background image",
            ),
        ),
    ]
