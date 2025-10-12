Storage
=======

Data in AlekSIS is mainly separated into two kinds of data:

- Structured data in a relational database
- Media files in a file storage

Both need to be carefully configured.

Database
--------

The only supported database system in AlekSIS is PostgreSQL. Its requirements
and basic installation are laid out in the installation chapter.

In order to gain good performance using PostgreSQL, special care should be taken
both in configuring the PostgreSQL server itself and AlekSIS.

Configuring and tuning PostgreSQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For help on configuring a performant PostgreSQL database, please refer
to the PostgreSQL documentation and related resources. In order to optimise
for AlekSIS' workload, some helpful hints to consider are:

- AlekSIS is a read-heavy workload. Hence, optimise for sufficient ``shared_buffers``
  to hold most of AlekSIS' data of the current school term.
- Some modules do extensive calculations in the database, e.g. resolve
  recurrence rules in the calendar system. This is especially true when using
  the class register or comparable apps. Ensure that ``work_mem`` is set
  high enough – when using the class register in an average high school, it
  can be advisable to set it as high as ``128MB`` to prevent PostgreSQL from
  creating temp files
- Failing fast is better than letting users wait indefinitely. Hence, set a
  reasonable ``statement_timeout``, e.g. ``5s``.
- Using external connection poolers like pgPool or pgBouncer is unnecessary and
  has no effects apart from reducing performance and security

Settings for AlekSIS' database usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On top of the settings explained in the installation instructions, AlekSIS'
PostgreSQL usage can be tuned by providing any ``OPTIONS`` supported by
psycopg. Notably, these include [ConnectionPool]_.

Ideally, your connection pool should maintain a minimum of connections to be
ready for the usual load of requests during a school day, and allow enough
spare connections for load peaks (e.g. during breaks or when new timetables
are published).

For an average high school with 1000 students and 100 teachers, we can estimate
a *usage factor*. While younger students will mostly check their substitutions
when at home, or have this done by their parents, older students might regularly
access AlekSIS on their smartphones all day long and especially during breaks.
Hence, we optimise for 500 users accessing the platform simultaneously. As most
requests take les than 100 ms in the database, and accesses don't occur strictly
simultaneously, if system resources allow for it, 50 is a good measure for the
minimum connection pool size, with a maximum of 100 for peaks (or even 150, if a
dedicated PostgreSQL server is used).

Addtionally, user interactions should *fail fast* instead of waiting indefinitely.
Hence, if the connection pool is exhausted, users should see a timeout error quickly.
They will certainly complain, but this is more actionable than havin users hammer their
touch screens impatiently.

This would result in a configuration like::

  [database.options.pool]
  min_size = 50
  max_size = 150
  timeout = 5

.. note::
   Make sure to also set PostgreSQL's ``max_connections`` high enough.

File storage
------------

AlekSIS needs a writable storage, both for media files (pictures,
generated PDF files, and the like), and to store generated frontend
assets like the themed CSS stylesheet.

.. note::
    Everything except this media storage can be mounted and used
    entirely read-only, i.e. to keep the AlekSIS installation immutable.

Local filesystem storage
~~~~~~~~~~~~~~~~~~~~~~~~

By default, the media storage resides in the local filesystem, in the
location defined in the ``static.root`` configuration key.

.. warning::
    Do not expose the media storage directly through a webserver.
    AlekSIS uses a specially protected storage framework that
    employs cryptographic tokens to protect user data from URL
    guessing.

Amazon S3 (or other S3-compatible storage)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

AlekSIS allows you to configure an Amazon S3 endpoint for  media
files. This is useful e.g. for loadbalancing with multiple AlekSIS
instances.

.. note::
   For some background jobs, AlekSIS stores HTML snippets in the media
   storage for later use. You must ensure your S3 endpoint is part of
   your ``Access-Control-Allow-Origin`` CORS header, so HTML loaded from
   there can load resources from the ALekSIS instance.

If you want to use an S3 endpoint to store files you have to configure the
endpoint in your configuration file (`/etc/aleksis/aleksis.toml`)::

  # Default values
  [storage.s3]
  enabled = true
  endpoint_url = "https://minio.example.com"
  bucket_name = "aleksis-test"
  access_key_id = "XXXXXXXXXXXXXX"
  secret_key = "XXXXXXXXXXXXXXXXXXXXXX"

.. [ConnectionPool] connection pooling options, psycopg2 docs,
                    https://www.psycopg.org/psycopg3/docs/api/pool.html#psycopg_pool.ConnectionPool
