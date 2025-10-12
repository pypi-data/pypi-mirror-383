from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _

import graphene
from graphene_django import DjangoObjectType

from ..data_checks import check_data
from ..models import DataCheckResult, TaskUserAssignment


class SolveOptionType(graphene.ObjectType):
    name = graphene.String()
    verbose_name = graphene.String()

    @staticmethod
    def resolve_name(root, info, **kwargs):
        return root[0]

    @staticmethod
    def resolve_verbose_name(root, info, **kwargs):
        return root[1].verbose_name


class DataCheckType(graphene.ObjectType):
    problem_name = graphene.String()
    verbose_name = graphene.String()
    solve_options = graphene.List(SolveOptionType)

    @staticmethod
    def resolve_solve_options(root, info, **kwargs):
        return root.solve_options.items()


class GenericRelatedObjectType(graphene.ObjectType):
    id = graphene.ID()
    class_verbose_name = graphene.String()
    instance_verbose_name = graphene.String()
    absolute_url = graphene.String()

    @staticmethod
    def resolve_absolute_url(root, info, **kwargs):
        return root.get_absolute_url().replace("/django", "")

    @staticmethod
    def resolve_class_verbose_name(root, info, **kwargs):
        return root._meta.verbose_name.title()

    @staticmethod
    def resolve_instance_verbose_name(root, info, **kwargs):
        return str(root)


class DataCheckResultType(DjangoObjectType):
    class Meta:
        model = DataCheckResult
        fields = (
            "id",
            "solved",
        )

    related_check = graphene.Field(DataCheckType)
    related_object = graphene.Field(GenericRelatedObjectType)


class RunDataChecksMutation(graphene.Mutation):
    task_id = graphene.ID()

    @classmethod
    def mutate(cls, root, info):
        if not info.context.user.has_perm("core.run_data_checks_rule"):
            raise PermissionDenied()

        user_assignment = check_data.delay_with_progress(
            TaskUserAssignment(
                user=info.context.user,
                title=_("Progress: Run data checks"),
                progress_title=_("Run data checks …"),
                error_message=_("There was a problem while running data checks."),
                success_message=_("The data checks were run successfully."),
                back_url="/data_checks/",
            )
        )

        return RunDataChecksMutation(task_id=user_assignment.id)


class SolveDataCheckResultMutation(graphene.Mutation):
    class Arguments:
        result = graphene.ID()
        solve_option = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, result, solve_option):
        if not info.context.user.has_perm("core.solve_data_problem_rule"):
            raise PermissionDenied()

        result_obj = DataCheckResult.objects.get(pk=result)

        if solve_option in result_obj.related_check.solve_options:
            result_obj.solve(solve_option)
        else:
            raise ValidationError(_("The requested solve option does not exist"))

        return SolveDataCheckResultMutation(ok=True)
