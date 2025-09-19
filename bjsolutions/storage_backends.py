from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False   # avoids overwriting files with same name
    default_acl = "public-read"
