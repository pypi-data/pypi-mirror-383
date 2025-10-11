"""Download functions for MEModel entities."""

from pathlib import Path
from typing import cast

from entitysdk.client import Client
from entitysdk.downloaders.cell_morphology import download_morphology
from entitysdk.downloaders.emodel import download_hoc
from entitysdk.downloaders.ion_channel_model import download_ion_channel_mechanism
from entitysdk.exception import IteratorResultError, StagingError
from entitysdk.models.emodel import EModel
from entitysdk.models.memodel import MEModel
from entitysdk.schemas.memodel import DownloadedMEModel
from entitysdk.utils.filesystem import create_dir


def download_memodel(client: Client, memodel: MEModel, output_dir=".") -> DownloadedMEModel:
    """Download all assets needed to run an me-model: hoc, ion channel models, and morphology.

    Args:
        client (Client): EntitySDK client
        memodel (MEModel): MEModel entitysdk object
        output_dir (str): directory to save the downloaded files, defaults to current directory
    """
    # we have to get the emodel to get the ion channel models.
    emodel = cast(
        EModel,
        client.get_entity(entity_id=memodel.emodel.id, entity_type=EModel),  # type: ignore
    )

    hoc_path = download_hoc(client, emodel, Path(output_dir) / "hoc")
    if not hoc_path.exists():
        raise StagingError(f"HOC does not exist: {hoc_path}")

    # only take .asc format for now.
    # Will take specific format when morphology_format is integrated into MEModel
    try:
        morphology_path = download_morphology(
            client, memodel.morphology, Path(output_dir) / "morphology", "asc"
        )
    except IteratorResultError:
        morphology_path = download_morphology(
            client, memodel.morphology, Path(output_dir) / "morphology", "swc"
        )
    mechanisms_dir = create_dir(Path(output_dir) / "mechanisms")
    mechanism_files = []
    for ic in emodel.ion_channel_models or []:
        ion_channel_path = download_ion_channel_mechanism(client, ic, mechanisms_dir)
        mechanism_files.append(ion_channel_path.name)

    return DownloadedMEModel(
        hoc_path=hoc_path,
        mechanisms_dir=mechanisms_dir,
        mechanism_files=mechanism_files,
        morphology_path=morphology_path,
    )
