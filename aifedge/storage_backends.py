from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class PublicMediaStorage(S3Boto3Storage):
    location = settings.AWS_PUBLIC_FILE_LOCATION
    # default_acl = 'None'
    file_overwrite = False