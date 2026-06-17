from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='show_on_homepage',
            field=models.BooleanField(
                default=True,
                help_text=(
                    'Admin only. When enabled, the promotion banner appears on the homepage. '
                    'When disabled, the sale stays active but the banner is hidden.'
                ),
                verbose_name='Show on homepage',
            ),
        ),
    ]
