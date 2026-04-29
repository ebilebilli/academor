"""
Review.video_embed_url: some DBs have this column as NOT NULL without DEFAULT.
Exposing it in Django and setting DEFAULT '' fixes admin INSERTs; new installs get the column.
"""

from django.db import migrations, models
from django.db.utils import OperationalError


def forwards_review_video_embed_url(apps, schema_editor):
    Review = apps.get_model('projects', 'Review')
    connection = schema_editor.connection
    table = Review._meta.db_table
    q = connection.ops.quote_name

    field = models.URLField(blank=True, default='', max_length=500)
    field.set_attributes_from_name('video_embed_url')
    field.model = Review

    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = ANY (current_schemas(true))
                  AND table_name = %s
                  AND column_name = 'video_embed_url'
                """,
                [table],
            )
            has_col = cursor.fetchone()
            if has_col:
                cursor.execute(
                    f'UPDATE {q(table)} SET {q("video_embed_url")} = %s '
                    f'WHERE {q("video_embed_url")} IS NULL',
                    [''],
                )
                cursor.execute(
                    f'ALTER TABLE {q(table)} ALTER COLUMN {q("video_embed_url")} '
                    "SET DEFAULT ''"
                )
            else:
                cursor.execute(
                    f'ALTER TABLE {q(table)} ADD COLUMN {q("video_embed_url")} '
                    'VARCHAR(500) NOT NULL DEFAULT %s',
                    [''],
                )
        return

    try:
        schema_editor.add_field(Review, field)
    except OperationalError as err:
        if 'duplicate column' not in str(err).lower():
            raise


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0044_review_rating'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='review',
                    name='video_embed_url',
                    field=models.URLField(
                        blank=True,
                        default='',
                        help_text=(
                            'Optional YouTube/Vimeo embed URL — leave blank '
                            'for text-only testimonials.'
                        ),
                        max_length=500,
                        verbose_name='Video embed URL',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    forwards_review_video_embed_url,
                    migrations.RunPython.noop,
                ),
            ],
        ),
    ]
