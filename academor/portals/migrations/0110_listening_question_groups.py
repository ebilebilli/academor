import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0109_readingquestion_spr_answers'),
    ]

    operations = [
        migrations.CreateModel(
            name='ListeningQuestionGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Order')),
                ('title', models.CharField(blank=True, help_text='Shown to students, e.g. Questions 17–20.', max_length=255, verbose_name='Title')),
                ('instructions', ckeditor.fields.RichTextField(blank=True, help_text='Task instructions shown above the map/plan.', verbose_name='Instructions')),
                ('question_type', models.CharField(choices=[('map_labelling', 'Map labelling'), ('plan_labelling', 'Plan labelling')], default='map_labelling', max_length=32, verbose_name='Task type')),
                ('diagram_image', models.ImageField(blank=True, help_text='Upload the labelled diagram (map or floor plan).', null=True, upload_to='portals/listening/diagrams/', verbose_name='Map / plan image')),
                ('option_pool', models.JSONField(blank=True, default=list, help_text='Letter pool shown as columns, e.g. ["A", "B", "C", "D", "E", "F", "G"].', verbose_name='Label options')),
                ('audio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_groups', to='portals.listeningaudio', verbose_name='Audio section')),
            ],
            options={
                'verbose_name': 'Listening question group',
                'verbose_name_plural': 'Listening question groups',
                'ordering': ('order', 'id'),
            },
        ),
        migrations.AddField(
            model_name='listeningquestion',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Optional map/plan labelling group with a shared letter pool.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questions', to='portals.listeningquestiongroup', verbose_name='Question group'),
        ),
    ]
