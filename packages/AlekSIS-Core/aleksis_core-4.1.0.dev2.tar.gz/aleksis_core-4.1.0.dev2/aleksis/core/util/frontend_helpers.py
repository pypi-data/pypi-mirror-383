import json
import os
import shutil
from collections.abc import Sequence
from typing import Any, Optional

from django.conf import settings

from django_yarnpkg.yarn import yarn_adapter

from .core_helpers import get_app_module, get_app_packages


def get_apps_with_frontend():
    """Get a dictionary of apps that ship frontend code/assets."""
    assets = {}
    for app in get_app_packages():
        mod = get_app_module(app, "apps")
        path = os.path.join(os.path.dirname(mod.__file__), "frontend")
        if os.path.isdir(path):
            package = ".".join(app.split(".")[:-2])
            assets[package] = path
    return assets


def write_vite_values(out_path: str) -> dict[str, Any]:
    # Inline import to avoid circular dependency
    from ..schema import schema

    vite_values = {
        "static_url": settings.STATIC_URL,
        "serverPort": settings.DJANGO_VITE_DEV_SERVER_PORT,
        "schema": schema.introspect(),
    }
    # Write rollup entrypoints for all apps
    vite_values["appDetails"] = {}
    for app, path in get_apps_with_frontend().items():
        if os.path.exists(path):
            vite_values["appDetails"][app] = {}
            vite_values["appDetails"][app]["name"] = app.split(".")[-1]
            vite_values["appDetails"][app]["assetDir"] = path
            vite_values["appDetails"][app]["hasMessages"] = os.path.exists(
                os.path.join(path, "messages", "en.json")
            )
    # Add core entrypoint
    vite_values["coreAssetDir"] = os.path.join(settings.BASE_DIR, "aleksis", "core", "frontend")

    # Add directories
    vite_values["baseDir"] = settings.BASE_DIR
    vite_values["cacheDir"] = settings.CACHE_DIR
    vite_values["node_modules"] = settings.JS_ROOT

    with open(out_path, "w") as out:
        json.dump(vite_values, out)


def run_vite(args: Optional[Sequence[str]] = None) -> int:
    args = list(args) if args else []

    config_path = os.path.join(settings.BASE_DIR, "aleksis", "core", "vite.config.mjs")
    shutil.copy(config_path, settings.NODE_MODULES_ROOT)

    mode = "development" if settings.DEBUG else "production"
    args += ["-m", mode]

    log_level = settings.LOGGING["root"]["level"]
    if settings.DEBUG or log_level == "DEBUG":
        args.append("-d")
    log_level = {"INFO": "info", "WARNING": "warn", "ERROR": "error"}.get(log_level, "silent")
    args += ["-l", log_level]

    return yarn_adapter.call_yarn(["run", "vite"] + args)


def get_language_cookie(code: str) -> str:
    """Build a cookie string to set a new language."""
    cookie_parts = [f"{settings.LANGUAGE_COOKIE_NAME}={code}"]
    args = dict(
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    cookie_parts += [f"{k.replace('_', '-')}={v}" for k, v in args.items() if v]
    return "; ".join(cookie_parts)
