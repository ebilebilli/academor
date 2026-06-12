from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0083_sale_description_richtext'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='sale',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='medias',
                to='projects.sale',
                verbose_name='Sale',
            ),
        ),
    ]
