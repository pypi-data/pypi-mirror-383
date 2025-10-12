PWA (progressive web application)
=================================

What is a progressive web application?
--------------------------------------

A PWA is an application developed with common web technologies and
delivered in form of a website, but which offers some features a
traditional website does not and overall creates an impression that
resembles that of a native application.

AlekSIS PWA features
--------------------

The AlekSIS PWA offers the following features (not all available on all
platforms):

-  Installable and displayable in a separate window
-  Caching and serving, if given page cannot be accessed, of
   non-interactive pages and needed assets
-  Provision of an offline fallback page if wanted page cannot be
   accessed and there is no cached one
-  Indicator whether the served page is served from the PWA cache

Installation of the PWA
-----------------------

The procedure to get a native feeling using the AlekSIS PWA varies from
platform to platform. On some, you are prompted to add AlekSIS to your
home screen of desktop using a popup; on others, you have to take action
yourself and find the corresponding menu entry. As of the time of
writing, “installable” PWAs are supported by all major platforms except
Firefox Desktop and Safari Desktop which nevertheless support the other features.

Chromium-based browsers (e.g. Chromium, Google Chrome, Microsoft
Edge) will usually prompt you to install the PWA by a popup on both
mobile and desktop devices; for the former using a banner

.. image:: ../_static/pwa_mobile_chromium.png
  :width: 40%
  :alt: PWA installation prompt on the mobile version of the Chromium browser

and for the latter using an appearing button in the address bar.

.. image:: ../_static/pwa_desktop_chromium.png
  :width: 100%
  :alt: PWA installation prompt on the desktop version of the Chromium browser

In both cases, a click on the notification is enough to start
the installation process.

Firefox Mobile will also prompt you using a dot near the
menu button; then ``Install`` has to be clicked.

.. image:: ../_static/pwa_mobile_firefox.png
  :width: 40%
  :alt: PWA installation prompt on the mobile version of the Firefox browser

On Safari Mobile, you need to open the share popup and click on the
``Add to Home Screen`` button.

.. image:: ../_static/pwa_mobile_safari.png
  :width: 40%
  :alt: PWA installation prompt on the mobile version of the Safari browser

No matter what platform is used, AlekSIS can be accessed as an
independent application entry, just like any other installed native
application, after installation.
