AlekSIS (School Information System) — Core (Core functionality and app framework)
=================================================================================

This is the core of the AlekSIS framework and the official distribution
(see below). It bundles functionality for all apps, and utilities for
developers and administrators.

If you are looking for the AlekSIS standard distribution, i.e. the complete
software product ready for installation and usage, please visit the `AlekSIS®`_
website or the distribution repository on `EduGit`_.

Features
--------

The AlekSIS core currently provides the following features:

* For users:

 * Authentication via local account, LDAP, or social accounts
 * Two factor authentication via WebAuthn, OTP, or SMS
 * Configurable dashboard with widgets
 * User-specific preferences
 * Global search
 * Global calendar system
 * CalDAV and CardDAV support
 * Manage personal events
 * Manage persons
 * Manage groups and group types
 * Manage roles per group
 * Manage announcements
 * Manage holidays
 * Notifications via SMS, email, or dashboard
 * PWA with offline caching
 * User registration, password changes and password reset
 * User invitations with invite codes and targeted invites

* For admins

 * `aleksis-admin` script to wrap django-admin with pre-configured settings
 * Manage school terms
 * Custom menu entries (e.g. in footer)
 * Automatic backup of database, static and media files
 * OAuth2 and OpenID Connect provider support
 * Serve prometheus metrics
 * System health and data checks
 * Configuration of low-level settings via configuration files
 * System-wide preferenes
 * Creating dashboard widgets for external links/apps

* For developers

 * Generic PDF generation with firefox
 * Caching with Valkey
 * Django REST framework for apps to use at own discretion
 * Injection of fields, methods, permissions and properties via custom ``ExtensibleModel``
 * K8s compatible, read-only Docker image
 * Object-level permissions and rules with ``django-guardian`` and ``django-rules``
 * uWSGI and Celery via ``django-uwsgi`` in development
 * Extensible dashbaord widget system
 * Extensible calendar system
 * Extensible OAuth/OpenID Connect scope and claims system

Licence
-------

::

  Copyright © 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024 Jonathan Weth <dev@jonathanweth.de>
  Copyright © 2017, 2018, 2019, 2020 Frank Poetzsch-Heffter <p-h@katharineum.de>
  Copyright © 2018, 2019, 2020, 2021, 2022, 2023, 2024 Hangzhi Yu <yuha@katharineum.de>
  Copyright © 2018, 2019, 2020, 2021, 2022, 2023, 2024 Julian Leucker <leuckeju@katharineum.de>
  Copyright © 2019, 2020, 2021, 2022, 2023, 2024, 2025 Dominik George <dominik.george@teckids.org>
  Copyright © 2019, 2020, 2021, 2022 Tom Teichler <tom.teichler@teckids.org>
  Copyright © 2019 mirabilos <thorsten.glaser@teckids.org>
  Copyright © 2021, 2022, 2023, 2024 magicfelix <felix@felix-zauberer.de>
  Copyright © 2021 Lloyd Meins <meinsll@katharineum.de>
  Copyright © 2022 Benedict Suska <benedict.suska@teckids.org>
  Copyright © 2022, 2023, 2024 Lukas Weichelt <lukas.weichelt@teckids.org>
  Copyright © 2023, 2024 Michael Bauer <michael-bauer@posteo.de>
  Copyright © 2024 Jonathan Krüger <jonathan.krueger@teckids.org>

  Licenced under the EUPL, version 1.2 or later, by Teckids e.V. (Bonn, Germany).

Please see the LICENCE.rst file accompanying this distribution for the
full licence text or on the `European Union Public Licence`_ website
https://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers
(including all other official language versions).

Trademark
---------

AlekSIS® is a registered trademark of the AlekSIS open source project, represented
by Teckids e.V. Please refer to the `trademark policy`_ for hints on using the trademark
AlekSIS®.

.. _AlekSIS®: https://aleksis.org
.. _European Union Public Licence: https://eupl.eu/
.. _EduGit: https://edugit.org/AlekSIS/official/AlekSIS
.. _trademark policy: https://aleksis.org/pages/about
