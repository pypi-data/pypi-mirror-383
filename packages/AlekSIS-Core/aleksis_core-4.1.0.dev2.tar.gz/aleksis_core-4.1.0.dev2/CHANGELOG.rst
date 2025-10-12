Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.

Unreleased
----------

Notable, breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~

* The dashboard has been rebuilt within the new Vue frontend. As a result, all apps with widgets must
  be updated accordingly. Installing AlekSIS apps that still use legacy dashboard widgets will cause
  the dashboard to break.
* The library for the 2FA was replaced so all accounts with configured 2FA will habe to reconfigure
  their 2FA methods. There is support for TOTP, recovery codes, and Webautn.
* Django backend administration (django-admin) has been removed.
* [Dev] `ExtensibleModel` now has a `uuid` field, requiring migrations to be created for all
  AlekSIS models.
* [Dev] Celery progress tracking was updated and needs changes if ``recorded_task`` is used.

Added
~~~~~

* Availability events feed indicating persons' free/busy status.
* Free/busy feed aggregating all events that explicitly set a person's or a group's availability status.
* [Dev] Introduce a RoomField analog to other similar fields.
* [Dev] All AlekSIS models now have a UUID
* Introduce availability types linked to availability events.
* Attendees of personal events are now provided via CalDAV.
* With the correct permissions, it's now possible to change/reset passwords for other users.
* vCards of persons now contain related persons.
* [Dev] Add a CalendarFeedField.
* [Dev] There are two new rules for frontend fields: isGreaterAndNotSameThan and isSmallerAndNotSameThan.
* [Dev] Introduce a Todo base model.
* Introduce personal todos.
* [Dev] Add a PositiveFloatField analog to PositiveSmallIntegerField.
* Add button that marks all notifications as read
* A configurable email contact will be notified on account registrations.
* [Dev] Support client credentials authentication for Django REST Framework
  views
* Support global announcements for all persons.
* [Dev] Allow `from_object_uri` to parse ObjectAuthenticator URIs (e.g. for NFC-SDM)
* [Dev] Generate Data Matrix codes for objects
* [Dev] OAuth2ClientAuthentication and ClientProtectedResourcePermission now support user tokens.
* Relationships like group memberships and person relationships now have an optional start and end date.

Changed
~~~~~~~

* Dashboard has been migrated to a new, interactive one.
* Announcements are shown in calendar and as banner on top of all pages.
* Persons now get notified about announcements.
* All HTTP requests are now encapsulated in a database transaction.
* DialogObjectForm is now slightly wider.
* [Dev] DialogObjectForm now implicitly handles a missing ``isCreate`` prop depending on the presence of ``editItem``.
* [Dev] DeleteDialog supports the activator slot now.
* The account registration and invitation code forms were migrated to the new frontend.
* Following administration views were migrated to new frontend:

  * System status
  * Data checks

* Allow limiting page numbers in PDF generation.
* vCards contain a link to the AlekSIS person object.
* Views for changing and resetting passwords were migrated to new frontend.
* [Dev] The ObjectForm bottom aligns its rows now.
* [CardDAV] Accept header and vCard version specified in REPORT query are respected.
* [Dev] Ensure `from_object_uri` returns expected model

Fixed
~~~~~

* Buttons in some dialogs were missing space between.
* [Dev] Dialog-Object-Form's internal dialog-mode-handling did not implement opening via activator slot.
* [Dev] MutateMixin could not be used for affected queries without variables.
* [Dev] RecurrenceField did error if an empty date was input.
* [Dev] InlineCRUDList broke with DialogObjectForm implicitly handling undefined ``isCreate``.
* Celery polling did not decrease frequency after all tasks have been finished.
* The person edit form guardians field did not show existing guardians.
* Filtering persons caused an error.
* Impersonation did not work.
* Fix Sentry integration to work with frontend and backend.
* After accessing forbidden page, redirect to page on successful login.
* Fix DAV endpoint for single objects.
* End datetimes passed to the calendar events query were not respected.
* [Dev] Do not exhaust PostgreSQL max_connections in development
* Editing managed objects was possible in inline lists.
* PDF generation took very long due to not properly closed selenium sessions
* [CalDAV] calendar-multiget returned more objects than requested.
* [DAV] Clients always refetched events due to changing DTSTAMP causing unstable ETags.
* [Dev] The ``versions`` property of ``ExtendedModel`` failed when parent versions were missing.
* When reloading, some calendar events became displayed multiple times.

Removed
~~~~~~~

* [Dev] ``render_progress_page`` has been removed.

`4.0.4`_ - 2025-07-29
---------------------

Fixed
~~~~~

* Fix incompatibility with newer `django-allauth` that made AlekSIS-Core not installable.

`4.0.3`_ - 2025-06-11
---------------------

Fixed
~~~~~

* [Dev] `get_single_events` didn't expand events by default.

`4.0.2`_ - 2025-05-21
---------------------

Added
~~~~~

* [Dev] Celery progress component for including in own pages (base for celery progress page).

`4.0.1`_ - 2025-04-16
---------------------

Fixed
~~~~~

* It wasn't possible to run data checks due to broken color data checks.
* Recurrence information for calendar events weren't removed on deletion.
* Full day events didn't work in calendar.
* Recurring events without until value weren't shown.
* [Dev] AddressInputType missed country field.
* Detail pages, e.g. for groups, did not work anymore.
* The configured theme colors were not used by the frontend.
* It wasn't possible to change icons of OAuth applications in the frontend.
* First fetching of calendar feeds logged an error to console.

`4.0.0`_ - 2025-03-29
-------------------

Notable, breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~

The special assignment page for groups and child groups has been removed.

For the calendar system, AlekSIS now needs an extension for the PostgreSQL database.
Please check the docs for instructions how to setup the ``pg_rrule`` extension
for PostgreSQL.

AlekSIS now uses Valkey as a drop-in replacement for Redis. Please update your configuration
files accordingly (see docs for further instructions).

