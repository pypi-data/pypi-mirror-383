from django.core.exceptions import PermissionDenied

import graphene

from ..models import Todo


class SetTodoCompletedMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()  # noqa
        completed = graphene.DateTime(required=False)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id, completed):  # noqa
        todo = Todo.objects.get(pk=id)

        if not todo.check_if_can_edit(info.context.user):
            raise PermissionDenied()

        todo.completed = completed
        if completed:
            todo.percent_complete = 100
        else:
            todo.percent_complete = 0
        todo.save()

        return SetTodoCompletedMutation(ok=True)
