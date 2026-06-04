from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0071_seed_price_packages_from_legacy_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coursepricepackage',
            old_name='hours',
            new_name='lesson_minutes',
        ),
    ]
