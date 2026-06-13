from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0086_sale_nullable_percent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='old_price',
        ),
    ]
