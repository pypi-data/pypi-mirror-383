"""Custom registries for some preference containers."""

from dynamic_preferences.registries import (
    PerInstancePreferenceRegistry,
    global_preferences_registry,
)


class PersonPreferenceRegistry(PerInstancePreferenceRegistry):
    """Registry for preferences valid for a person."""

    pass


class GroupPreferenceRegistry(PerInstancePreferenceRegistry):
    """Registry for preferences valid for members of a group."""

    pass


site_preferences_registry = global_preferences_registry
person_preferences_registry = PersonPreferenceRegistry()
group_preferences_registry = GroupPreferenceRegistry()
