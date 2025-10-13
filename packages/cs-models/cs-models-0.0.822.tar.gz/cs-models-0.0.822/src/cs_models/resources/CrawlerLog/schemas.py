from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    ValidationError,
)
from ...utils.utils import pre_load_date_fields


class CrawlerLogResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    company_sec_id = fields.Integer(allow_none=True)
    company_ous_id = fields.Integer(allow_none=True)
    crawl_time = fields.Float(required=True)
    base_crawl_time = fields.Float(allow_none=True)
    base_crawl_completed = fields.Boolean(allow_none=True)
    crawl_date = fields.DateTime(required=True)
    updated_at = fields.DateTime()

    @pre_load
    def check_company_ids(self, in_data, **kwargs):
        if self._get_number_of_company_fields(in_data) != 1:
            raise ValidationError('Provide either company_sec_id or '
                                  'company_ous_id, not both')
        return in_data

    def _get_number_of_company_fields(self, in_data, **kwargs):
        result = 0
        if 'company_sec_id' in in_data:
            if in_data['company_sec_id'] is not None:
                result += 1
        if 'company_ous_id' in in_data:
            if in_data['company_ous_id'] is not None:
                result += 1
        return result

    @pre_load
    def convert_string_to_datetime(self, in_data, **kwargs):
        date_fields = ['crawl_date']

        in_data = pre_load_date_fields(
            in_data,
            date_fields,
            date_format='%Y%m%dT%H%M%S',
        )
        return in_data
