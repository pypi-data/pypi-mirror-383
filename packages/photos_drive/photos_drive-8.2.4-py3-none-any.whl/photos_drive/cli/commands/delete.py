import logging

import typer
from typing_extensions import Annotated

from photos_drive.backup.backup_photos import PhotosBackup
from photos_drive.backup.diffs import Diff
from photos_drive.backup.processed_diffs import DiffsProcessor
from photos_drive.cli.shared.config import build_config_from_options
from photos_drive.cli.shared.files import (
    get_media_file_paths_from_path,
)
from photos_drive.cli.shared.inputs import (
    prompt_user_for_yes_no_answer,
)
from photos_drive.cli.shared.logging import setup_logging
from photos_drive.cli.shared.printer import pretty_print_diffs
from photos_drive.cli.shared.typer import (
    createMutuallyExclusiveGroup,
)
from photos_drive.shared.blob_store.gphotos.clients_repository import (
    GPhotosClientsRepository,
)
from photos_drive.shared.llm.models.blip_image_captions import BlipImageCaptions
from photos_drive.shared.llm.models.open_clip_image_embeddings import (
    OpenCLIPImageEmbeddings,
)
from photos_drive.shared.llm.vector_stores import vector_store_builder
from photos_drive.shared.llm.vector_stores.distributed_vector_store import (
    DistributedVectorStore,
)
from photos_drive.shared.maps.mongodb.map_cells_repository_impl import (
    MapCellsRepositoryImpl,
)
from photos_drive.shared.metadata.mongodb.albums_repository_impl import (
    AlbumsRepositoryImpl,
)
from photos_drive.shared.metadata.mongodb.clients_repository_impl import (
    MongoDbClientsRepository,
)
from photos_drive.shared.metadata.mongodb.media_items_repository_impl import (
    MediaItemsRepositoryImpl,
)

logger = logging.getLogger(__name__)

app = typer.Typer()
config_exclusivity_callback = createMutuallyExclusiveGroup(2)


@app.command()
def delete(
    path: str,
    config_file: Annotated[
        str | None,
        typer.Option(
            "--config-file",
            help="Path to config file",
            callback=config_exclusivity_callback,
        ),
    ] = None,
    config_mongodb: Annotated[
        str | None,
        typer.Option(
            "--config-mongodb",
            help="Connection string to a MongoDB account that has the configs",
            is_eager=False,
            callback=config_exclusivity_callback,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            help="Whether to show all logging debug statements or not",
        ),
    ] = False,
):
    setup_logging(verbose)

    logger.debug(
        "Called add handler with args:\n"
        + f" path: {path}\n"
        + f" config_file: {config_file}\n"
        + f" config_mongodb={config_mongodb}\n"
        + f" verbose={verbose}"
    )

    # Set up the repos
    config = build_config_from_options(config_file, config_mongodb)
    mongodb_clients_repo = MongoDbClientsRepository.build_from_config(config)
    gphoto_clients_repo = GPhotosClientsRepository.build_from_config(config)
    albums_repo = AlbumsRepositoryImpl(mongodb_clients_repo)
    media_items_repo = MediaItemsRepositoryImpl(mongodb_clients_repo)
    map_cells_repository = MapCellsRepositoryImpl(mongodb_clients_repo)
    vector_store = DistributedVectorStore(
        [
            vector_store_builder.config_to_vector_store(vector_store_config)
            for vector_store_config in config.get_vector_store_configs()
        ]
    )

    # Get the diffs
    diffs = [
        Diff(modifier="-", file_path=path)
        for path in get_media_file_paths_from_path(path)
    ]

    # Confirm if diffs are correct by the user
    pretty_print_diffs(diffs)
    if not prompt_user_for_yes_no_answer("Is this correct? (Y/N): "):
        print("Operation cancelled.")
        return

    # Process the diffs with metadata
    diff_processor = DiffsProcessor(OpenCLIPImageEmbeddings(), BlipImageCaptions())
    processed_diffs = diff_processor.process_raw_diffs(diffs)
    for processed_diff in processed_diffs:
        logger.debug(f"Processed diff: {processed_diff}")

    # Process the diffs
    backup_service = PhotosBackup(
        config,
        albums_repo,
        media_items_repo,
        map_cells_repository,
        vector_store,
        gphoto_clients_repo,
        mongodb_clients_repo,
    )
    backup_results = backup_service.backup(processed_diffs)
    logger.debug(f"Backup results: {backup_results}")

    print(f"Deleted {len(diffs)} items.")
    print(f"Items added: {backup_results.num_media_items_added}")
    print(f"Items deleted: {backup_results.num_media_items_deleted}")
    print(f"Albums created: {backup_results.num_albums_created}")
    print(f"Albums deleted: {backup_results.num_albums_deleted}")
