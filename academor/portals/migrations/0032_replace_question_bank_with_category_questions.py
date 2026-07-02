from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0031_quiz_category_question_bank'),
    ]

    operations = [
        migrations.DeleteModel(
            name='QuizCategoryQuestionBank',
        ),
        migrations.CreateModel(
            name='QuizCategoryQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_name', models.CharField(blank=True, help_text='Source file name this question was loaded from.', max_length=255, verbose_name='Resource name')),
                ('level', models.CharField(blank=True, db_index=True, help_text='Level label from the resource file.', max_length=64, verbose_name='Level')),
                ('source_key', models.CharField(help_text='Stable key for upsert when reloading resources.', max_length=64, verbose_name='Source key')),
                ('question', models.TextField(verbose_name='Question text')),
                ('answer_options', models.JSONField(default=list, verbose_name='Answer options')),
                ('correct_option_index', models.PositiveIntegerField(default=0, verbose_name='Correct option index')),
                ('correct_answer', models.CharField(blank=True, max_length=500, verbose_name='Correct answer')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Active')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_questions', to='portals.quizcategory', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Category question',
                'verbose_name_plural': 'Category questions',
                'ordering': ('id',),
            },
        ),
        migrations.AddConstraint(
            model_name='quizcategoryquestion',
            constraint=models.UniqueConstraint(fields=('category', 'source_key'), name='portals_quiz_category_question_uniq'),
        ),
    ]
