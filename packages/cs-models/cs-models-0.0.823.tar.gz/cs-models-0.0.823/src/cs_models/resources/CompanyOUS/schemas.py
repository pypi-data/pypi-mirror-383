from marshmallow import (
    Schema,
    fields,
    validate,
)


class CompanyOUSResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    cik = fields.Integer()
    name = fields.String(required=True, validate=not_blank)
    ticker = fields.String(allow_none=True)
    exchange = fields.String(allow_none=True)
    market_cap = fields.Decimal(allow_none=True)
    company_url = fields.String(allow_none=True)
    pipeline_url = fields.String(allow_none=True)
    ir_url = fields.String(allow_none=True)
    is_activated = fields.Boolean(allow_none=True)
    is_searchable = fields.Boolean(allow_none=True)
    last_crawl_date = fields.DateTime(allow_none=True)
    industry_type = fields.String(allow_none=True)
    company_sec_link = fields.Integer(allow_none=True)
    relevant_links = fields.String(allow_none=True)
    notes = fields.String(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)


class CompanyOUSQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    name = fields.String(validate=not_blank)
    ticker = fields.String(validate=not_blank)


class CompanyOUSUpdateSchema(Schema):
    id = fields.Integer()
    cik = fields.Integer()
    market_cap = fields.Decimal(allow_none=True)
    company_url = fields.String(allow_none=True)
    pipeline_url = fields.String(allow_none=True)
    ir_url = fields.String(allow_none=True)
    last_crawl_date = fields.DateTime(allow_none=True)
    industry_type = fields.String(allow_none=True)
    company_sec_link = fields.Integer(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)
