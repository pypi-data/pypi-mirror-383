import random
import string
from urllib.parse import urlparse

from django import template
from django.shortcuts import reverse

from bs4 import BeautifulSoup

register = template.Library()


@register.filter
def add_class_to_el(value: str, arg: str) -> str:
    """Add a CSS class to every occurence of an element type.

    :Example:

    .. code-block::

        {{ mymodel.myhtmlfield|add_class_to_el:"ul,browser-default" }}
    """
    el, cls = arg.split(",")
    soup = BeautifulSoup(value, "html.parser")

    for sub_el in soup.find_all(el):
        sub_el["class"] = sub_el.get("class", []) + [cls]

    return str(soup)


@register.filter
def remove_prefix(value: str, prefix: str) -> str:
    """Remove prefix of a url.

    :Example:

    .. code-block::

        {{ object.get_absolute_url|remove_prefix: "/django/" }}
    """
    url = urlparse(value)

    if url.path.startswith(prefix):
        url = url._replace(path=url.path[len(prefix) :])

    return url.geturl()


@register.simple_tag
def generate_random_id(prefix: str, length: int = 10) -> str:
    """Generate a random ID for templates.

    :Example:

    .. code-block::

        {% generate_random_id "prefix-" %}
    """
    return prefix + "".join(
        random.choice(string.ascii_lowercase)  # noqa: S311
        for i in range(length)
    )


@register.simple_tag(takes_context=True)
def absolute_url(context, view_name, *args, **kwargs):
    request = context["request"]
    return request.build_absolute_uri(reverse(view_name, args=args, kwargs=kwargs))
