from typing import Optional

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Model
from django.http import HttpRequest

from guardian.backends import ObjectPermissionBackend
from guardian.shortcuts import get_objects_for_user
from rules import predicate

from ..mixins import ExtensibleModel
from ..models import (
    AvailabilityEvent,
    DashboardWidgetInstance,
    Group,
    Person,
    PersonalEvent,
    PersonalTodo,
)
from .core_helpers import get_content_type_by_perm, get_site_preferences, queryset_rules_filter
from .core_helpers import has_person as has_person_helper


def permission_validator(request: HttpRequest, perm: str) -> bool:
    """Check whether the request user has a permission."""
    if request.user:
        return request.user.has_perm(perm)
    return False


def check_global_permission(user: User, perm: str) -> bool:
    """Check whether a user has a global permission."""
    return ModelBackend().has_perm(user, perm)


def check_object_permission(
    user: User, perm: str, obj: Model, checker_obj: Optional[ExtensibleModel] = None
) -> bool:
    """Check whether a user has a permission on an object.

    You can provide a custom ``ObjectPermissionChecker`` for prefetching object permissions
    by annotating an extensible model with ``set_object_permission_checker``.
    This can be the provided object (``obj``)  or a special object
    which is only used to get the checker class (``checker_obj``).
    """
    if checker_obj is None:
        checker_obj = obj
    if hasattr(checker_obj, "_permission_checker"):
        return checker_obj._permission_checker.has_perm(perm, obj)
    return ObjectPermissionBackend().has_perm(user, perm, obj)


def has_global_perm(perm: str):
    """Build predicate which checks whether a user has a global permission."""
    name = f"has_global_perm:{perm}"

    @predicate(name)
    def fn(user: User) -> bool:
        return check_global_permission(user, perm)

    return fn


def has_object_perm(perm: str):
    """Build predicate which checks whether a user has a permission on a object."""
    name = f"has_global_perm:{perm}"

    @predicate(name)
    def fn(user: User, obj: Model) -> bool:
        if obj is None:
            return False
        return check_object_permission(user, perm, obj)

    return fn


def has_any_object(perm: str, klass):
    """Check if has any object.

    Build predicate which checks whether a user has access
    to objects with the provided permission or rule.
    Differentiates between object-related permissions and rules.
    """
    name = f"has_any_object:{perm}"

    @predicate(name)
    def fn(user: User) -> bool:
        ct_perm = get_content_type_by_perm(perm)
        # In case an object-related permission with the same ContentType class as the given class
        # is passed, the optimized django-guardian get_objects_for_user function is used.
        if ct_perm and ct_perm.model_class() == klass:
            return get_objects_for_user(user, perm, klass).exists()
        # In other cases, it is checked for each object of the given model whether the current user
        # fulfills the given rule.
        else:
            return queryset_rules_filter(user, klass.objects.all(), perm).exists()

    return fn


def is_site_preference_set(section: str, pref: str):
    """Check the boolean value of a given site preference."""
    name = f"check_site_preference:{section}__{pref}"

    @predicate(name)
    def fn() -> bool:
        return bool(get_site_preferences()[f"{section}__{pref}"])

    return fn


@predicate
def has_person(user: User) -> bool:
    """Predicate which checks whether a user has a linked person."""
    return has_person_helper(user)


@predicate
def has_person_user(user: User, obj) -> bool:
    """Predicate which checks whether a person has a linked user."""
    if obj is None:
        return False
    return bool(obj.user)


@predicate
def has_person_email(user: User, obj) -> bool:
    """Predicate which checks whether a person has an email address."""
    if obj is None:
        return False
    return bool(obj.email)


@predicate
def is_anonymous(user: User) -> bool:
    """Predicate which checks whether a user is anonymous."""
    return user.is_anonymous


@predicate
def is_current_person(user: User, obj: Model) -> bool:
    """Predicate which checks if the provided object is the person linked to the user object."""
    if obj is None:
        return False
    return user.person == obj


