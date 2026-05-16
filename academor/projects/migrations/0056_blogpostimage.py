from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0055_blogpost'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPostImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='blog/', verbose_name='Image')),
                ('order', models.PositiveSmallIntegerField(
                    default=0,
                    validators=[django.core.validators.MaxValueValidator(5)],
                    verbose_name='Order',
                    help_text='0 = cover (first). Max 6 images total.',
                )),
                ('post', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='images',
                    to='projects.blogpost',
                    verbose_name='Blog post',
                )),
            ],
            options={
                'verbose_name': 'Blog post image',
                'verbose_name_plural': 'Blog post images',
                'ordering': ('order', 'id'),
            },
        ),
    ]
