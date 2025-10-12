import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connections
from django.db.migrations.recorder import MigrationRecorder
from django.db.models import Model
from django.db.models.aggregates import Count
from django.utils.functional import classproperty
from django.utils.text import slugify
from django.utils.translation import gettext as _

import reversion
from color_contrast import AccessibilityLevel, ModulationMode, check_contrast, modulate
from reversion import set_comment

from .mixins import RegistryObject
from .util.celery_progress import ProgressRecorder, recorded_task
from .util.core_helpers import get_site_preferences
from .util.email import send_email

if TYPE_CHECKING:
    from aleksis.core.models import DataCheckResult


class SolveOption:
    """Define a solve option for one or more data checks.

    Solve options are used in order to give the data admin typical
    solutions to a data issue detected by a data check.

    Example definition

    .. code-block:: python

        from aleksis.core.data_checks import SolveOption
        from django.utils.translation import gettext as _

        class DeleteSolveOption(SolveOption):
            _class_name = "delete" # has to be unqiue
            verbose_name = _("Delete") # should make use of i18n

            @classmethod
            def solve(cls, check_result: "DataCheckResult"):
                check_result.related_object.delete()
                check_result.delete()

    After the solve option has been successfully executed,
    the corresponding data check result has to be deleted.
    """

    _class_name: str = "default"
    verbose_name: str = ""

    @classmethod
    def solve(cls, check_result: "DataCheckResult"):
        pass


class IgnoreSolveOption(SolveOption):
    """Mark the object with data issues as solved."""

    _class_name = "ignore"
    verbose_name = _("Ignore problem")

    @classmethod
    def solve(cls, check_result: "DataCheckResult"):
        """Mark the object as solved without doing anything more."""
        check_result.solved = True
        check_result.save()


class DataCheck(RegistryObject):
    """Define a data check.

    Data checks should be used to search objects of
    any type which are broken or need some extra action.

    Defining data checks
    --------------------
    Data checks are defined by inheriting from the class DataCheck
    and registering the inherited class in the data check registry.

    Example:

    ``data_checks.py``
    ******************

    .. code-block:: python

        from aleksis.core.data_checks import DataCheck, DATA_CHECK_REGISTRY
        from django.utils.translation import gettext as _

        class ExampleDataCheck(DataCheck):
            _class_name = "example" # has to be unique
            verbose_name = _("Ensure that there are no examples.")
            problem_name = _("There is an example.") # should both make use of i18n
            required_for_migrations = True # Make mandatory for migrations

            solve_options = {
                IgnoreSolveOption._class_name: IgnoreSolveOption
            }

            @classmethod
            def check_data(cls):
                from example_app.models import ExampleModel

                wrong_examples = ExampleModel.objects.filter(wrong_value=True)

                for example in wrong_examples:
                    cls.register_result(example)

    ``models.py``
    *************

    .. code-block:: python

        from .data_checks import ExampleDataCheck

        # ...

        class ExampleModel(Model):
            data_checks = [ExampleDataCheck]


    Solve options are used in order to give the data admin typical solutions to this specific issue.
    They are defined by inheriting from SolveOption.
    More information about defining solve options can be find there.

    The dictionary ``solve_options`` should include at least the IgnoreSolveOption,
    but preferably also own solve options. The keys in this dictionary
    have to be ``<YourOption>SolveOption._class_name``
    and the values must be the corresponding solve option classes.

    The class method ``check_data`` does the actual work. In this method
    your code should find all objects with issues and should register
    them in the result database using the class method ``register_result``.

    Data checks have to be registered in their corresponding model.
    This can be done by adding a list ``data_checks``
    containing the data check classes.

    Executing data checks
    ---------------------
    The data checks can be executed by using the
    celery task named ``aleksis.core.data_checks.check_data``.
    We recommend to create a periodic task in the backend
    which executes ``check_data`` on a regular base (e. g. every day).

    .. warning::
        To use the option described above, you must have setup celery properly.

    Notifications about results
    ---------------------------
    The data check tasks can notify persons via email
    if there are new data issues. You can set these persons
    by adding them to the preference
    ``Email recipients for data checks problem emails`` in the site configuration.

    To enable this feature, you also have to activate
    the preference ``Send emails if data checks detect problems``.
    """  # noqa: D412

    verbose_name: str = ""
    problem_name: str = ""

    required_for_migrations: bool = False
    migration_dependencies: list[str] = []

    solve_options = {IgnoreSolveOption._class_name: IgnoreSolveOption}

    _current_results = []

    @classmethod
    def check_data(cls):
        """Find all objects with data issues and register them."""
        pass

    @classmethod
    def run_check_data(cls):
        """Wrap ``check_data`` to ensure that post-processing tasks are run."""
        cls.check_data()
        cls.delete_old_results()

    @classmethod
    def solve(cls, check_result: "DataCheckResult", solve_option: str):
        """Execute a solve option for an object detected by this check.

        :param check_result: The result item from database
        :param solve_option: The name of the solve option that should be executed
        """
        with reversion.create_revision():
            solve_option_obj = cls.solve_options[solve_option]
            set_comment(
                _(
                    f"Solve option '{solve_option_obj.verbose_name}' "
                    f"for data check '{cls.verbose_name}'"
                )
            )
            solve_option_obj.solve(check_result)

    @classmethod
    def get_results(cls):
        DataCheckResult = apps.get_model("core", "DataCheckResult")

        return DataCheckResult.objects.filter(data_check=cls._class_name)

    @classmethod
    def register_result(cls, instance) -> "DataCheckResult":
        """Register an object with data issues in the result database.

        :param instance: The affected object
        :return: The database entry
        """
        from aleksis.core.models import DataCheckResult

        ct = ContentType.objects.get_for_model(instance)
        result, __ = DataCheckResult.objects.get_or_create(
            data_check=cls._class_name,
            content_type=ct,
            object_id=instance.id if not isinstance(instance, int) else instance,
        )

        # Track all existing problems (for deleting old results)
        cls._current_results.append(result)

        return result

    @classmethod
    def delete_old_results(cls):
        """Delete old data check results for problems which exist no longer."""
        pks = [r.pk for r in cls._current_results]
        old_results = cls.get_results().exclude(pk__in=pks)

        if old_results.exists():
            logging.info(f"Delete {old_results.count()} old data check results.")
            old_results.delete()

        # Reset list with existing problems
        cls._current_results = []

    @classproperty
    def data_checks_choices(cls):
        return [(check._class_name, check.verbose_name) for check in cls.registered_objects_list]


