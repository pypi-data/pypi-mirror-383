from re import match, sub

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from aleksis.core.util.core_helpers import get_app_module


def camelcase(value: str) -> str:
    """Convert a string to camelcase."""
    titled = value.replace("_", " ").title().replace(" ", "")
    return titled[0].lower() + titled[1:]


class Command(BaseCommand):
    help = "Convert Django URLs for an app into vue-router routes"  # noqa

    def add_arguments(self, parser):
        parser.add_argument("app", type=str)

    def handle(self, *args, **options):
        app = options["app"]
        app_camel_case = camelcase(app)

        app_config = apps.get_app_config(app)
        app_config_name = f"{app_config.__module__}.{app_config.__class__.__name__}"

        # Import urls from app
        urls = get_app_module(app_config_name, "urls")
        if not urls:
            raise CommandError(f"No url patterns found in app {app}")
        urlpatterns = urls.urlpatterns

        # Import menu from app and structure as dict by url name
        menus = get_app_module(app_config_name, "menus")
        menu_by_urls = {}
        if "NAV_MENU_CORE" in menus.MENUS:
            menu = menus.MENUS["NAV_MENU_CORE"]
            menu_by_urls = {m["url"]: m for m in menu}

            for menu_item in menu:
                if "submenu" in menu_item:
                    for submenu_item in menu_item["submenu"]:
                        menu_by_urls[submenu_item["url"]] = submenu_item

        for url in urlpatterns:
            # Convert route name and url pattern to vue-router format
            menu = menu_by_urls.get(url.name, None)
            route_name = f"{app_camel_case}.{camelcase(url.name)}"
            url_pattern = url.pattern._route
            new_url_pattern_list = []
            for url_pattern_part in url_pattern.split("/"):
                if match(r"<[\w,:,*]*>", url_pattern_part):
                    url_pattern_part = sub(r"(<(?P<val>[\w,:,*]*)>)", r":\g<val>", url_pattern_part)
                    new_url_pattern_list.append(":" + url_pattern_part.split(":")[-1])
                else:
                    new_url_pattern_list.append(url_pattern_part)
            url_pattern = "/".join(new_url_pattern_list)

            # Start building route
            route = "{\n"
            route += f'  path: "{url_pattern}",\n'
            route += (
                '  component: () => import("aleksis.core/components/LegacyBaseTemplate.vue"),\n'
            )
            route += f'  name: "{route_name}",\n'

            if menu:
                # Convert icon to Vuetify format
                icon = None
                if menu.get("vuetify_icon"):
                    icon = menu["vuetify_icon"]
                elif menu.get("svg_icon"):
                    icon = menu["svg_icon"].replace(":", "-")
                elif menu.get("icon"):
                    icon = "mdi-" + menu["icon"]

                if icon:
                    icon = icon.replace("_", "-")

                # Get permission for menu item
                permission = None
                if menu.get("validators"):
                    possible_validators = [
                        v
                        for v in menu["validators"]
                        if v[0] == "aleksis.core.util.predicates.permission_validator"
                    ]
                    if possible_validators:
                        permission = possible_validators[0][1]

                route += "  meta: {\n"
                route += "    inMenu: true,\n"
                route += f'    titleKey: "{menu["name"]}", // Needs manual work\n'
                if icon:
                    route += f'    icon: "{icon}",\n'
                if permission:
                    route += f'    permission: "{permission}",\n'
                route += "  },\n"
            route += "},"

            print(route)
