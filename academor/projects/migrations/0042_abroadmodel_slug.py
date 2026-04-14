# Slug for AbroadModel (from AZ name via data migration; unique URLs)

from django.db import migrations, models
from django.utils.text import slugify
from unidecode import unidecode


def populate_abroad_slugs(apps, schema_editor):
    AbroadModel = apps.get_model('projects', 'AbroadModel')
    for obj in AbroadModel.objects.order_by('id'):
        source = (obj.name_az or obj.name_en or obj.name_ru or '').strip()
        if not source:
            base = f'abroad-{obj.pk}'
        else:
            base = slugify(unidecode(source)) or f'abroad-{obj.pk}'
        slug = base
        num = 1
        while AbroadModel.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
            slug = f'{base}-{num}'
            num += 1
        obj.slug = slug
        obj.save(update_fields=['slug'])


def _drop_postgresql_abroadmodel_slug_constraints_and_indexes(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != 'postgresql':
        return
    qn = connection.ops.quote_name
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT c.conname
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            WHERE t.relname = 'projects_abroadmodel'
              AND pg_table_is_visible(t.oid)
              AND c.contype = 'u'
              AND array_length(c.conkey, 1) = 1
              AND (
                  SELECT a.attname
                  FROM pg_attribute a
                  WHERE a.attrelid = c.conrelid
                    AND a.attnum = c.conkey[1]
                    AND NOT a.attisdropped
              ) = 'slug'
            """
        )
        for (conname,) in cursor.fetchall():
            cursor.execute(
                'ALTER TABLE projects_abroadmodel DROP CONSTRAINT IF EXISTS %s' % qn(conname)
            )

        cursor.execute(
            """
            SELECT n.nspname, c.relname
            FROM pg_index i
            JOIN pg_class tbl ON tbl.oid = i.indrelid
            JOIN pg_class c ON c.oid = i.indexrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE tbl.relname = 'projects_abroadmodel'
              AND pg_table_is_visible(tbl.oid)
              AND NOT i.indisprimary
              AND c.relname::text LIKE %s
            """,
            ['%slug%'],
        )
        for schema, iname in cursor.fetchall():
            if schema == 'public':
                cursor.execute('DROP INDEX IF EXISTS %s' % qn(iname))
            else:
                cursor.execute(
                    'DROP INDEX IF EXISTS %s.%s' % (qn(schema), qn(iname))
                )


def _database_set_slug_unique(apps, schema_editor):
    """PostgreSQL: never use schema_editor AlterField for slug unique — it creates a second
    pattern opclass index (*_like) that collides after partial/failed runs. Use one btree only.
    Other DBs: normal AlterField via schema_editor.
    """
    connection = schema_editor.connection
    if connection.vendor == 'postgresql':
        _drop_postgresql_abroadmodel_slug_constraints_and_indexes(apps, schema_editor)
        # Known name from Django's PostgreSQL backend for this field (failed deploys leave it).
        with connection.cursor() as cursor:
            cursor.execute(
                'DROP INDEX IF EXISTS projects_abroadmodel_slug_ce430fac_like'
            )
            cursor.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS projects_abroadmodel_slug_key
                ON projects_abroadmodel (slug)
                """
            )
        return

    Model = apps.get_model('projects', 'AbroadModel')
    old_field = models.SlugField(blank=True, max_length=255, verbose_name='Slug')
    old_field.set_attributes_from_name('slug')
    new_field = models.SlugField(
        blank=True, max_length=255, unique=True, verbose_name='Slug'
    )
    new_field.set_attributes_from_name('slug')
    schema_editor.alter_field(Model, old_field, new_field)


def _database_set_slug_unique_reverse(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute('DROP INDEX IF EXISTS projects_abroadmodel_slug_key')
        return
    Model = apps.get_model('projects', 'AbroadModel')
    old_field = models.SlugField(blank=True, max_length=255, verbose_name='Slug')
    old_field.set_attributes_from_name('slug')
    new_field = models.SlugField(
        blank=True, max_length=255, unique=True, verbose_name='Slug'
    )
    new_field.set_attributes_from_name('slug')
    schema_editor.alter_field(Model, new_field, old_field)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0041_remove_heroslide'),
    ]

    operations = [
        migrations.AddField(
            model_name='abroadmodel',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, verbose_name='Slug'),
        ),
        migrations.RunPython(populate_abroad_slugs, migrations.RunPython.noop),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='abroadmodel',
                    name='slug',
                    field=models.SlugField(
                        blank=True,
                        max_length=255,
                        unique=True,
                        verbose_name='Slug',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    _database_set_slug_unique,
                    _database_set_slug_unique_reverse,
                ),
            ],
        ),
    ]
