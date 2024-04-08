# convert yaml to objects

from django.db import transaction

from customermodels.models import UserSchema, UserTable, UserTableColumn
from customermodels.schemas import UserSchemaSchema
from users.models import User


def create_user_table_from_yaml(user: User, parsed_input: UserSchemaSchema):
    # for now do not worry about repeats.
    with transaction.atomic():
        schema = UserSchema.objects.create(
            user=user, name=parsed_input.name, description=parsed_input.description
        )

        for table in parsed_input.tables:
            user_table = UserTable.objects.create(
                user=user, name=table.name, description=table.description, schema=schema
            )

            for column in table.columns:
                UserTableColumn.objects.create(
                    table=user_table,
                    name=column.name,
                    description=column.description,
                    dtype=column.dtype,
                )

    return schema