To make setting names consistent, the setting ``auth.login.registration.unique_email``
was renamed to ``auth.registration.unique_email``.

The "additional fields" feature has been removed because it had design issues
that practically made it unusable in all scenarios. No migration path away
from the feature is defined. If you have been using additional group fields
and need a replacement, please contact the development team.

The "managed models" feature is mandatory for all models derived from `ExtensibleModel`
and requires creating a migration for all downstream models to add the respective field.

As legacy pages are no longer themed, you should update them to the new frontend as soon as possible.

To prevent collisions with fields, the class variable ``name`` on ``RegistryObject`` has been renamed
to ``_class_name``. Please update any references and subclasses.

Deprecated
~~~~~~~~~~

* The field ``owners`` of group will be removed in the next release and will be replaced by memberships
  using the special ownership role.

Added
~~~~~

* Global calendar system

  * CalDAV and CardDAV for syncing calendars and Persons read-only.
  * Calendar for birthdays of persons
  * Management of personal calendar events.
  * Holiday model to track information about holidays.

* Following management views were added:

  * Rooms
  * Holiday

* Global school term select for limiting data to a specific school term.
* Error message when loading in incompatible browser
* Tooltips for every information in the person page
* New menu item "Data management" with Rooms, Announcements, Holidays, and School Terms
* Priority to sort announcements
* Generic Roles for describing relationships. Currently used for Person-to-Group relationships.
* Mascot images in multiple places throughout the application.
* Generic endpoint for retrieving objects as JSON
* Add option to disallow reserved usernames.
* Allow matching social accounts to local accounts by their username.
* Support RP-initiated logout for OIDC applications
* Support native PostgreSQL connection pooling
* Support profiling with Sentry in addition to tracing
* Introduce .well-known urlpatterns for apps
* [Dev] Views can request to span the entire screen width.
* [Dev] Base model for organisational entities (external companies, associations,…)
* [Dev] Support running of data checks before/after migrations.
* [Dev] Notifications based on calendar alarms.
* [Dev] Components for implementing standard CRUD operations in new frontend.
* [Dev] Options for filtering and sorting of GraphQL queries at the server.
* [Dev] Managed models for instances handled by other apps.
* [Dev] Upload slot sytem for out-of-band uploads in GraphQL clients

Changed
~~~~~~~

* Following management views were migrated to new frontend:

  * School Terms
  * Announcements
  * OAuth Applications
  * Persons

* Content width on different screen sizes is more consistent.
* Room model icon changed from the default to a specific one.
* Show only short name, if available, in announcement recipients
* Move "Invite person" to persons page
* Show avatars of groups in all places.
* Use new auth rate limiting settings
* Factor out addresses in their own model and allow multiple addresses with different types
  (e. g. home, business) for one person
* Setting ``auth.login.registration.unique_email`` was renamed to ``auth.registration.unique_email``
* Adapt permission scheme for announcements to other permissions.
* Use Firefox instead of Chromium for PDF creation and support external webdriver via
  `selenium.url` option, e.g. for use in containers.
* Replace all mentions of Redis with Valkey where possible
* [Dev] Rename `RegistryObject`'s class var `name` to `_class_name`.
* [Dev] Use Django 5.
* [Dev] Bump Python version to 3.10
* [Dev] Child groups are exposed in the GraphQL type for groups.

Fixed
~~~~~

* Accessibility issues with new frontend.
* Improve error handling in frontend and show meaningful error messages.
* GraphQL mutations did not return errors in case of exceptions.
* Make email field unique over all persons.
* Opening group details wasn't possible without permissions for all person details.
* Correctly redirect to AlekSIS frontend after login with a third-party account.
* Our own account adapter wasn't used so signup settings weren't applied correctly.
* Setting images for groups did not work
* Update and fix URLs for 3rdparty login.
* The OpenID Connect Discovery endpoint now returns the issuer data directly
  under the URI without a trailing `/`.
* Not-logged in users were able to access all PDF files (CVE-2025-25683).
* [Docs] An example config contained invalid values.
* [Container] Database backup failed with postgres versions 15 and 16.
* [Dev] Foreign keys to ExtensiblePolymorphicModel types were using the wrong manager.
* [Dev] Allow activating more frequent polling for Celery task progress.
* [Dev] Integrate model validation mechanisms into GraphQL queries.

Removed
~~~~~~~

* Yubikey support (not WebAuthn) was removed
* Additional fields.
* Legacy pages are no longer themed.
* [Dev] Batching of GraphQL queries.
* [Dev] `_recursive` methods for groups have been removed.
  Developers relying on parent groups need to account for recursion themselves.
* [Dev] Extended fields mechanism on top of django-jsonstore.

`3.2.2`_ - 2025-01-18
---------------------

Fixed
~~~~~

* Not-logged in users were able to access all PDF files (CVE-2025-25683).

`3.2.1`_ - 2024-06-27
---------------------

Fixed
~~~~~

* Synchronisation of AlekSIS and Django groups caused permissions issues
* [OIDC] Custom additional claims were not present in userinfo
* [Docs] The docker-compose method was not described detailed enough
* [Docker] Fix build of production images to include only released versions
* Third-party login buttons now directly open external login page.
* Persons could not be edited by non-superusers with global person editing permission.
* Permission checks for dashboard widget creation and person invitations were invalid
* New Persons were not added to selected primary group on creation
* In some browsers, AlekSIS was not categorised as an installable PWA.
* Announcements without any recipient had a line to display recipients
* Missing migrations for update of OAuth library


`3.2.0`_ - 2023-12-25
---------------------

Fixed
~~~~~

* Description field of Person was not editable.
* [Docs] Certain parts of installation docs not visible
* Nav submenu items could not be distinguished from regular ones.
* Group GraphQL queries failed when queried by owner or member.
* Special printouts included a blank white page at the end.
* Icons of active menu entries are filled if possible.
* Collapse icon on the progress drawer was the wrong way around.
* Deleting persons now requires confirmation.
* Editing of OAuth applications led to broken UI.
* Add missing feedback for password changing and resetting.
* Sex of a person was not translated.

