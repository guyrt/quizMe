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


def user_schema_to_markdown(user: User, user_schema_id: int) -> str:
    # Fetch the UserSchema instance
    user_schema = get_user_schema_with_related(user, user_schema_id)

    # Start building the Markdown string
    markdown_str = f"# Schema: {user_schema.name}\n\n"
    markdown_str += f"**Description:** {user_schema.description}\n\n"

    # Fetch related UserTable instances
    user_tables = user_schema.usertable_set.all()
    for user_table in user_tables:
        markdown_str += f"## Table: {user_table.name}\n"
        markdown_str += f"**Description:** {user_table.description}\n\n"

        # Fetch related UserTableColumn instances
        user_table_columns = user_table.usertablecolumn_set.all()
        if user_table_columns:
            markdown_str += "**Columns:**\n\n"
            markdown_str += "| Name | Description | Data Type |\n"
            markdown_str += "|------|-------------|-----------|\n"
            for user_table_column in user_table_columns:
                markdown_str += f"| {user_table_column.name} | {user_table_column.description} | {user_table_column.dtype or 'N/A'} |\n"
            markdown_str += "\n"
        else:
            markdown_str += "_No columns defined._\n\n"

    return markdown_str


def get_user_schema_with_related(user: User, user_schema_id: int):
    user_schema = UserSchema.objects.prefetch_related("usertable_set").prefetch_related(
        "usertable_set__usertablecolumn_set"
    )
    return user_schema.get(user=user, id=user_schema_id)
