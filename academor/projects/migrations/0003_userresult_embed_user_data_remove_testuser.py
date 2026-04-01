# Generated manually on 2026-04-02

from django.db import migrations, models


def copy_test_user_into_result(apps, schema_editor):
    UserResult = apps.get_model("projects", "UserResult")
    TestUser = apps.get_model("projects", "TestUser")

    # If there is no data yet, do nothing quickly.
    # We use iterator() to avoid loading everything into memory.
    for result in UserResult.objects.select_related("test_user").iterator():
        tu = getattr(result, "test_user", None)
        if not tu:
            continue
        UserResult.objects.filter(pk=result.pk).update(
            first_name=tu.first_name,
            last_name=tu.last_name,
            number=tu.number,
            email=tu.email,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0002_alter_about_options_alter_contact_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userresult",
            name="first_name",
            field=models.CharField(max_length=100, null=True, blank=True, verbose_name="First name"),
        ),
        migrations.AddField(
            model_name="userresult",
            name="last_name",
            field=models.CharField(max_length=100, null=True, blank=True, verbose_name="Last name"),
        ),
        migrations.AddField(
            model_name="userresult",
            name="number",
            field=models.CharField(max_length=30, null=True, blank=True, verbose_name="Phone number"),
        ),
        migrations.AddField(
            model_name="userresult",
            name="email",
            field=models.EmailField(max_length=254, null=True, blank=True, verbose_name="Email"),
        ),
        migrations.RunPython(copy_test_user_into_result, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="userresult",
            name="test_user",
        ),
        migrations.DeleteModel(
            name="TestUser",
        ),
    ]