Deprecated
~~~~~~~~~~

This release deprecates some features in preparation for the 4.0 release.

* Additional fields.
* Legacy Yubikey support (not WebAuthn).
* [Dev] *_recursive methods for groups. Developers relying on parent groups
  need to account for recursion themselves.
* [Dev] Extended fields mechanism on top of django-jsonstore.

`3.1.7`_ - 2025-01-18
---------------------

Fixed
~~~~~

* Not-logged in users were able to access all PDF files (CVE-2025-25683).

`3.1.6`_ - 2024-06-27
---------------------

Fixed
~~~~~

* [Docs] Certain parts of installation docs not visible
* Synchronisation of AlekSIS and Django groups caused permissions issues
* [OIDC] Custom additional claims were not present in userinfo
* [Docs] The docker-compose method was not described detailed enough
* [Docker] Fix build of production images to include only released versions
* Third-party login buttons now directly open external login page.
* Persons could not be edited by non-superusers with global person editing permission.
* Permission checks for dashboard widget creation and person invitations were invalid
* New Persons were not added to selected primary group on creation
* In some browsers, AlekSIS was not categorised as an installable PWA.
* Announcements without any recipient had a line to display recipients
* Missing migrations for update of OAuth library

`3.1.5`_ - 2023-09-02
---------------------

Fixed
~~~~~

* [Docs] A required package was not listed
* Migrations failed in some cases

`3.1.4`_ - 2023-07-20
---------------------

Fixed
~~~~~

* Extensible form was broken due to a missing import.

`3.1.3`_ – 2023-07-18
---------------------

Fixed
~~~~~

* [Docker] The build could silently continue even if frontend bundling failed, resulting
  in an incomplete AlekSIS frontend app.
* Rendering of "simple" PDF templates failed when used with S3 storage.
* Log messages on some loggers did not contain log message

`3.1.2`_ - 2023-07-05
---------------------

Changed
~~~~~~~

* uWSGI is now installed together with AlekSIS-Core per default.

Fixed
~~~~~

* Notifications were not properly shown in the frontend.
* [Dev] Log levels were not correctly propagated to all loggers
* [Dev] Log format did not contain all essential information
* When navigating from legacy to legacy page, the latter would reload once for no reason.
* The oauth authorization page was not accessible when the service worker was active.
* [Docker] Clear obsolete bundle parts when adding apps using ONBUILD
* Extensible forms that used a subset of fields did not render properly

`3.1.1`_ - 2023-07-01
---------------------

Fixed
~~~~~

* Progress page didn't work properly.
* About page failed to load for apps with an unknown licence.
* QUeries for persons with partial permissions failed.
* Some pages couldn't be scrolled when a task progress popup was open.
* Notification query failed on admin users without persons.
* Querying for notification caused unnecessary database requests.
* Loading bar didn't disappear on some pages after loading was finished.
* Support newer versions of django-oauth-toolkit.

`3.1`_ - 2023-05-30
-------------------

Changed
~~~~~~~

* The frontend is now able to display headings in the main toolbar.

Fixed
~~~~~

* Default translations from Vuetify were not loaded.
* Browser locale was not the default locale in the entire frontend.
* In some cases, items in the sidenav menu were not shown.
* The search bar in the sidenav menu was shown even though the user had no permission to see it.
* Accept invitation menu item was shown when the invitation feature was disabled.
* Metrics endpoint for Prometheus was at the wrong URL.
* Polling behavior of the whoAmI and permission queries was improved.
* Confirmation e-mail contained a wrong link.

`3.0`_ - 2023-05-11
-------------------

Added
~~~~~

* GraphQL schema for Rooms
* Provide API endpoint for system status.
* [Dev] UpdateIndicator Vue Component to display the status of interactive pages
* [Dev] DeleteDialog Vue Component to unify item deletion in the new frontend
* Use build-in mechanism in Apollo for GraphQL batch querying.


Changed
~~~~~~~

* Show message on successful logout to inform users properly.
* Phone number country now has to be configured in config file insted of frontend.

Fixed
~~~~~

* GraphQL endpoints for groups, persons, and notifications didn't expose all necessary fields.
* Loading indicator in toolbar was not shown at the complete loading progress.
* 404 page was sometimes shown while the page was still loading.
* Setting of page height in the iframe was not working correctly.
* App switched to offline state when the user was logged out/in.
* The `Stop Impersonation` button is not shown due to an oversee when changing the type of the whoAmI query to an object of UserType
* Offline fallback page for legacy pages was misleading sometimes.
* Route changes in the Legacy-Component iframe didn't trigger a scroll to the top
* Query strings did not get passed when navigating legacy pages inside of the SPA.
* Retry button on error 500 page did not trigger a reload of the page.
* When the Celery worker wasn't able to execute all tasks in time, notifications were sent multiple times.
* Changing the maintenance mode state spawned another SPA instance in the iframe
* Phone numbers couldn't be in regional format.
* System status view wasn't accessible through new frontend if a check failed.
* Progress page didn't show error message on failure.
* Dynamic routes were not removed/hidden when the respective object registering it was deleted.
* Django messages were not displayed in Vue frontend.
* Links to data check objects did not work properly.
* Backend cleanup task for Celery wasn't working.
* URLs in invitation email were broken.
* Invitation view didn't work.
* Invitation emails were using wrong styling.
* GraphQL queries and mutations did not log exceptions.

`3.0b3`_ - 2023-03-19
---------------------

Fixed
~~~~~

* Some GraphQL queries could return more data than permitted in related fields.

`3.0b2`_ - 2023-03-09
---------------------

Changed
~~~~~~~

* Change default network policy of the Apollo client to `cache-and-network`.

Fixed
~~~~~

* In case the status code of a response was not in the range between 200 and 299
  but still indicates that the response should be delivered, e. g. in the case
  of a redirected request, the service worker served the offline fallback page.
* In some cases, the resize listener for the IFrame in the `LegacyBaseTemplate`
  did not trigger.