@predicate
def is_group_owner(user: User, group: Group) -> bool:
    """Predicate which checks if the user is a owner of the provided group."""
    if group is None:
        return False
    return user.person in group.owners.all()


@predicate
def is_group_member(user: User, group: Group) -> bool:
    """Predicate which checks if the user is a member of the provided group."""
    if group is None:
        return False
    return user.person in group.members.all()


@predicate
def is_notification_recipient(user: User, obj: Model) -> bool:
    """Check if is a notification recipient.

    Predicate which checks whether the recipient of the
    notification a user wants to mark read is this user.
    """
    if obj is None:
        return False
    return user == obj.recipient.user


def contains_site_preference_value(section: str, pref: str, value: str):
    """Check if given site preference contains a value."""
    name = f"check_site_preference_value:{section}__{pref}"

    @predicate(name)
    def fn() -> bool:
        return bool(value in get_site_preferences()[f"{section}__{pref}"])

    return fn


@predicate
def is_assigned_to_current_person(user: User, obj: Model) -> bool:
    """Check if the object is assigned to the current person."""
    if obj is None:
        return False
    return getattr(obj, "person", None) == user.person


@predicate
def is_own_celery_task(user: User, obj: Model) -> bool:
    """Check if the celery task is owned by the current user."""
    if obj is None:
        return False
    return obj.user == user


@predicate
def is_own_availability_event(user: User, availability_event: AvailabilityEvent) -> bool:
    """Predicate which checks if the user is the owner of the provided AvailabilityEvent."""
    if availability_event is None:
        return False
    return user.person == availability_event.person


@predicate
def is_personal_event_owner(user: User, personal_event: PersonalEvent) -> bool:
    """Predicate which checks if the user is the owner of the provided custom event."""
    if personal_event is None:
        return False
    return user.person == personal_event.owner


@predicate
def is_personal_todo_owner(user: User, personal_todo: PersonalTodo) -> bool:
    """Predicate which checks if the user is the owner of the provided personal todo."""
    return user.person == personal_todo.owner


@predicate
def is_group_owner_with_group_type(user: User, group: Group) -> bool:
    """Predicate whick checks if the user is a owner of the group (with allowed group type)."""
    if group is None or not group.group_type or not group.group_type.owners_can_see_groups:
        return False
    return user.person in group.owners.all()


@predicate
def is_group_owner_of_person_with_group_type(user: User, person: Person) -> bool:
    """Check if the user is a group owner of the person (with allowed group type)."""
    if person is None:
        return False
    return person.member_of.filter(
        group_type__owners_can_see_members=True,
        owners=user.person,
    ).exists()


@predicate
def is_group_owner_allowed_information(key: str):
    """Predicate which checks if the information is allowed for group owners."""
    name = f"is_group_owner_allowed_information:{key}"

    @predicate(name)
    def fn(user: User, person: Person) -> bool:
        if person is None:
            return False
        return person.member_of.filter(
            owners=user.person,
            group_type__owners_can_see_members_allowed_information__contains=[key],
        ).exists()

    return fn


@predicate
def has_any_group(user: User):
    qs = get_objects_for_user(user, "core.view_group", Group)
    qs = qs | Group.objects.filter(
        owners=user.person,
        group_type__owners_can_see_groups=True,
    )
    return qs.exists()


@predicate
def has_any_person(user: User):
    qs = get_objects_for_user(user, "core.view_person", Person.objects.all())
    qs = qs | Person.objects.filter(
        member_of__in=Group.objects.filter(
            owners=user.person,
            group_type__owners_can_see_members=True,
        ),
    )
    return qs.exists()


@predicate
def is_dummy(user: User):
    return user.person is None or getattr(user.person, "is_dummy", False)


@predicate
def is_dashboard_widget_instance_owner(user: User, instance: DashboardWidgetInstance) -> bool:
    """Predicate which checks if the user is the owner of the provided custom event."""
    if instance is None:
        return False
    return user.person == instance.person
