from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0057_alter_blogpost_on_main_page_alter_blogpost_on_top'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='email_2',
            field=models.EmailField(blank=True, null=True, verbose_name='Email 2'),
        ),
        migrations.AddField(
            model_name='contact',
            name='email_3',
            field=models.EmailField(blank=True, null=True, verbose_name='Email 3'),
        ),
    ]