* [Dev] Allow apps to declare URLs in the non-legacy namespace again

`3.0b1`_ - 2023-02-27
---------------------

Added
~~~~~

* Support for two factor authentication via email codes and Webauthn.

`3.0b0`_ - 2023-02-15
---------------------

This release starts a new era of the AlekSIS® framework, by introducing a
dynamic frontend app written in Vue.js which communicates with the backend
through GraphQL.  Support for legacy views (Django templates and
Materialize) was removed; while there is backwards compatibility for now,
this is only used by official apps until their views are fully migrated.

AlekSIS and its new frontend require Node.js version 18 or higher to run the
Vite bundler. On Debian, this means that Debian 12 (bookworm) is needed, or
Node.js must be installed from a third-party repository.

Removed
~~~~~~~

* Official support for views rendered server-side in Django is removed. The
  `LegacyBaseTemplate` provided for backwards compatibility must not be used
  by apps declaring a dependency on AlekSIS >= 3.0.
* Support for deploying AlekSIS in sub-URLs
* Support for production deployments without HTTPS

Deprecated
~~~~~~~~~~

* The `webpack_bundle` management command is replaced by the new `vite`
  command. The `webpack_bundle` command will be removed in AlekSIS-Core 4.0.

Added
~~~~~

* Notification drawer in top nav bar
* GraphQL queries for base system and some core data management
* [Dev] New mechanism to register classes over all apps (RegistryObject)
* Model for rooms

Changed
~~~~~~~

* Show languages in local language
* Rewrite of frontend (base template) using Vuetify
    * Frontend bundling migrated from Webpack to Vite (cf. installation docs)
    * [Dev] The runuwsgi dev server now starts a Vite dev server with HMR in the
      background
* OIDC scope "profile" now exposes the avatar instead of the official photo
* Based on Django 4.0
    * Use built-in Redis cache backend
    * Introduce PBKDF2-SHA1 password hashing
* Persistent database connections are now health-checked as to not fail
  requests
* [Dev] The undocumented field `check` on `DataCheckResult` was renamed to `data_check`
* Frontend bundling migrated from Webpack to Vite
* Get dashboard widgets and data checks from apps with new registration mechanism.
* Use write-through cache for sessions to retain on clear_cache
* Better error page with redirect option to login page when user has no permission to access a route.
* Users now can setup as many 2FA devices as they want.
* The 2FA profile overview was completely redesigned.

Fixed
~~~~~

* The system tried to send notifications for done background tasks
  in addition to tasks started in the foreground
* 2FA via messages or phone calls didn't work after a faulty dependency
  update
* [Dev] Site reference on extensible models can no longer cause name clashes
  because of its related name

Removed
~~~~~~~

* iCal feed URLs for birthdays (will be reintroduced later)
* [Dev] Django debug toolbar
    * It caused major performance issues and is not useful with the new
      frontend anymore

`2.12.3`_ - 2023-03-07
----------------------

Fixed
~~~~~

* The permission check for the dashboard edit page failed when the user had no person assigned.
* OIDC scope "phone" had no claims.
* AlekSIS groups were not synced to Django groups on registration of existing persons
* Invitations for existing short name did not work.
* Invitations for persons without pre-defined e-mail address did not behave correctly

`2.12.2`_ - 2022-12-18
----------------------

Fixed
~~~~~

* Incorporate SPDX license list for app licenses on About page because
  spdx-license-list dependency vanished.

`2.12.1`_ - 2022-11-06
----------------------

Fixed
~~~~~

* An invalid backport caused OIDC clients without PKCD to fail.

`2.12`_ - 2022-11-04
--------------------

Added
~~~~~

* Show also group ownerships on person detail page
* [Dev] Provide plain PDF template without header/footer for special layouts.
* [Dev] Introduce support for reformattinga and linting JS, Vue, and CSS files.

Changed
~~~~~~~

* OIDC scope "profile" now exposes the avatar instead of the official photo
* Language selection on Vue pages now runs via GraphQL queries.
* [Dev] Provide function to generate PDF files from fully-rendered templates.
* [Dev] Accept pre-created file object for PDF generation to define
  the redirect URL in advance.

Fixed
~~~~~

* The logo in the PDF files was displayed at the wrong position.
* Sometimes the PDF files were not generated correctly
  and images were displayed only partially.
* Error message in permission form was misleading.
* Personal invites did not work
* Invite Person view threw an error when personal invites existed
* Detailed information for done Celery tasks weren't saved.

`2.11`_ - 2022-08-27
--------------------

This release sunsets the 2.x series of the AleKSIS core.

Deprecated
~~~~~~~~~~

* All frontends using Django views and Django templates are deprecated and support
  for them will be removed in AlekSIS-Core 3.0. All frontend code must be written in
  Vue.js and be properly separated from the backend. In the same spirit, all backend
  features must expose GraphQL APIs for the frontend to use.

Added
~~~~~

The following features are introduced here mainly to simplify gradual
updates. GraphQL and the Vuetify/Vue.js frontend mechanisms are preview
functionality and app developers should not rely on them before AlekSIS-Core
3.0.

* Introduce GraphQL API and Vue.js frontend implementation
* Introduce webpack bundling for frontend code

`2.10.2`_ - 2022-08-25
----------------------

Fixed
~~~~~

* Celery's logging did not honour Django's logging level
* Automatically clean up expired OAuth tokens after 24 hourse

`2.10.1`_ - 2022-07-24
----------------------

Changed
~~~~~~~

* Make External Link Widget icons clickable

Fixed
~~~~~

* The progress page for background tasks didn't show all status messages.

`2.10`_ - 2022-06-25
--------------------

Added
~~~~~

* Add Ukrainian locale (contributed by Sergiy Gorichenko from Fre(i)e Software GmbH).
* Add third gender to gender choices
* Add DataCheck to validate specific fields of specific models

Changed
~~~~~~~

* Restructure group page and show more information about members.
* django-two-factor-auth >= 1.14.0 is now required due to a
  backwards-incompatible breakage in that library

