from buzzerboy_saas_tenants.core import settings
from buzzerboy_saas_tenants.core.platformConnectors import *
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage


DEFAULT_ACL = 'private'
ADDRESSING_STYLE = 'path'
SIGNATURE_VERSION = 's3v4'

# Constants for storage locations
MEDIA_LOCATION = "media/"
KB_LOCATION="knowledgebase/"

class BaseStorage:
    def __init__(self, location: str, default_acl: str = DEFAULT_ACL,
                 addressing_style: str = ADDRESSING_STYLE,
                 signature_version: str = SIGNATURE_VERSION, sync_to_bedrock: bool = False, *args, **kwargs):

        self.sync_to_bedrock = sync_to_bedrock
        bucket_name = getBucketName()
        if bucket_name:
            kwargs.update({
                "access_key": getAWSAccessKey(),
                "secret_key": getAWSSecretKey(),
                "bucket_name": bucket_name,
                "region_name": getRegionName(),
                "default_acl": default_acl,
                "file_overwrite": False,
                "location": location,
                "addressing_style": addressing_style,
                "signature_version": signature_version,
            })
            self.storage = S3Boto3Storage(*args, **kwargs)
        else:
            self.storage = FileSystemStorage(location=location)
            # print(f"Using local file system storage for location: {location}")

    def __getattr__(self, name):
        return getattr(self.storage, name)

    def save(self, name, content, max_length=None):
        """Override save to add Bedrock sync functionality"""
        name = self.storage.save(name, content, max_length=max_length)

        if self.sync_to_bedrock and isinstance(self.storage, S3Boto3Storage):
            self._trigger_bedrock_sync(name)
        return name

    # def _trigger_bedrock_sync(self, file_name):
    #     """Trigger a sync with Bedrock Knowledge Base for a specific file"""
    #     try:
    #         knowledge_base_id = getBedrockKnowledgeBaseId()
    #         if not knowledge_base_id:
    #             print("No Bedrock Knowledge Base ID configured")
    #             return

    #         # Use the same credentials as S3Boto3Storage
    #         bedrock_client = boto3.client(
    #             'bedrock-agent',  # This service name is correct
    #             aws_access_key_id=getAWSAccessKey(),
    #             aws_secret_access_key=getAWSSecretKey(),
    #             region_name=getRegionName()
    #         )

    #         data_source_id = getBedrockKnowledgeDataSourceId()
            
    #         # Specify the S3 URI for the specific file
    #         bucket_name = getBucketName()
    #         file_s3_uri = f"s3://{bucket_name}/{self.storage.location}{file_name}"

    #         # Use IngestKnowledgeBaseDocuments API to add only this specific file
    #         try:
    #             response = bedrock_client.ingest_knowledge_base_documents(
    #                 knowledgeBaseId=knowledge_base_id,
    #                 dataSourceId=data_source_id,
    #                 documents=[{
    #                     "content": {
    #                         "dataSourceType": "S3",
    #                         "s3": {
    #                             "s3Location": {
    #                                 "uri": file_s3_uri
    #                             }
    #                         }
    #                     }
    #                 }]
    #             )
    #             print(f"File {file_name} directly ingested into Knowledge Base: {response}")
    #         except Exception as e:
    #             print(f"Direct ingestion failed, falling back to full sync: {str(e)}")
                
    #             # Fallback to regular sync if direct ingestion fails
    #             response = bedrock_client.start_ingestion_job(
    #                 knowledgeBaseId=knowledge_base_id,
    #                 dataSourceId=data_source_id,
    #                 description=f"Fallback sync for file: {file_name}"
    #             )
    #             print(f"Fallback: Full Knowledge Base sync initiated for file {file_name}: {response}")
                
    #     except Exception as e:
    #         print(f"Failed to sync file {file_name} with Bedrock Knowledge Base: {str(e)}")

class MediaStorage(BaseStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(location=MEDIA_LOCATION, sync_to_bedrock=True, *args, **kwargs)

