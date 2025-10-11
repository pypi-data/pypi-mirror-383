from app.internal.config import settings
from app.utils.constants.settings import App
from logyca_azure_storage_blob import AzureStorageAccountBlobManagement, SetCredentialsConnectionString
import json

asabm=AzureStorageAccountBlobManagement(SetCredentialsConnectionString(connection_string=settings.connection_string))

# 1) Delete all by date searching from the root of the container (if preview_only=true it does not delete)
res = asabm.container_blob_delete_by_age(
    container_name=App.AzureStorageAccount.Containers.NAME_WITH_DATA,
    older_than_unit="hours",
    older_than=7,
    container_folders=[],
    include_subfolders=True,
    preview_only=True
)
if isinstance(res,dict):
    print(f"deleted files={res.get("deleted",None)}")
    print(f"details={json.dumps(res,indent=4)}")
else:
    print(f"Error: {res}")

# 2) Delete only in /folder1/folder2/ (without entering subfolders)
res = asabm.container_blob_delete_by_age(
    container_name=App.AzureStorageAccount.Containers.NAME_WITH_DATA,
    older_than_unit="weeks",
    older_than=2,
    container_folders=["folder1","folder2"],
    include_subfolders=False,
    preview_only=True
)
if isinstance(res,dict):
    print(f"deleted files={res.get("deleted",None)}")
    print(f"details={json.dumps(res,indent=4)}")
else:
    print(f"Error: {res}")
