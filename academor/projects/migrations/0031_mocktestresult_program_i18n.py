from django.db import migrations


class Migration(migrations.Migration):
    """
    Bring DB columns in sync when 0030 was applied before program_* fields
    were added to the migration file.
    Safe for both old DBs (missing columns) and fresh installs (columns exist).
    """

    dependencies = [
        ('projects', '0030_mocktestresult'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE projects_mocktestresult
                            ADD COLUMN IF NOT EXISTS program_az varchar(200) NOT NULL DEFAULT '';
                        ALTER TABLE projects_mocktestresult
                            ALTER COLUMN program_az DROP DEFAULT;

                        ALTER TABLE projects_mocktestresult
                            ADD COLUMN IF NOT EXISTS program_en varchar(200) NOT NULL DEFAULT '';
                        ALTER TABLE projects_mocktestresult
                            ALTER COLUMN program_en DROP DEFAULT;

                        ALTER TABLE projects_mocktestresult
                            ADD COLUMN IF NOT EXISTS program_ru varchar(200) NOT NULL DEFAULT '';
                        ALTER TABLE projects_mocktestresult
                            ALTER COLUMN program_ru DROP DEFAULT;

                        ALTER TABLE projects_mocktestresult
                            DROP COLUMN IF EXISTS program_id;
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
    ]
