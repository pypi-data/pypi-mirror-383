Managing your personal account
==============================

Each logged in user has several options to provided through the AlekSIS
core. Which of these items are display depends on whether the user has a
person and what your system administrator has configured. All of the functionality
listed below (except of the notification menu) can be accessed via the account
menu that is shown when clicking the own avatar on the right of the app bar.

.. _core-notifications:

Notifications
-------------

.. image:: ../_static/notifications.png
  :width: 100%
  :alt: Notifications menu

The AlekSIS core has a built-in notification system which can be used by
apps to send urgent information to specific persons (e. g. timetable
changes). Notifications are shown in the notifications menu reachable by the
bell icon in the app bar. In addition to that, notifications can be sent to
users through several communication channels. These channels can be switched
on or off in your personal preferences (cf. :ref:`core-user-preferences`).

Notifications can be marked as read using the mail button on the item's right
side.

.. _core-2fa:

Setup two-factor authentication
-------------------------------

.. image:: ../_static/2fa_disabled.png
  :width: 100%
  :alt: Two factor authentication page with 2FA disabled

AlekSIS provides two factor authentication using authenticator apps/
code generators supporting TOTP and/or security keys supporting FIDO U2F.

To configure a second factor, visit ``Account menu → 2FA`` and follow the
instructions.

Please keep the recovery codes somewhere safe so you do not lose access to
your account. If you are unable to login with two factor authentication,
please contact your site administrator.

If you forget to safe your recovery codes, but you are still logged in, visit
``Account menu → 2FA``, and click ``Show codes``` in order to view the recovery codes.

To disable two factor authentication, login to your account and navigate to
``Account menu → 2FA``, then you can deactivate all authentication methods.

.. image:: ../_static/2fa_enabled.png
  :width: 100%
  :alt: Two factor authentication page with 2FA enabled

.. _core-change-password:

Change password
---------------

.. image:: ../_static/change_password.png
  :width: 100%
  :alt: Change password page

If your system administrator has activated this function, you can change
your password via ``Account menu → Change password``. If you forgot your
password, there is a link ``Password forgotten?`` on this page which
helps with resetting your password. The system then will send you a
password reset link via email.

.. _core-me-page:

Me page
-------

.. image:: ../_static/about_me_page.png
  :width: 100%
  :alt: About me page

Reachable under ``Account menu → Account``, this page shows the personal
information saved about you in the system. If activated, you can upload
a picture of yourself or edit some information using the ``Edit`` button.

Apps can extend the information shown on this page by adding widgets displaying
other personal data, such as coursebook statistics or absences.

.. _core-user-preferences:

Personal preferences
--------------------

You can configure some behavior using the preferences under
``Account menu → Preferences``. By default, the Core only provides some
preferences, but apps can extend this list. You can find further
information about such preferences in the chapter of the respective
apps.

-  **Notifications**

   -  **Name format for addressing**: Here you can select how AlekSIS
      should address you.
   -  **Channels to use for notifications:** This channel is used to
      sent notifications to you (cf. :ref:`core-notifications`).

-  **Calendar**

   -  **First day that appears in the calendar**: Here you can select
      first weekday that is shown in the calendar frontend.
   -  **Activated calendars**: These calendars are shown in the calendar
      select list in the calendar frontend.

.. _core-third-party-accounts:

Third-party accounts
--------------------

If you logged in using a third-party account (e. g. a Google or
Microsoft account), you can manage the connections to these accounts on
the page ``Account menu → Third-party accounts``.

The feature to use third-party accounts needs to be enabled by
an administrator, as described in :doc:`../admin/23_socialaccounts`.

.. _core-authorized-applications:

Authorized third-party applications
-----------------------

On the page ``Account menu → Third-party applications`` you can see all
external applications you authorized to retrieve data about you from
AlekSIS. That can be services provided by your local institution like a
chat platform, for example.

For each third-party application, you can see the personal information it
has access to. Additionally, you may revoke its access.
