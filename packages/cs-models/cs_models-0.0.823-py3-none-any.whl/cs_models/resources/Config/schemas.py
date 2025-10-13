from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
)
from ...utils.utils import pre_load_date_fields


class ConfigResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    latest_date = fields.DateTime(required=True)
    table_name = fields.String(required=True)
    field_name = fields.String(required=True)
    field_value = fields.String(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

    @pre_load
    def convert_string_to_datetime(self, in_data, **kwargs):
        date_fields = ['latest_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m-%d-%Y',
        )
        return in_data


class ConfigQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer()
    table_name = fields.String()
    field_name = fields.String()
    field_value = fields.String()
    latest_date = fields.DateTime()

    @pre_load
    def convert_string_to_datetime(self, in_data, **kwargs):
        date_fields = ['date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m-%d-%Y',
        )
        return in_data


class ConfigPatchSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    latest_date = fields.DateTime(allow_none=False)
    table_name = fields.String(allow_none=False)
    field_name = fields.String(allow_none=False)
    field_value = fields.String(allow_none=True)

    @pre_load
    def convert_string_to_datetime(self, in_data, **kwargs):
        date_fields = ['date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%m-%d-%Y',
        )
        return in_data
