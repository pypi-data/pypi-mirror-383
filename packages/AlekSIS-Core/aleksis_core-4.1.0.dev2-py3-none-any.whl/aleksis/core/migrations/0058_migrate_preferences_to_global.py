from django.db import migrations


def forwards_func(apps, schema_editor):
    SitePreferenceModel = apps.get_model("core", "SitePreferenceModel")
    GlobalPreferenceModel = apps.get_model("dynamic_preferences", "GlobalPreferenceModel")
    db_alias = schema_editor.connection.alias
    for pref in SitePreferenceModel.objects.using(db_alias):
        GlobalPreferenceModel.objects.update_or_create(section=pref.section, name=pref.name, defaults=dict(raw_value=pref.raw_value))


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0057_drop_otp_yubikey"),
        ("dynamic_preferences", "0006_auto_20191001_2236")
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
