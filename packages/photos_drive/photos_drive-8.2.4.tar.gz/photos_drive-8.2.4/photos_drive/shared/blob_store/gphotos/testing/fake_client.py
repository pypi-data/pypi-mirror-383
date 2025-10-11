import sys
from typing import Optional
import uuid

from photos_drive.shared.blob_store.gphotos.albums_client import GPhotosAlbumsClient
from photos_drive.shared.blob_store.gphotos.client import (
    GPhotosClientV2,
    GPhotosStorageQuota,
)
from photos_drive.shared.blob_store.gphotos.media_items_client import (
    GPhotosMediaItemsClient,
)
from photos_drive.shared.blob_store.gphotos.testing.fake_albums_client import (
    FakeGPhotosAlbumsClient,
)
from photos_drive.shared.blob_store.gphotos.testing.fake_items_repository import (
    FakeItemsRepository,
)
from photos_drive.shared.blob_store.gphotos.testing.fake_media_items_client import (
    FakeGPhotosMediaItemsClient,
)


class FakeGPhotosClient(GPhotosClientV2):
    def __init__(
        self,
        repository: FakeItemsRepository,
        id: Optional[str] = None,
        max_num_photos: int = sys.maxsize,
    ):
        self.repository = repository
        self.id = str(uuid.uuid4()) if id is None else id
        self.max_num_photos = max_num_photos

        self._albums_client = FakeGPhotosAlbumsClient(self.id, repository)
        self._media_items_client = FakeGPhotosMediaItemsClient(self.id, repository)

    def get_storage_quota(self) -> GPhotosStorageQuota:

        # Each photo is 1 byte
        return GPhotosStorageQuota(
            limit=self.max_num_photos,
            usage_in_drive=0,
            usage_in_drive_trash=0,
            usage=len(self.media_items().search_for_media_items()),
        )

    def name(self) -> str:
        return self.id

    def albums(self) -> GPhotosAlbumsClient:
        return self._albums_client

    def media_items(self) -> GPhotosMediaItemsClient:
        return self._media_items_client