Fixed
~~~~~~~

* Password change view did not redirect to login when accessed unauthenticated.
* Sorting icons were inlined into stylesheet
* iOS devices used the favicon instead of the PWA icon when the PWA was added to the home screen.

Changed
~~~~~~~

* Update icon choices for models to new icon set

`2.9`_ - 2022-05-25
-------------------

Added
~~~~~

* Allow to disable exception mails to admins
* Add possibility to create iCal feeds in all apps and dynamically create user-specific urls.

Fixed
~~~~~

* The menu button used to be displayed twice on smaller screens.
* The icons were loaded from external servers instead from local server.
* Weekdays were not translated if system locales were missing
    * Added locales-all to base image and note to docs
* The icons in the account menu were still the old ones.
* Due to a merge error, the once removed account menu in the sidenav appeared again.
* Scheduled notifications were shown on dashboard before time.
* Remove broken notifications menu item in favor of item next to account menu.
* Serve OAuth discovery information under root of domain
* [OAuth2] Resources which are protected with client credentials
  allowed access if no scopes were allowed (CVE-2022-29773).
* The site logo could overlap with the menu for logos with an unexpected aspect ratio.
* Some OAuth2 views stopped working with long scope names.
* Resetting password was impossible due to a missing rule
* Language selection was broken when only one language was enabled in
  preferences.

Removed
~~~~~~~

* Remove option to limit available languages in preferences.

Changed
~~~~~~~

* [Dev] ActionForm now checks permissions on objects before executing
* [Dev] ActionForm now returns a proper return value from the executed action
* Pin version of javascript dependencies

`2.8.1`_ - 2022-03-13
--------------------

Changed
~~~~~~~

* Official apps can now override any setting

`2.8`_ - 2022-03-11
-------------------

Added
~~~~~

* Add iconify icons
* Use identicons where avatars are missing.
* Display personal photos instead of avatars based on a site preference.
* Add an account menu in the top navbar.
* Create a reusable snippet for avatar content.
* Allow to configure if additional field is required
* Allow to configure description of additional fields
* Allow configuring regex for allowed usernames
* [Dev] Support scheduled notifications.
* Implement StaticContentWidget
* Allow to enable password change independently of password reset

Changed
~~~~~~~

* Added a `Retry` button to the server error page

Fixed
~~~~~

* The user handbook was lacking images and instructions on PWA usage with the Safari browser.
* The ``reset password`` button on the login site used to overflow the card on smaller devices.

Deprecated
~~~~~~~~~~

* Legacy material icon font will be removed in AlekSIS-Core 3.0

`2.7.4`_ - 2022-02-09
---------------------

Changed
~~~~~~~

* Allow disabling query caching with cachalot
* Add invitation key to success message when a person without e-mail address is invited by id

Fixed
~~~~~

* Only exactly one person without e-mail address could be invited
* No person was created and linked to the PersonInvitation object when invite by e-mail is used
* No valid data in the second e-mail field of the signup form when it was disabled
* Invitation options were displayed to superusers even when the feature was disabled
* Inviting newly created persons for registration failed
* Invited person was not displayed correctly in list of sent invitations
* [Docker] Do not clear cache in migration container die to session invalidation issues
* Notification email about user changes was broken
* SQL cache invalidation could fail when hitting OOT database

`2.7.3`_ - 2022-02-03
---------------------

Fixed
~~~~~

* Migration added in 2.7.2 did not work in all scenarios
* [Dev] Field change tracking API for Person was broken in 2.7.2
* [OAuth] Automatic clean-up of expired OAuth tokens could fail
* Allow maskable icons for non-masked use
* Add missing documentation

Known issues
~~~~~~~~~~~~

* Maskable and non-masked icons *purpose) any cannot be separated

`2.7.2`_ - 2022-01-31
---------------------

Changed
~~~~~~~

* [Dev] The (undocumented) setting PDF_CONTEXT_PROCESSORS is now named NON_REQUEST_CONTEXT_PROCESSORS
* [Docker] Cache is now cleared if migrations are applied
* Update German translations.

Fixed
~~~~~

* Celery progress could be inaccurate if recording progress during a transaction


`2.7.1`_ - 2022-01-28
---------------------

Changed
~~~~~~~

* PWA icons can now be marked maskable
* [OAuth] Expired tokens are now cleared in a periodic task
* PDF file jobs are now automatically expired
* Data checks are now scheduled every 15 minutes by default

Fixed
~~~~~

* PDF generation failed with S3 storage due to incompatibility with boto3
* PWA theme colour defaulted to red
* Form for editing group type displayed irrelevant fields
* Permission groups could get outdated if re-assigning a user account to a different person
* User preferences didn't work correctly sometimes due to race conditions.

`2.7`_ - 2022-01-24
-------------------

Added
~~~~~

* Periodic tasks can now have a default schedule, which is automatically created

Fixed
~~~~~

* Signup was forbidden even if it was enabled in settings
* Phone numbers were not properly linked and suboptimally formatted on person page
* Favicon upload failed with S3 storage.
* Some combinations of allowed self-edit fields on persons could cause errors
* Some preferences were required when they shouldn't, and vice versa.
* IO errors on accessing backup directory in health check are now properly reported
* Date picker was not properly initialized if field was already filled.
* The menu item for entering an invitation code received offline was missing
* CleaveJS was not loaded properly when using an external CDN

Changed
-------

* Allow non-superusers with permission to invite persons

`2.6`_ - 2022-01-10
-------------------

Added
~~~~~

* Add option to open entry in new tab for sidebar navigation menu.
* Add preference for configuring the default phone number country code.
* Persons and groups now have two image fields: official photo and public avatar
* Admins recieve an mail for celery tasks with status "FAILURE"
* OpenID Connect RSA keys can now be passed as string in config files
* Views filtering for person names now also search the username of a linked user
* OAuth2 applications now take an icon which is shown in the authorization progress.
* Add support for hiding the main side nav in ``base.html``.
* Provide base template and function for sending emails with a template.

