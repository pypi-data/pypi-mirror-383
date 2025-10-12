.. _core-concept:

Concepts of the AlekSIS core
============================

The AlekSIS core provides functionality and data models as a base for
all apps.

.. _core-concept-schoolterm:

The concept of school terms
---------------------------

In AlekSIS, mostly everything is based on school terms. A school term is
a defined time range which can be used to link data to it. Typically,
such data are learning groups, timetables or class register records.
Although their name suggests it, school terms don’t have to be a half or
a full year. They should depend on the way how you organise data in your
institution.

For example, if you issue reports at the end of every half year, a half
year would be a good time range for your school terms because the class
register statistics are evaluated for school terms.

Anyway, you should create a school term before you start to import or
create other data entries like persons or groups.

Manage school terms
~~~~~~~~~~~~~~~~~~~

You can manage the school terms if you login with your admin account and
open the menu entry ``Data management → School terms``. There you can find a list
of all school terms and buttons to create, edit or delete school terms.
Please be aware that there can be only one school term at time and each
school term needs a unique name.

The currently active school term can be selected using the ``Active school term``
menu in the app bar. It defaults to the school term that includes the
current date. When viewing school term related data such as class register
statistics, the currently set active school term determines the subset of
data that is shown.

.. _core-concept-person:

The concept of persons
----------------------

The person model is designed to save all the data of students, teachers,
guardians and any other persons of the school society. It tracks
information like the following:

-  Full name
-  Short name
-  Sex
-  Date of birth
-  Contact details (phone numbers, email)
-  Address details
-  Photo
-  Relation to guardians
-  Primary group (e. g. a class or a tutor group, cf. :ref:`core-concept-group`)

Except for the name, all data points are optional, so you can decide on
your own (and based on your local data protection laws) which data should be
included in AlekSIS.

There are two important things you should know about persons:

-  **Persons are not automatically users:** That means that persons can
   be linked to a user account including things like a password and the
   ability to login, but they don’t have to be. For example, your
   AlekSIS instance could save the data about parents, but you don’t
   want them to login: In this scenario, the guardians are available as
   persons **without** user accounts.
-  **Persons are not linked to school terms:** As persons like students
   are not only at the school for one school term, persons are not
   linked to school terms.

Manage persons
~~~~~~~~~~~~~~

The main method to manage persons is the view under
``People → Persons``. To add person to groups, you have to open the
respective group and set the person as a member or an owner.

.. _core-concept-group:

The concept of groups
---------------------

The AlekSIS groups are a universal way to organise persons in
collections like classes, courses, tutor groups, clubs, or any other
division you could imagine. They track the following data:

-  Group name and short name
-  Owners (e. g. class or course teacher(s))
-  Members (e. g. students)
-  Parent groups (e. g. a class could be a parent group for a course)
-  Group type (e. g. class, course, club, etc.)

In contrast to persons, groups are supposed to be **linked to school
terms** (but they don’t have to be). For example, the composition of a
class or a course varies from school term to school term. In order to
archive historical data according to local laws, these groups have to be
separated which is solved by linking them to a school term.

Manage groups
~~~~~~~~~~~~~

Groups are managed on the page ``People → Groups``. There you can
search, view, create, change and delete groups.

.. _core-concept-grouptype:

Manage group types
~~~~~~~~~~~~~~~~~~

You can manage your local group types by opening the menu entry
``People → Group types`` as an admin user.


The concept of roles
~~~~~~~~~~~~~~~~~~~~

As a flexible way to describe relationships in AlekSIS, there are roles.
Currently, it is used to describe the person-to-person relationships of
children and their parents. In the future it will be possible to describe
person-to-person relationships, group memberships, and more with custom roles.

Import school terms, persons and groups from other data sources
---------------------------------------------------------------

When AlekSIS is not your single date source, all these data can be
imported from other sources. You can find further information in the
respective integration apps.

.. _core-concept-room:

The concept of rooms
--------------------

The rooms model allows you to manage places (e. g. actual rooms, sports fields)
that can then be linked to other location-based entities (e. g. lessons). 
It tracks the following data:

-  Room name and short name

Manage rooms
~~~~~~~~~~~~

Rooms are managed on the page ``Data management → Rooms``. There you can
search, view, create, change and delete rooms.

Import rooms from other data sources
------------------------------------

When AlekSIS is not your single date source, rooms can be
imported from other sources. You can find further information in the
respective integration apps.

.. _core-concept-calendarfeed:

The concept of calendar feeds and calendar events
-------------------------------------------------

In AlekSIS, every category of time-related information is organised in
a seperate calendar feed. Each calendar feed is populated with events
based on a given logic. Calendar event instances are used to track
the required information. In some cases, event data is filled based on
data that is already present in instances of another model (e. g. birthdays of persons).
If not extended, these calendar events can track the following data:

- Start and end date/datetime
- Timezone
- Recurrence rule

In AlekSIS' core, there are three predefined calendar feeds:

- Birthdays (of persons)
- Holidays
- Personal events

The events contained in calendar feeds can be viewed on the ``Calendar`` page.
Users are able to select which feeds they want to see in their personal
calendar overview.

Configure calendar feeds
------------------------

You can configure calendar-related settings via the ``Calendar`` tab of the
``Administration → Configuration`` page. This includes:

- The first weekday to appear on the calendar frontend
- The colors assigned to the birthday, holiday and personal event feeds, respectively

.. _core-concept-holiday:

The concept of holidays
-----------------------

Holidays are used to save the time periods of (public) holidays. They are displayed
as contextual information in the calendar overview and all relevant calendar views
(e. g. timetables). They track the following data:

- Holiday name
- Start and end date

Manage holidays
~~~~~~~~~~~~~~~

Holidays are managed on the page ``Data management → Holidays``. There you can
search, view, create, change and delete holidays.
