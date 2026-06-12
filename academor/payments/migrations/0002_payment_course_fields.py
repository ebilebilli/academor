import django.db.models.deletion
from django.db import migrations, models


def _payment_column_names(schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = CURRENT_SCHEMA()
              AND table_name = 'payments_payment'
            """
        )
        return {row[0] for row in cursor.fetchall()}


def add_payment_course_fields(apps, schema_editor):
    """Idempotent — safe when columns were added manually or by a prior deploy."""
    existing = _payment_column_names(schema_editor)
    Payment = apps.get_model('payments', 'Payment')
    table = Payment._meta.db_table

    statements = []
    if 'product_type' not in existing:
        statements.append(
            f"ALTER TABLE {table} "
            "ADD COLUMN product_type varchar(20) NOT NULL DEFAULT 'generic'"
        )
    if 'buyer_email' not in existing:
        statements.append(
            f"ALTER TABLE {table} "
            "ADD COLUMN buyer_email varchar(254) NOT NULL DEFAULT ''"
        )
    if 'buyer_name' not in existing:
        statements.append(
            f"ALTER TABLE {table} "
            "ADD COLUMN buyer_name varchar(255) NOT NULL DEFAULT ''"
        )
    if 'buyer_phone' not in existing:
        statements.append(
            f"ALTER TABLE {table} "
            "ADD COLUMN buyer_phone varchar(30) NOT NULL DEFAULT ''"
        )
    if 'enrollment_completed_at' not in existing:
        statements.append(
            f"ALTER TABLE {table} "
            "ADD COLUMN enrollment_completed_at timestamp with time zone NULL"
        )
    if 'course_id' not in existing:
        statements.append(
            f"ALTER TABLE {table} "
            "ADD COLUMN course_id bigint NULL "
            "REFERENCES projects_service(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED"
        )
    if 'price_package_id' not in existing:
        statements.append(
            f"ALTER TABLE {table} "
            "ADD COLUMN price_package_id bigint NULL "
            "REFERENCES projects_coursepricepackage(id) ON DELETE SET NULL "
            "DEFERRABLE INITIALLY DEFERRED"
        )

    with schema_editor.connection.cursor() as cursor:
        for sql in statements:
            cursor.execute(sql)

    index_statements = []
    if 'product_type' not in existing:
        index_statements.append(
            f"CREATE INDEX IF NOT EXISTS payments_payment_product_type_0887f9f1 "
            f"ON {table} (product_type)"
        )
    if 'course_id' not in existing:
        index_statements.append(
            f"CREATE INDEX IF NOT EXISTS payments_payment_course_id_7f0a1e2a "
            f"ON {table} (course_id)"
        )
    if 'price_package_id' not in existing:
        index_statements.append(
            f"CREATE INDEX IF NOT EXISTS payments_payment_price_package_id_0c2b8b0d "
            f"ON {table} (price_package_id)"
        )

    with schema_editor.connection.cursor() as cursor:
        for sql in index_statements:
            cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='payment',
                    name='product_type',
                    field=models.CharField(
                        choices=[('course', 'Course'), ('generic', 'Generic')],
                        db_index=True,
                        default='generic',
                        max_length=20,
                    ),
                ),
                migrations.AddField(
                    model_name='payment',
                    name='buyer_email',
                    field=models.EmailField(blank=True, default='', max_length=254),
                ),
                migrations.AddField(
                    model_name='payment',
                    name='buyer_name',
                    field=models.CharField(blank=True, default='', max_length=255),
                ),
                migrations.AddField(
                    model_name='payment',
                    name='buyer_phone',
                    field=models.CharField(blank=True, default='', max_length=30),
                ),
                migrations.AddField(
                    model_name='payment',
                    name='enrollment_completed_at',
                    field=models.DateTimeField(blank=True, null=True),
                ),
                migrations.AddField(
                    model_name='payment',
                    name='course',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='payments',
                        to='projects.service',
                        verbose_name='Course',
                    ),
                ),
                migrations.AddField(
                    model_name='payment',
                    name='price_package',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='payments',
                        to='projects.coursepricepackage',
                        verbose_name='Price package',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(add_payment_course_fields, migrations.RunPython.noop),
            ],
        ),
    ]
