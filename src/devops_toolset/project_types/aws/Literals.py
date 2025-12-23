"""AWS module literals"""

from devops_toolset.core.app import App
from devops_toolset.core.ValueDictsBase import ValueDictsBase

app: App = App()


class Literals(ValueDictsBase):
    """ValueDicts for the AWS module."""

    _info = {
        "cloudfront_invalidation_created": _("Created CloudFront invalidation with id {id}"),
        "s3_downloaded_object_from_s3_bucket":
            _("Downloaded object with key \"{name}\" from bucket {bucket} to {destination}"),
        "s3_downloading_objects_from_s3_bucket":
            _("Downloading {number} objects from bucket {bucket} to {destination}"),
        "s3_got_x_objects_from_s3_bucket": _("Got a list of {number} objects from the {bucket} bucket"),
        "s3_uploaded_object_to_s3_bucket": _("Uploaded object {object_key} to {bucket} bucket"),
    }
    _errors = {}
