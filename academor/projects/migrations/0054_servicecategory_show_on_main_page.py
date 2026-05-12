from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0053_abroadmodel_show_on_main_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecategory',
            name='show_on_main_page',
            field=models.BooleanField(
                default=True,
                help_text='If enabled, this course appears in the "Our Services" grid on the homepage.',
                verbose_name='Show on home page',
            ),
        ),
    ]
