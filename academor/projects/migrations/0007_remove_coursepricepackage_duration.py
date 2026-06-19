from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_contenttag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursepricepackage',
            name='duration',
        ),
    ]
