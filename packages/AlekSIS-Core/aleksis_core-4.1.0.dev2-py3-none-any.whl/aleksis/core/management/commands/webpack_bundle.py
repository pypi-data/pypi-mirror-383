import warnings

from .vite import Command as ViteCommand


class Command(ViteCommand):
    help = "Create Vite bundles for AlekSIS (legacy command alias)"  # noqa

    def handle(self, *args, **options):
        warnings.warn(
            "webpack_bundle is deprecated and will be removed "
            "in AlekSIS-Core 4.0. Use the new vite command instead.",
            UserWarning,
        )

        super().handle(*args, **options)
