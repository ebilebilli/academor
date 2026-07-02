from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0038_alter_studygroup_courses'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(db_index=True, max_length=32, verbose_name='Service')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Lesson category',
                'verbose_name_plural': 'Lesson categories',
                'ordering': ('service', 'name', 'id'),
            },
        ),
        migrations.AddConstraint(
            model_name='lessoncategory',
            constraint=models.UniqueConstraint(
                fields=('service', 'name'),
                name='portals_lesson_category_uniq',
            ),
        ),
        migrations.AddField(
            model_name='lesson',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='lessons',
                to='portals.lessoncategory',
                verbose_name='Category',
            ),
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='lesson_type',
        ),
    ]
