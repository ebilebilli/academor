from django.db import migrations

from projects.lucky_wheel_defaults import DEFAULT_LUCKY_WHEEL_PRIZES


def replace_default_prizes(apps, schema_editor):
    Prize = apps.get_model("projects", "LuckyWheelPrize")
    Spin = apps.get_model("projects", "LuckyWheelSpin")

    used_ids = set(Spin.objects.values_list("prize_id", flat=True))
    Prize.objects.exclude(pk__in=used_ids).delete()
    if used_ids:
        Prize.objects.filter(pk__in=used_ids).update(is_active=False)

    Prize.objects.bulk_create(
        [
            Prize(is_active=True, code="", **row)
            for row in DEFAULT_LUCKY_WHEEL_PRIZES
        ]
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0035_lucky_wheel_default_prizes"),
    ]

    operations = [
        migrations.RunPython(replace_default_prizes, noop_reverse),
    ]