@recorded_task(run_every=timedelta(minutes=15))
def check_data(recorder: ProgressRecorder):
    """Execute all registered data checks and send email if activated."""

    for check in recorder.iterate(DataCheck.registered_objects_list):
        logging.info(f"Run check: {check.verbose_name}")
        check.run_check_data()

    if get_site_preferences()["general__data_checks_send_emails"]:
        send_emails_for_data_checks()


def check_data_for_migrations(with_dependencies: bool = False):
    """Run data checks before/after migrations to ensure consistency of data."""
    applied_migrations = set(MigrationRecorder(connections["default"]).applied_migrations())

    for check in filter(lambda d: d.required_for_migrations, DataCheck.registered_objects_list):
        check: DataCheck

        if set(check.migration_dependencies).issubset(applied_migrations) or not with_dependencies:
            logging.info(f"Run data check: {check.verbose_name}")
            check.run_check_data()

            # Show results
            results = check.get_results().values("id")
            for result in results:
                result: DataCheckResult
                logging.info(f"#{result['id']}")

            if results and with_dependencies:
                logging.error(
                    "There are unresolved data checks necessary for migrating. "
                    "Please resolve them as described in the documentation before migrating."
                )
                exit(1)
            elif results:
                logging.error(
                    "There are unresolved data checks. "
                    "Please check and resolve them in the web interface."
                )


def send_emails_for_data_checks():
    """Notify one or more recipients about new problems with data.

    Recipients can be set in dynamic preferences.
    """
    from .models import DataCheckResult  # noqa

    results = DataCheckResult.objects.filter(solved=False, sent=False)

    if results.exists():
        results_by_check = results.values("data_check").annotate(count=Count("data_check"))

        results_with_checks = []
        for result in results_by_check:
            results_with_checks.append(
                (DataCheck.registered_objects_dict[result["data_check"]], result["count"])
            )

        recipient_list = [
            p.mail_sender
            for p in get_site_preferences()["general__data_checks_recipients"]
            if p.email
        ]

        for group in get_site_preferences()["general__data_checks_recipient_groups"]:
            recipient_list += [p.mail_sender for p in group.announcement_recipients if p.email]

        send_email(
            template_name="data_checks",
            recipient_list=recipient_list,
            context={"results": results_with_checks},
        )

        logging.info("Sent notification email because of unsent data checks")

        results.update(sent=True)


class DeactivateDashboardWidgetSolveOption(SolveOption):
    _class_name = "deactivate_dashboard_widget"
    verbose_name = _("Deactivate DashboardWidget")

    @classmethod
    def solve(cls, check_result: "DataCheckResult"):
        from .models import DashboardWidget

        widget = check_result.related_object
        widget.status = DashboardWidget.Status.OFF.value
        widget.save()
        check_result.delete()


