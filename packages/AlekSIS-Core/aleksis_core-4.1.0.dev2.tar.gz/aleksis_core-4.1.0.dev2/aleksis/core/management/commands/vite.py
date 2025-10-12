import os

from django.conf import settings
from django.core.management.base import CommandError

from django_yarnpkg.management.base import BaseYarnCommand
from django_yarnpkg.yarn import yarn_adapter

from ...util.frontend_helpers import run_vite, write_vite_values


class Command(BaseYarnCommand):
    help = "Create Vite bundles for AlekSIS"  # noqa

    def add_arguments(self, parser):
        parser.add_argument("command", choices=["build", "serve"], nargs="?", default="build")
        parser.add_argument("--no-install", action="store_true", default=False)

    def handle(self, *args, **options):
        super().handle(*args, **options)

        # Inject settings into Vite
        write_vite_values(os.path.join(settings.NODE_MODULES_ROOT, "django-vite-values.json"))

        # Install Node dependencies
        if not options["no_install"]:
            yarn_adapter.install(settings.YARN_INSTALLED_APPS)

        # Run Vite build
        ret = run_vite([options["command"]])
        if ret != 0:
            raise CommandError("yarn command failed", returncode=ret)