Fixed
~~~~~

* Changing the favicon did not result in all icons being replaced in some cases
* Superusers with a dummy person were able to access the dashboard edit page.
* GroupManager.get_queryset() returned an incomplete QuerySet
* OAuth was broken by a non-semver-adhering django-oauth-toolkit update
* Too long texts in chips didn't result in a larger chip.
* The ``Person`` model had an ``is_active`` flag that was used in unclear ways; it is now removed
* The data check results list view didn't work if a related object had been deleted in the meanwhile.
* Socialaccount login template was not overriden
* Atomic transactions now cause only one Haystack update task to run
* Too long headlines didn't break in another line.

Changed
~~~~~~~

* Configuration files are now deep merged by default
* Improvements for shell_plus module loading
    * core.Group model now takes precedence over auth.Group
    * Name collisions are resolved by prefixing with the app label
    * Apps can extend SHELL_PLUS_APP_PREFIXES and SHELL_PLUS_DONT_LOAD
* [Docker] Base image now contains curl, grep, less, sed, and pspg
* Views raising a 404 error can now customise the message that is displayed on the error page
* OpenID Connect is enabled by default now, without RSA support
* Login and authorization pages for OAuth2/OpenID Connect now indicate that the user is in progress
  to authorize an external application.
* Tables can be scrolled horizontally.
* Overhauled person detail page
* Use common base template for all emails.

`2.5`_ – 2022-01-02
-------------------

Added
~~~~~

* Recursive helper methods for group hierarchies

Fixed
~~~~~

* Remove left-over reference to preferences in a form definition that caused
  form extensions in downstream apps to break
* Allow non-LDAP users to authenticate if LDAP is used with password handling
* Additional button on progress page for background tasks was shown even if the task failed.
* Register preference for available allowed oauth grants.

`2.4`_ – 2021-12-24
-------------------

Added
~~~~~

* Allow configuration of database options
* User invitations with invite codes and targeted invites for existing
  persons

Fixed
~~~~~

* Correctly update theme colours on change again
* Use correct favicon as default AlekSIS favicon
* Show all years in a 200 year range around the current year in date pickers
* Imprint is now called "Imprint" and not "Impress".
* Logo files weren't uploaded to public namespace.
* Limit LDAP network timeouts to not hang indefinitely on login if LDAP
  server is unreachable

Changed
~~~~~~~

* Modified the appearance of tables for mobile users to be more user friendly
* [Dev] Remove lock file; locking dependencies is the distribution's
  responsibility

Removed
~~~~~~~

* Remove old generated AlekSIS icons

`2.3.1`_ – 2021-12-17
---------------------

Fixed
~~~~~

* Small files could fail to upload to S3 storage due to MemoryFileUploadHandler
* Corrected typos in previous changelog

`2.3`_ – 2021-12-15
-------------------

Added
~~~~~

* [OAuth] Allow apps to fill in their own claim data matching their scopes

Fixed
~~~~~

* View for assigning permissions didn't work with some global permissions.
* PDFs generated in background didn't contain logo or site title.
* Admins were redirected to their user preferences
  while they wanted to edit the preferences of another user.
* Some CharFields were using NULL values in database when field is empty
* Optional dependecy `sentry-sdk` was not optional

Changed
~~~~~~~

* Docker base image ships PostgreSQL 14 client binaries for maximum compatibility
* Docker base image contains Sentry client by default (disabled in config by default)

Removed
~~~~~~~

* Remove impersonation page. Use the impersonation button on the person
  detail view instead.

`2.2.1`_ – 2021-12-02
--------------------

Fixed
~~~~~

* [Docker] Stop initialisation if migrations fail
* [OAuth] Register `groups` scope and fix claim
* [OAuth] Fix OAuth claims for follow-up requests (e.g. UserInfo)
* [OAuth] Fix grant types checking failing on wrong types under some circumstances
* [OAuth] Re-introduce missing algorithm field in application form
* Remove errornous backup folder check for S3

`2.2`_ - 2021-11-29
-------------------

Added
~~~~~

* Support config files in sub-directories
* Provide views for assigning/managing permissions in frontend
* Support (icon) tabs in the top navbar.

Changed
~~~~~~~

* Update German translations.

Fixed
~~~~~

* Use new MaterializeCSS fork because the old version is no longer maintained.
* Sender wasn't displayed for notifications on dashboard.
* Notifications and activities on dashboard weren't sorted from old to new.

`2.1.1`_ - 2021-11-14
---------------------

Added
~~~~~

* Provide ``SITE_PREFERENCES`` template variable for easier and request-independent access on all site preferences.

Fixed
~~~~~

* Make style.css and favicons cachable.
* Import model extensions from other apps before form extensions.
* Recreate backwards compatiblity for OAuth URLs by using ``oauth/`` again.
* Show correct logo and school title in print template if created in the background.

Removed
~~~~~~~

* Remove fallback code from optional Celery as it's now non-optional.

`2.1`_ - 2021-11-05
-------------------

Added
~~~~~

* Provide an ``ExtensiblePolymorphicModel`` to support the features of extensible models for polymorphic models and vice-versa.
* Implement optional Sentry integration for error and performance tracing.
* Option to limit allowed scopes per application, including mixin to enforce that limit on OAuth resource views
* Support trusted OAuth applications that leave out the authorisation screen.
* Add birthplace to Person model.

Changed
~~~~~~~

* Replace dev.sh helper script with tox environments.
* OAuth Grant Flows are now configured system-wide instead of per app.
* Refactor OAuth2 application management views.

Fixed
~~~~~

* Fix default admin contacts

Credits
~~~~~~~

* We welcome new contributor 🐧 Jonathan Krüger!
* We welcome new contributor 🐭 Lukas Weichelt!

`2.0`_ - 2021-10-29
-------------------

Changed
~~~~~~~

* Refactor views/forms for creating/editing persons.

Fixed
~~~~~

* Fix order of submit buttons in login form and restructure login template
  to make 2FA work correctly.