class BrokenDashboardWidgetDataCheck(DataCheck):
    _class_name = "broken_dashboard_widgets"
    verbose_name = _("Ensure that there are no broken DashboardWidgets.")
    problem_name = _("The DashboardWidget was reported broken automatically.")
    solve_options = {
        IgnoreSolveOption._class_name: IgnoreSolveOption,
        DeactivateDashboardWidgetSolveOption._class_name: DeactivateDashboardWidgetSolveOption,
    }

    @classmethod
    def check_data(cls):
        from .models import DashboardWidget

        broken_widgets = DashboardWidget.objects.filter(status=DashboardWidget.Status.BROKEN.value)

        for widget in broken_widgets:
            logging.info("Check DashboardWidget %s", widget)
            cls.register_result(widget)


def field_validation_data_check_factory(app_name: str, model_name: str, field_name: str) -> type:
    from django.apps import apps

    class FieldValidationDataCheck(DataCheck):
        _class_name = f"field_validation_{slugify(model_name)}_{slugify(field_name)}"
        verbose_name = _("Validate field {field} of model {model}.").format(
            field=field_name, model=app_name + "." + model_name
        )
        problem_name = _("The field {} couldn't be validated successfully.").format(field_name)
        solve_options = {
            IgnoreSolveOption._class_name: IgnoreSolveOption,
        }

        @classmethod
        def check_data(cls):
            model: Model = apps.get_model(app_name, model_name)
            for obj in model.objects.all():
                try:
                    model._meta.get_field(field_name).validate(getattr(obj, field_name), obj)
                except ValidationError:
                    logging.info(f"Check {model_name} {obj}")
                    cls.register_result(obj)

    FieldValidationDataCheck.__name__ = model_name + "FieldValidationDataCheck"

    return FieldValidationDataCheck


class DisallowedUIDDataCheck(DataCheck):
    _class_name = "disallowed_uid"
    verbose_name = _("Ensure that there are no disallowed usernames.")
    problem_name = _("A user with a disallowed username was reported automatically.")
    solve_options = {
        IgnoreSolveOption._class_name: IgnoreSolveOption,
    }

    @classmethod
    def check_data(cls):
        from django.contrib.auth.models import User

        disallowed_uids = get_site_preferences()["auth__disallowed_uids"].split(",")

        for user in User.objects.filter(username__in=disallowed_uids):
            logging.info(f"Check User {user}")
            cls.register_result(user)


field_validation_data_check_factory("core", "CustomMenuItem", "icon")


class ChangeEmailAddressSolveOption(SolveOption):
    _class_name = "change_email_address"
    verbose_name = _("Change email address")


class EmailUniqueDataCheck(DataCheck):
    _class_name = "email_unique"
    verbose_name = _("Ensure that email addresses are unique among all persons")
    problem_name = _("There was a non-unique email address.")

    required_for_migrations = True
    migration_dependencies = [("core", "0057_drop_otp_yubikey")]

    solve_options = {ChangeEmailAddressSolveOption._class_name: ChangeEmailAddressSolveOption}

    @classmethod
    def check_data(cls):
        known_email_addresses = set()
        from .models import Person

        persons = Person.objects.values("id", "email")

        for person in persons:
            if person["email"] and person["email"] in known_email_addresses:
                cls.register_result(person["id"])
            known_email_addresses.add(person["email"])


def accessible_colors_factory(
    app_name: str,
    model_name: str,
    fg_field_name: str = None,
    bg_field_name: str = None,
    fg_color: str = "#ffffff",
    bg_color: str = "#000000",
    modulation_mode: ModulationMode = ModulationMode.BOTH,
) -> None:
    ColorAccessibilityDataCheck.models.append(
        (
            app_name,
            model_name,
            fg_field_name,
            bg_field_name,
            fg_color,
            bg_color,
            modulation_mode,
        )
    )


def _get_colors_from_model_instance(instance, fg_field_name, bg_field_name, fg_color, bg_color):
    colors: list[str] = [fg_color, bg_color]
    if fg_field_name is not None:
        colors[0] = getattr(instance, fg_field_name)

    if bg_field_name is not None:
        colors[1] = getattr(instance, bg_field_name)

    # Transparency is not support for checking contrasts, so simply truncate it
    for index, color in enumerate(colors):
        if not color.startswith("#"):
            continue
        if len(color) == 5:
            # color is of format "#RGBA"
            colors[index] = color[:-1]
        elif len(color) == 9:
            # color is of format "#RRGGBBAA"
            colors[index] = color[:-2]

    return colors


