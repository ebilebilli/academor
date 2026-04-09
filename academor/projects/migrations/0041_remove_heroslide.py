from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0040_abroadmodel_localized_names'),
    ]

    operations = [
        migrations.DeleteModel(
            name='HeroSlide',
        ),
    ]
