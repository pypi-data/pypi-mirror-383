Social accounts
===============

AlekSIS can authenticate users against third party applications using OAuth2
or OpenID.

This can be used to grant access to persons whose credentials shall not be
managed in AlekSIS itself, for example because another authentication provider
is already used throughout the school, or for guardians that can or should for
some reason not get a local account, or similar situations.

.. warning::
  Social accounts are **not** working with two factor authentication! If a user
  authenticates with a social account, the two factor authentication is
  ignored on login (but enforced for views that require two factor authentication later).

Configuring social account provider
-----------------------------------

For available providers, see documentation of `django-allauth
<https://docs.allauth.org/en/latest/socialaccount/providers/index.html>`_.

A new social account provider can be configured in your configuration file
(located in ``/etc/aleksis/``).

Configuration examples::

  # GitLab
  [[auth.providers.gitlab.APPS]]
  client_id = "<client_id>"
  secret = "<client_secret>"
  settings = { gitlab_url = "https://gitlab.example.com" }

  # Generic OpenID Connect
  [[auth.providers.openid_connect.APPS]]
  client_id = '<client_id>'
  secret = '<client_secret>'
  name = 'Service Name'
  provider_id = 'service_name'
  settings = { server_url =  'https://example.org' }

After configuring a new authentication provider, you have to restart AlekSIS.

Match local accounts to social accounts by username
---------------------------------------------------

You can configure AlekSIS to automatically match local accounts to social accounts
by their username. To do this, set the following configuration::

  [auth]
  socialaccount_username_matching = true

.. warning::
  Only activate this behavior, if you are completely sure
  that you want to match local accounts to social accounts
  by their username and that the third-party provider can be trusted.
