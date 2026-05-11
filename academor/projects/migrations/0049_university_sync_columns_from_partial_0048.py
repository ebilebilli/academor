"""
Repair DBs where an older 0048 added only part of the University fields.

If 0048 was applied when it only added `name` (and optionally `abroad_item`), the
migration is recorded as applied while `slug`, `description`, and `study_abroad`
columns are missing. This migration adds any missing columns and copies
`abroad_item_id` into `study_abroad_id` before dropping the legacy column.
"""

from django.db import migrations


def _table_columns(cursor, table_name: str, vendor: str) -> set[str]:
    if vendor == 'postgresql':
        cursor.execute(
            """
            SELECT a.attname
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE n.nspname = current_schema()
              AND c.relname = %s
              AND a.attnum > 0
              AND NOT a.attisdropped
            """,
            [table_name],
        )
        return {row[0] for row in cursor.fetchall()}
    if vendor == 'sqlite':
        if not table_name.isidentifier():
            return set()
        cursor.execute('PRAGMA table_info(%s)' % table_name)
        return {row[1] for row in cursor.fetchall()}
    return set()


def sync_university_columns(apps, schema_editor):
    connection = schema_editor.connection
    vendor = connection.vendor
    table = 'projects_university'

    if vendor not in ('postgresql', 'sqlite'):
        return

    with connection.cursor() as cursor:
        cols = _table_columns(cursor, table, vendor)

        if 'slug' not in cols:
            cursor.execute(
                'ALTER TABLE projects_university ADD COLUMN slug varchar(150) NULL'
            )

        cols = _table_columns(cursor, table, vendor)
        if 'description' not in cols:
            cursor.execute(
                'ALTER TABLE projects_university ADD COLUMN description text NULL'
            )

        cols = _table_columns(cursor, table, vendor)
        if 'study_abroad_id' not in cols:
            if vendor == 'postgresql':
                cursor.execute(
                    """
                    ALTER TABLE projects_university
                    ADD COLUMN study_abroad_id bigint NULL
                    REFERENCES projects_abroadmodel (id)
                    ON DELETE SET NULL
                    """
                )
            else:
                cursor.execute(
                    """
                    ALTER TABLE projects_university
                    ADD COLUMN study_abroad_id bigint NULL
                    REFERENCES projects_abroadmodel (id)
                    ON DELETE SET NULL
                    """
                )

        cols = _table_columns(cursor, table, vendor)
        if 'abroad_item_id' in cols and 'study_abroad_id' in cols:
            cursor.execute(
                """
                UPDATE projects_university
                SET study_abroad_id = abroad_item_id
                WHERE abroad_item_id IS NOT NULL
                  AND study_abroad_id IS NULL
                """
            )

        cols = _table_columns(cursor, table, vendor)
        if 'abroad_item_id' in cols:
            if vendor == 'postgresql':
                cursor.execute(
                    'ALTER TABLE projects_university DROP COLUMN IF EXISTS abroad_item_id'
                )
            else:
                cursor.execute(
                    'ALTER TABLE projects_university DROP COLUMN abroad_item_id'
                )

        if vendor == 'postgresql':
            cursor.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint
                        WHERE conname = 'projects_university_slug_key'
                    ) THEN
                        ALTER TABLE projects_university
                        ADD CONSTRAINT projects_university_slug_key UNIQUE (slug);
                    END IF;
                END $$;
                """
            )


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0048_university_name_abroad_item'),
    ]

    operations = [
        migrations.RunPython(sync_university_columns, migrations.RunPython.noop),
    ]