* Fix page title bug on the impersonate page.
* Users were able to edit the linked user if self-editing was activated.
* Users weren't able to edit the allowed fields although they were configured correctly.
* Provide `style.css` and icon files without any authentication to avoid caching issues.


Removed
~~~~~~~

* Remove mass linking of persons to accounts, bevcause the view had performance issues,
  but was practically unused.

`2.0rc7`_ - 2021-10-18
----------------------

Fixed
~~~~~

* Configuration mechanisms for OpenID Connect were broken.
* Set a fixed version for django-sass-processor to avoid a bug with searching ``style.css`` in the wrong storage.
* Correct the z-index of the navbar to display the main title again on mobile devices.

Removed
~~~~~~~

* Leftovers from a functionality already dropped in the development process
  (custom authentication backends and alternative login views).

`2.0rc6`_ - 2021-10-11
----------------------

Added
~~~~~

* OpenID Connect scope and accompanying claim ``groups``
* Support config files in JSON format
* Allow apps to dynamically generate OAuth scopes

Changed
~~~~~~~

* Do not log or e-mail ALLOWED_HOSTS violations
* Update translations.
* Use initial superuser settings as default contact and from addresses

Fixed
~~~~~

* Show link to imprint in footer
* Fix API for adding OAuth scopes in AppConfigs
* Deleting persons is possible again.
* Removed wrong changelog section

Removed
~~~~~~~

* Dropped data anonymization (django-hattori) support for now
* ``OAUTH2_SCOPES`` setting in apps is not supported anymore. Use ``get_all_scopes`` method
  on ``AppConfig`` class instead.

`2.0rc5`_ - 2021-08-25
----------------------

Fixed
~~~~~

* The view for getting the progress of celery tasks didn't respect that there can be anonymous users.
* Updated django to latest 3.2.x


`2.0rc4`_ - 2021-08-01
----------------------

Added
~~~~~

* Allow to configure port for prometheus metrics endpoint.

Fixed
~~~~~

* Correctly deliver server errors to user
* Use text HTTP response for serviceworker.js insteas of binary stream
* Use Django permission instead of rule to prevent performance issues.

`2.0rc3`_ - 2021-07-26
----------------------

Added
~~~~~

* Support PDF generation without available request object (started completely from background).
* Display a loading animation while fetching search results in the sidebar.

Fixed
~~~~~

* Make search suggestions selectable using the arrow keys.

Fixed
~~~~~

* Use correct HTML 5 elements for the search frontend and fix CSS accordingly.

`2.0rc2`_ - 2021-06-24
---------------------

Added
~~~~~

* Allow to install system and build dependencies in docker build


`2.0rc1`_ - 2021-06-23
----------------------

Added
~~~~~

* Add option to disable dashboard auto updating as a user and sitewide.

Changed
~~~~~~~

* Use semantically correct html elements for headings and alerts.

Fixed
~~~~~

* Add missing dependency python-gnupg
* Add missing AWS options to ignore invalid ssl certificates

`2.0b2`_ - 2021-06-15
--------------------

Added
~~~~~~~

* Add option to disable dashboard auto updating as a user and sitewide.

Changed
~~~~~~~

* Add verbose names for all preference sections.
* Add verbose names for all openid connect scopes and show them in grant
  view.
* Include public dashboard in navigation
* Update German translations.

Fixed
~~~~~

* Fix broken backup health check
* Make error recovery in about page work

Removed
~~~~~~~

* Drop all leftovers of DataTables.

`2.0b1`_ - 2021-06-01
---------------------

Changed
~~~~~~~

* Rename every occurance of "social account" by "third-party account".
* Use own templates and views for PWA meta and manifest.
* Use term "application" for all authorized OAuth2 applications/tokens.
* Use importlib instead of pkg_resources (no functional changes)

Fixed
~~~~~

* Fix installation documentation (nginx, uWSGI).
* Use a set for data checks registry to prevent double entries.
* Progress page tried to redirect even if the URL is empty.

Removed
~~~~~~~

* Drop django-pwa completely.

`2.0b0`_ - 2021-05-21
---------------------

Added
~~~~~

* Allow defining several search configs for LDAP users and groups
* Use setuptools entrypoints to find apps
* Add django-cachalot as query cache
* Add ``syncable_fields`` property to ``ExtensibleModel`` to discover fields
  sync backends can write to
* Add ``aleksis-admin`` script to wrap django-admin with pre-configured settings
* Auto-create persons for users if matching attributes are found
* Add ``django-allauth`` to allow authentication using OAuth, user registration,
  password changes and password reset
* Add OAuth2 and OpenID Connect provider support
* Add ``django-uwsgi`` to use uWSGI and Celery in development
* Add loading page for displaying Celery task progress
* Implement generic PDF generation using Chromium
* Support Amazon S3 storage for /media files
* Enable Django REST framework for apps to use at own discretion
* Add method to inject permissions to ExtensibleModels dynamically
* Add helper function which filters queryset by permission and user
* Add generic support for Select 2 with materialize theme
* Add simple message that is shown whenever a page is served from the PWA cache
* Add possibility to upload files using ckeditor
* Show guardians and children on person full page
* Manage object-level permissions in frontend
* Add a generic deletion confirmation view
* Serve Prometheus metrics from app
* Provide system health check endpoint and checks for some components
* Add impersonate button to person view
* Implement a data check system for sanity checks and guided resolution of inconsistencies
* Make the dashboard configurable for users and as default dashboard by admins
* Support dynamic badges in menu items
* Auto-delete old /media files when related model instance is deleted
* Add SortableJS
* Add a widget for links/buttons to other websites

Changed
~~~~~~~

