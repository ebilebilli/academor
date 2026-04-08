from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0032_alter_studyabroadsection_richtext'),
    ]

    operations = [
        migrations.AddField(
            model_name='abroadmodel',
            name='detail_page_img',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='abroad/detail/',
                verbose_name='Detail page image',
            ),
        ),
    ]
