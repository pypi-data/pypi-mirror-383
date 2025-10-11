from typing import cast

from photos_drive.shared.metadata.album_id import AlbumId
from photos_drive.shared.metadata.albums_repository import AlbumsRepository
from photos_drive.shared.metadata.media_items_repository import MediaItemsRepository


class AlbumsPruner:
    '''A class responsible for pruning albums in the albums tree.'''

    def __init__(
        self,
        root_album_id: AlbumId,
        albums_repo: AlbumsRepository,
        media_items_repo: MediaItemsRepository,
    ):
        self.__albums_repo = albums_repo
        self.__root_album_id = root_album_id
        self.__media_items_repo = media_items_repo

    def prune_album(self, album_id: AlbumId) -> int:
        '''
        Prunes albums upwards in the albums tree.
        For instance, if we have this album structure:

        Archives
        └── Photos
            ├── random.jpg
            └── 2011
                └── Wallpapers

        running AlbumsPruner.prune_album() on Wallpapers will delete Wallpapers and
        2011, and make the albums tree become:

        Archives
        └── Photos
            └── random.jpg

        Args:
            album_id (AlbumId): The starting node.

        Returns:
            int: The number of albums that have been deleted.
        '''
        albums_to_delete: set[AlbumId] = set()
        cur_album_id = album_id
        cur_album = self.__albums_repo.get_album_by_id(cur_album_id)

        while True:
            cur_album = self.__albums_repo.get_album_by_id(cur_album_id)
            child_albums = self.__albums_repo.find_child_albums(cur_album_id)
            child_album_ids_set = set([child_album.id for child_album in child_albums])
            if len(child_album_ids_set - albums_to_delete) > 0:
                break

            if self.__media_items_repo.get_num_media_items_in_album(cur_album_id) > 0:
                break

            if cur_album.id == self.__root_album_id:
                break

            parent_album_id = cast(AlbumId, cur_album.parent_album_id)
            albums_to_delete.add(cur_album_id)

            cur_album_id = parent_album_id

        self.__albums_repo.delete_many_albums(list(albums_to_delete))

        return len(albums_to_delete)
