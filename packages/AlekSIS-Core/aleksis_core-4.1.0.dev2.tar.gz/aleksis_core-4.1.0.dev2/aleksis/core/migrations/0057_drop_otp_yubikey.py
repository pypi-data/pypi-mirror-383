from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0056_rename_customevent_personalevent"),
    ]

    operations = [
        migrations.RunSQL(
            "; ".join(
                f"drop table if exists {x} cascade;" for x in [
                    "otp_yubikey_remoteyubikeydevice",
                    "otp_yubikey_validationservice",
                    "otp_yubikey_remoteyubikeydevice"
                ]
            )
        )
    ]
