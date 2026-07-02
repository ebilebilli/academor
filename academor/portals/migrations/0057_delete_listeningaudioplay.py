from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portals', '0056_rename_portals_lis_student_6f0f0d_idx_portals_lis_student_cfba39_idx'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ListeningAudioPlay',
        ),
    ]
