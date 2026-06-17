from django.db import migrations


def _sale_columns(schema_editor):
    table = 'projects_sale'
    with schema_editor.connection.cursor() as cursor:
        return {
            col.name
            for col in schema_editor.connection.introspection.get_table_description(
                cursor, table
            )
        }


def merge_is_visible_into_show_on_homepage(apps, schema_editor):
    columns = _sale_columns(schema_editor)
    if 'is_visible' not in columns:
        return

    if 'show_on_homepage' not in columns:
        schema_editor.execute(
            'ALTER TABLE projects_sale '
            'RENAME COLUMN is_visible TO show_on_homepage'
        )
        return

    schema_editor.execute(
        'UPDATE projects_sale '
        'SET show_on_homepage = is_visible '
        'WHERE is_visible IS TRUE AND show_on_homepage IS NOT TRUE'
    )
    schema_editor.execute('ALTER TABLE projects_sale DROP COLUMN is_visible')


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_sale_show_on_homepage'),
    ]

    operations = [
        migrations.RunPython(
            merge_is_visible_into_show_on_homepage,
            migrations.RunPython.noop,
        ),
    ]
