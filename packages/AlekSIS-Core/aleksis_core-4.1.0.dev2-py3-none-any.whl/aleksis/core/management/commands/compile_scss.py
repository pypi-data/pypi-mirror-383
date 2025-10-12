import os

from django.conf import settings
from django.core.management.base import BaseCommand

import sass


class Command(BaseCommand):
    help = "Compile SCSS stylesheet for AlekSIS"  # noqa

    def handle(self, *args, **options):
        static_dir = os.path.join(settings.BASE_DIR, "aleksis", "core", "static")
        scss_dir = os.path.join(static_dir, "public")
        scss_path = os.path.join(scss_dir, "style.scss")
        css_path = os.path.join(static_dir, "style.css")

        compiled = sass.compile(
            filename=scss_path,
            include_paths=[
                os.path.join(settings.JS_ROOT, "@materializecss", "materialize", "sass"),
                os.path.join(scss_path),
            ],
        )
        with open(css_path, "w") as f:
            f.write(compiled)
