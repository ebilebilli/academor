import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_userresult_embed_user_data_remove_testuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='medias',
                to='projects.servicecategory',
                verbose_name='Service category',
            ),
        ),
    ]