* Make Redis non-optional (see documentation)
* Use Redis as caching and session store to allow horizontal scaling
* Enable PostgreSQL connection pooling
* Use uWSGI to serve /static under development
* Use a token-secured storage as default /media storage
* Rewrite Docker image to serve as generic base image for AlekSIS distributions
* Make Docker image run completely read-only
* Ensure Docker image is compatible with K8s
* Remove legacy file upload functoin; all code is required to use the storage API
* Default search index backend is now Whoosh with Redis storage
* Re-style search result page
* Move notifications to separate page with indicator in menu
* Move to ``BigAutoField`` for all AlekSIS apps
* Require Django 3.2 and Python 3.9
* Person and group lists can now be filtered
* Allow displaying the default widget to anonymous users

Fixed
~~~~~

* Correct behavious of celery-beat in development
* Fix precaching of offline fallback page
* Use correct styling for language selector
* Rewrite notification e-mail template for AlekSIS
* Global search now obeys permissions correctly
* Improve performance of favicon generation
* Dashboard widgets now handle exceptions gracefully
* Roboto font was not available for serving locally

Removed
~~~~~~~

* Dropped support for other search backends than Whoosh
* Drop django-middleware-global-request completely

`2.0a2`_ - 2020-05-04
---------------------

Added
~~~~~

* Frontend-ased announcement management.
* Auto-create Person on User creation.
* Select primary group by pattern if unset.
* Shortcut to personal information page.
* Support for defining group types.
* Add description to Person.
* age_at method and age property to Person.
* Synchronise AlekSIS groups with Django groups.
* Add celery worker, celery-beat worker and celery broker to docker-compose setup.
* Global search.
* License information page.
* Roles and permissions.
* User preferences.
* Additional fields for people per group.
* Support global permission flags by LDAP group.
* Persistent announcements.
* Custom menu entries (e.g. in footer).
* New logo for AlekSIS.
* Two factor authentication with Yubikey, OTP or SMS.
* Devs: Add ExtensibleModel to allow apps to add fields, properties.
* Devs: Support multiple recipient object for one announcement.

Changes
~~~~~~~

* Make short_name for group optional.
* Generalised live loading of widgets for dashboard.
* Devs: Add some CSS helper classes for colours.
* Devs: Mandate use of AlekSIS base model.
* Devs: Drop import_ref field(s); apps shold now define their own reference fields.

Fixed
~~~~~

* DateTimeField Announcement.valid_from received a naive datetime.
* Enable SASS processor in production.
* Fix too short fields.
* Load select2 locally.

`2.0a1`_ - 2020-02-01
---------------------

Added
~~~~~

* Migrate to MaterializeCSS.
* Dashboard.
* Notifications via SMS (Twilio), Email or on the dashboard.
* Admin interface.
* Turn into installable, progressive web app.
* Devs: Background Tasks with Celery.

Changed
~~~~~~~

* Customisable save_button template.
* Redesign error pages.

Fixed
~~~~~

* setup_data no longer forces database connection.

`1.0a4`_ - 2019-11-25
---------------------

Added
~~~~~

* Two-factor authentication with TOTP (Google Authenticator), Yubikey, SMS
  and phone call.
* Devs: CRUDMixin provides a crud_event relation that returns all CRUD
  events for an object.

`1.0a2`_ - 2019-11-11
---------------------

Added
~~~~~

* Devs: Add ExtensibleModel to allow injection of methods and properties into models.


`1.0a1`_ - 2019-09-17
---------------------

Added
~~~~~

* Devs: Add API to get an audit trail for any school-related object.
* Devs: Provide template snippet to display an audit trail.
* Devs: Provide base template for views that allow browsing back/forth.
* Add management command and Cron job for full backups.
* Add system status overview page.
* Allow enabling and disabling maintenance mode from frontend.
* Allow editing the dates of the current school term.
* Add logo to school information.
* Allow editing school information.
* Ensure all actions are reverted if something fails (atomic requests).

Fixed
~~~~~

* Only show active persons in group and persons views.
* Silence KeyError in get_dict template tag.
* Use bootstrap buttons everywhere.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

.. _1.0a1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/1.0a1
.. _1.0a2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/1.0a2
.. _1.0a4: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/1.0a4
.. _2.0a1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0a1
.. _2.0a2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0a2
.. _2.0b0: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0b0
.. _2.0b1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0b1
.. _2.0b2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0b2
.. _2.0rc1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0rc1
.. _2.0rc2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0rc2
.. _2.0rc3: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0rc3
.. _2.0rc4: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0rc4
.. _2.0rc5: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0rc5
.. _2.0rc6: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0rc6
.. _2.0rc7: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0rc7
.. _2.0: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.0
.. _2.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.1
.. _2.1.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.1.1
.. _2.2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.2
.. _2.2.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.2.1
.. _2.3: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.3
.. _2.3.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.3.1
.. _2.4: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.4
.. _2.5: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.5
.. _2.6: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.6
.. _2.7: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.7
.. _2.7.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.7.1
.. _2.7.2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.7.2
.. _2.7.3: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.7.3
.. _2.7.4: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.7.4
.. _2.8: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.8
.. _2.8.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.8.1
.. _2.9: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.9
.. _2.10: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.10
.. _2.10.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.10.1
.. _2.10.2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.10.2
.. _2.11: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.11
.. _2.11.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.11.1
.. _2.12: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.12
.. _2.12.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.12.1
.. _2.12.2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.12.2
.. _2.12.3: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/2.12.3
.. _3.0b0: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.0b0
.. _3.0b1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.0b1
.. _3.0b2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.0b2
.. _3.0b3: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.0b3
.. _3.0: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.0
.. _3.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.1
.. _3.1.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.1.1
.. _3.1.2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.1.2
.. _3.1.3: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.1.3
.. _3.1.4: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.1.4
.. _3.1.5: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.1.5
.. _3.1.6: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.1.6
.. _3.1.7: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.1.7
.. _3.2.0: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.2.0
.. _3.2.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.2.1
.. _3.2.2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/3.2.2
.. _4.0.0: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/4.0.0
.. _4.0.1: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/4.0.1
.. _4.0.2: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/4.0.2
.. _4.0.3: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/4.0.3
.. _4.0.4: https://edugit.org/AlekSIS/official/AlekSIS-Core/-/tags/4.0.4
