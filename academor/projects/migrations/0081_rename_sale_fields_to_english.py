from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0080_sale_apply_to_service_prices'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sale',
            old_name='ad_az',
            new_name='name_az',
        ),
        migrations.RenameField(
            model_name='sale',
            old_name='ad_en',
            new_name='name_en',
        ),
        migrations.RenameField(
            model_name='sale',
            old_name='ad_ru',
            new_name='name_ru',
        ),
        migrations.RenameField(
            model_name='sale',
            old_name='melumat_az',
            new_name='description_az',
        ),
        migrations.RenameField(
            model_name='sale',
            old_name='melumat_en',
            new_name='description_en',
        ),
        migrations.RenameField(
            model_name='sale',
            old_name='melumat_ru',
            new_name='description_ru',
        ),
    ]