class ModulateColorsSolveOption(SolveOption):
    _class_name = "modulate_colors"
    verbose_name = _("Auto-adjust Colors")

    @classmethod
    def solve(cls, check_result: "DataCheckResult"):
        instance = check_result.related_object
        ctype = check_result.content_type

        model_info = list(
            filter(
                lambda m: m[0] == ctype.app_label and m[1] == ctype.model,
                ColorAccessibilityDataCheck.models,
            )
        )

        if len(model_info) == 0:
            check_result.solved = False
            check_result.save()
            logging.error(f"Modulate Colors check failed for {check_result}: Model Info not found")
            return
        elif len(model_info) > 1:
            check_result.solved = False
            check_result.save()
            logging.error(f"Modulate Colors check failed for {check_result}: Duplicate Model Info")
            return

        [_, _, fg_field_name, bg_field_name, fg_color, bg_color, modulation_mode] = model_info[0]

        colors = _get_colors_from_model_instance(
            instance, fg_field_name, bg_field_name, fg_color, bg_color
        )

        fg_new, bg_new, success = modulate(*colors, mode=modulation_mode)

        if not success:
            check_result.solved = False
            check_result.save()
            logging.error(
                f"Modulate Colors check failed for {check_result}: Modulation not possible"
            )
            return

        if fg_field_name:
            setattr(instance, fg_field_name, fg_new)
        if bg_field_name:
            setattr(instance, bg_field_name, bg_new)
        instance.save()
        check_result.solved = True
        check_result.save()


class ColorAccessibilityDataCheck(DataCheck):
    _class_name = "colors_accessibility_datacheck"
    verbose_name = _("Validate contrast accessibility of colors of customizable objects.")
    problem_name = _("The colors of this object are not accessible.")
    solve_options = {
        IgnoreSolveOption._class_name: IgnoreSolveOption,
        ModulateColorsSolveOption._class_name: ModulateColorsSolveOption,
    }
    models = []

    @classmethod
    def check_data(cls):
        from django.apps import apps

        for [
            app_name,
            model_name,
            fg_field_name,
            bg_field_name,
            fg_color,
            bg_color,
            _modulation_mode,
        ] in cls.models:
            model: Model = apps.get_model(app_name, model_name)
            for obj in model.objects.all():
                colors = _get_colors_from_model_instance(
                    obj, fg_field_name, bg_field_name, fg_color, bg_color
                )

                if not check_contrast(*colors, level=AccessibilityLevel.AA):
                    logging.info(f"Insufficient contrast in {app_name}.{model_name}.{obj}")
                    cls.register_result(obj)


class ModulateThemeColorsSolveOption(SolveOption):
    _class_name = "modulate_theme_colors"
    verbose_name = _("Auto-adjust Color")

    @classmethod
    def solve(cls, check_result: "DataCheckResult"):
        instance = check_result.related_object

        preference = f"{instance.section}__{instance.name}"

        prefs = get_site_preferences()

        color = prefs[preference]

        fg_new, color_new, success = modulate("#fff", color, mode=ModulationMode.BACKGROUND)

        if not success:
            check_result.solved = False
            check_result.save()
            logging.error(f"Modulate {instance.name} theme color failed: Modulation not possible.")
            return

        prefs[preference] = str(color_new)

        check_result.solved = True
        check_result.save()


class AccessibleThemeColorsDataCheck(DataCheck):
    _class_name = "accessible_themes_colors_datacheck"
    verbose_name = _("Validate that theme colors are accessible.")
    problem_name = _("The color does not provide enough contrast")
    solve_options = {
        IgnoreSolveOption._class_name: IgnoreSolveOption,
        ModulateThemeColorsSolveOption._class_name: ModulateThemeColorsSolveOption,
    }

    @classmethod
    def check_data(cls):
        from dynamic_preferences.models import GlobalPreferenceModel

        from .util.core_helpers import get_site_preferences

        prefs = get_site_preferences()

        primary = prefs["theme__primary"]
        secondary = prefs["theme__secondary"]

        # White text on primary colored background
        if not check_contrast("#fff", primary, level=AccessibilityLevel.AA):
            logging.info("Insufficient contrast in primary color")
            obj = GlobalPreferenceModel.objects.get(section="theme", name="primary")
            cls.register_result(obj)

        # White text on secondary colored background
        if not check_contrast("#fff", secondary, level=AccessibilityLevel.AA):
            logging.info("Insufficient contrast in primary color")
            obj = GlobalPreferenceModel.objects.get(section="theme", name="secondary")
            cls.register_result(obj)
