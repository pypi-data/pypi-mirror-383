from marshmallow import (
    Schema,
    fields,
    validate,
)


class MeetingBucketResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    meeting_bucket_name = fields.String(required=True)
    updated_at = fields.DateTime()
