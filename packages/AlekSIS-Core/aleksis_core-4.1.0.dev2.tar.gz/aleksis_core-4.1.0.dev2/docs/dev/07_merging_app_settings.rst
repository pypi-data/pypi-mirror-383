Merging of app settings
=======================

AlekSIS provides features to merge app settings into main ``settings.py``.

Third-party apps can only add values to some select existing settings.
Official apps (those under the ``aleksis.apps.`` namespace) can mark any
setting for overriding.

Currently mergable settings
---------------------------

The following settings can be amended by any app:

 * INSTALLED_APPS
 * DATABASES
 * YARN_INSTALLED_APPS
 * ANY_JS

If you want to add another database for your AlekSIS app, you have to add
the following into your ``settings.py``::

    DATABASES = {
        "database": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "database",
            "USER": "database",
            "PASSWORD": "Y0urV3ryR4nd0mP4ssw0rd",
            "HOST": "127.0.0.1",
            "PORT": 5432,
        }
    }

Overriding any setting
----------------------

Official apps only (currently) can override any setting, but need to explicitly
mark it by listing it in a list called ``overrides`` in their ``settings.py``::

    PAYMENT_MODEL = "tezor.Invoice"

    overrides = ["PAYMENT_MODEL"]
