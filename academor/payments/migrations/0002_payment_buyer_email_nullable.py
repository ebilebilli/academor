from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='buyer_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='courseenrollment',
            name='buyer_email',
            field=models.EmailField(blank=True, db_index=True, max_length=254, null=True),
        ),
    ]
