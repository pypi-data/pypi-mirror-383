from __future__ import annotations

import sys

if sys.version_info < (3, 11):  # pragma: no cover
    from backports.strenum import StrEnum
else:
    from enum import StrEnum


from enum import Enum
from typing import Annotated, Any, Literal
from pydantic import AnyUrl, AwareDatetime, BaseModel, Field, RootModel, UUID4
from uuid import UUID
from pathlib import Path
from datetime import timedelta


class ActivityType(StrEnum):
    simulation_execution = "simulation_execution"
    simulation_generation = "simulation_generation"
    validation = "validation"
    calibration = "calibration"
    analysis_notebook_execution = "analysis_notebook_execution"


class AgePeriod(StrEnum):
    prenatal = "prenatal"
    postnatal = "postnatal"
    unknown = "unknown"


class AnalysisNotebookExecutionAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    start_time: Annotated[AwareDatetime | str | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[AwareDatetime | str | None, Field(title="End Time")] = "<NOT_SET>"
    used_ids: Annotated[list[UUID] | str | None, Field(title="Used Ids")] = "<NOT_SET>"
    generated_ids: Annotated[list[UUID] | str | None, Field(title="Generated Ids")] = "<NOT_SET>"
    analysis_notebook_template_id: Annotated[
        UUID | str | None, Field(title="Analysis Notebook Template Id")
    ] = "<NOT_SET>"
    analysis_notebook_environment_id: Annotated[
        UUID | str | None, Field(title="Analysis Notebook Environment Id")
    ] = "<NOT_SET>"


class AnalysisNotebookExecutionCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    start_time: Annotated[AwareDatetime | None, Field(title="Start Time")] = None
    end_time: Annotated[AwareDatetime | None, Field(title="End Time")] = None
    used_ids: Annotated[list[UUID] | None, Field(title="Used Ids")] = []
    generated_ids: Annotated[list[UUID] | None, Field(title="Generated Ids")] = []
    analysis_notebook_template_id: Annotated[
        UUID | None, Field(title="Analysis Notebook Template Id")
    ] = None
    analysis_notebook_environment_id: Annotated[
        UUID, Field(title="Analysis Notebook Environment Id")
    ]


class AnalysisNotebookResultAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"


class AnalysisNotebookResultCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]


class AnalysisNotebookResultUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"


class CountMax(RootModel[int]):
    root: Annotated[int, Field(ge=0, title="Count Max")]


class AnalysisScale(StrEnum):
    subcellular = "subcellular"
    cellular = "cellular"
    circuit = "circuit"
    system = "system"


class AnnotationAdminUpdate(BaseModel):
    pref_label: Annotated[str | None, Field(title="Pref Label")] = "<NOT_SET>"
    alt_label: Annotated[str | None, Field(title="Alt Label")] = "<NOT_SET>"
    definition: Annotated[str | None, Field(title="Definition")] = "<NOT_SET>"


class AnnotationCreate(BaseModel):
    pref_label: Annotated[str, Field(title="Pref Label")]
    alt_label: Annotated[str, Field(title="Alt Label")]
    definition: Annotated[str, Field(title="Definition")]


class AnnotationRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    pref_label: Annotated[str, Field(title="Pref Label")]
    alt_label: Annotated[str, Field(title="Alt Label")]
    definition: Annotated[str, Field(title="Definition")]


class ApiErrorCode(StrEnum):
    GENERIC_ERROR = "GENERIC_ERROR"
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    INVALID_REQUEST = "INVALID_REQUEST"
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    ENTITY_FORBIDDEN = "ENTITY_FORBIDDEN"
    ENTITY_DUPLICATED = "ENTITY_DUPLICATED"
    ASSET_NOT_FOUND = "ASSET_NOT_FOUND"
    ASSET_DUPLICATED = "ASSET_DUPLICATED"
    ASSET_INVALID_FILE = "ASSET_INVALID_FILE"
    ASSET_MISSING_PATH = "ASSET_MISSING_PATH"
    ASSET_INVALID_PATH = "ASSET_INVALID_PATH"
    ASSET_NOT_A_DIRECTORY = "ASSET_NOT_A_DIRECTORY"
    ASSET_INVALID_SCHEMA = "ASSET_INVALID_SCHEMA"
    ASSET_INVALID_CONTENT_TYPE = "ASSET_INVALID_CONTENT_TYPE"
    ION_NAME_NOT_FOUND = "ION_NAME_NOT_FOUND"
    S3_CANNOT_CREATE_PRESIGNED_URL = "S3_CANNOT_CREATE_PRESIGNED_URL"
    OPENAI_API_KEY_MISSING = "OPENAI_API_KEY_MISSING"
    OPENAI_API_ERROR = "OPENAI_API_ERROR"


class AssetLabel(StrEnum):
    morphology = "morphology"
    morphology_with_spines = "morphology_with_spines"
    cell_composition_summary = "cell_composition_summary"
    cell_composition_volumes = "cell_composition_volumes"
    single_neuron_synaptome_config = "single_neuron_synaptome_config"
    single_neuron_synaptome_simulation_data = "single_neuron_synaptome_simulation_data"
    single_neuron_simulation_data = "single_neuron_simulation_data"
    sonata_circuit = "sonata_circuit"
    compressed_sonata_circuit = "compressed_sonata_circuit"
    circuit_figures = "circuit_figures"
    circuit_analysis_data = "circuit_analysis_data"
    circuit_connectivity_matrices = "circuit_connectivity_matrices"
    nwb = "nwb"
    neuron_hoc = "neuron_hoc"
    emodel_optimization_output = "emodel_optimization_output"
    sonata_simulation_config = "sonata_simulation_config"
    simulation_generation_config = "simulation_generation_config"
    custom_node_sets = "custom_node_sets"
    campaign_generation_config = "campaign_generation_config"
    campaign_summary = "campaign_summary"
    replay_spikes = "replay_spikes"
    voltage_report = "voltage_report"
    spike_report = "spike_report"
    neuron_mechanisms = "neuron_mechanisms"
    brain_atlas_annotation = "brain_atlas_annotation"
    brain_atlas_region_mesh = "brain_atlas_region_mesh"
    voxel_densities = "voxel_densities"
    validation_result_figure = "validation_result_figure"
    validation_result_details = "validation_result_details"
    simulation_designer_image = "simulation_designer_image"
    circuit_visualization = "circuit_visualization"
    node_stats = "node_stats"
    network_stats_a = "network_stats_a"
    network_stats_b = "network_stats_b"
    cell_surface_mesh = "cell_surface_mesh"
    jupyter_notebook = "jupyter_notebook"
    requirements = "requirements"
    ion_channel_model_figure = "ion_channel_model_figure"
    ion_channel_model_figure_summary_json = "ion_channel_model_figure_summary_json"
    ion_channel_model_thumbnail = "ion_channel_model_thumbnail"


class AssetStatus(StrEnum):
    created = "created"
    deleted = "deleted"


class Author(BaseModel):
    given_name: Annotated[str, Field(title="Given Name")]
    family_name: Annotated[str, Field(title="Family Name")]


class BodyUploadEntityAssetEntityRouteEntityIdAssetsPost(BaseModel):
    file: Annotated[bytes, Field(title="File")]
    label: AssetLabel
    meta: Annotated[dict[str, Any] | None, Field(title="Meta")] = None


class BrainRegionAdminUpdate(BaseModel):
    annotation_value: Annotated[int | str | None, Field(title="Annotation Value")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    acronym: Annotated[str | None, Field(title="Acronym")] = "<NOT_SET>"
    color_hex_triplet: Annotated[str | None, Field(title="Color Hex Triplet")] = "<NOT_SET>"
    parent_structure_id: Annotated[UUID | str | None, Field(title="Parent Structure Id")] = (
        "<NOT_SET>"
    )
    hierarchy_id: Annotated[UUID | str | None, Field(title="Hierarchy Id")] = "<NOT_SET>"


class BrainRegionCreate(BaseModel):
    annotation_value: Annotated[int, Field(title="Annotation Value")]
    name: Annotated[str, Field(title="Name")]
    acronym: Annotated[str, Field(title="Acronym")]
    color_hex_triplet: Annotated[str, Field(title="Color Hex Triplet")]
    parent_structure_id: Annotated[UUID | None, Field(title="Parent Structure Id")] = None
    hierarchy_id: Annotated[UUID, Field(title="Hierarchy Id")]


class BrainRegionRead(BaseModel):
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    annotation_value: Annotated[int, Field(title="Annotation Value")]
    name: Annotated[str, Field(title="Name")]
    acronym: Annotated[str, Field(title="Acronym")]
    color_hex_triplet: Annotated[str, Field(title="Color Hex Triplet")]
    parent_structure_id: Annotated[UUID | None, Field(title="Parent Structure Id")] = None
    hierarchy_id: Annotated[UUID, Field(title="Hierarchy Id")]


class CalibrationAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    start_time: Annotated[AwareDatetime | str | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[AwareDatetime | str | None, Field(title="End Time")] = "<NOT_SET>"
    used_ids: Annotated[list[UUID] | str | None, Field(title="Used Ids")] = "<NOT_SET>"
    generated_ids: Annotated[list[UUID] | str | None, Field(title="Generated Ids")] = "<NOT_SET>"


class CalibrationCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    start_time: Annotated[AwareDatetime | None, Field(title="Start Time")] = None
    end_time: Annotated[AwareDatetime | None, Field(title="End Time")] = None
    used_ids: Annotated[list[UUID] | None, Field(title="Used Ids")] = []
    generated_ids: Annotated[list[UUID] | None, Field(title="Generated Ids")] = []


class CellMorphologyGenerationType(StrEnum):
    digital_reconstruction = "digital_reconstruction"
    modified_reconstruction = "modified_reconstruction"
    computationally_synthesized = "computationally_synthesized"
    placeholder = "placeholder"


class CellMorphologyProtocolDesign(StrEnum):
    electron_microscopy = "electron_microscopy"
    cell_patch = "cell_patch"
    fluorophore = "fluorophore"


class CircuitBuildCategory(StrEnum):
    computational_model = "computational_model"
    em_reconstruction = "em_reconstruction"


class CircuitScale(StrEnum):
    single = "single"
    pair = "pair"
    small = "small"
    microcircuit = "microcircuit"
    region = "region"
    system = "system"
    whole_brain = "whole_brain"


class CircuitUserUpdate(BaseModel):
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    has_morphologies: Annotated[bool | str | None, Field(title="Has Morphologies")] = "<NOT_SET>"
    has_point_neurons: Annotated[bool | str | None, Field(title="Has Point Neurons")] = "<NOT_SET>"
    has_electrical_cell_models: Annotated[
        bool | str | None, Field(title="Has Electrical Cell Models")
    ] = "<NOT_SET>"
    has_spines: Annotated[bool | str | None, Field(title="Has Spines")] = "<NOT_SET>"
    number_neurons: Annotated[int | str | None, Field(title="Number Neurons")] = "<NOT_SET>"
    number_synapses: Annotated[int | str | None, Field(title="Number Synapses")] = "<NOT_SET>"
    number_connections: Annotated[int | str | None, Field(title="Number Connections")] = "<NOT_SET>"
    scale: Annotated[CircuitScale | str | None, Field(title="Scale")] = "<NOT_SET>"
    build_category: Annotated[CircuitBuildCategory | str | None, Field(title="Build Category")] = (
        "<NOT_SET>"
    )
    root_circuit_id: Annotated[UUID | str | None, Field(title="Root Circuit Id")] = "<NOT_SET>"
    atlas_id: Annotated[UUID | str | None, Field(title="Atlas Id")] = "<NOT_SET>"


class ProtocolDocument(RootModel[AnyUrl]):
    root: Annotated[AnyUrl, Field(title="Protocol Document")]


class ComputationallySynthesizedCellMorphologyProtocolCreate(BaseModel):
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    protocol_design: CellMorphologyProtocolDesign
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[
        Literal["computationally_synthesized"], Field(title="Generation Type")
    ]
    method_type: Annotated[str, Field(title="Method Type")]


class ConsortiumCreate(BaseModel):
    pref_label: Annotated[str, Field(title="Pref Label")]
    alternative_name: Annotated[str | None, Field(title="Alternative Name")] = None
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = None


class ContentType(StrEnum):
    application_json = "application/json"
    application_swc = "application/swc"
    application_nrrd = "application/nrrd"
    application_obj = "application/obj"
    application_hoc = "application/hoc"
    application_asc = "application/asc"
    application_abf = "application/abf"
    application_nwb = "application/nwb"
    application_x_hdf5 = "application/x-hdf5"
    text_plain = "text/plain"
    application_vnd_directory = "application/vnd.directory"
    application_mod = "application/mod"
    application_pdf = "application/pdf"
    image_png = "image/png"
    image_jpeg = "image/jpeg"
    model_gltf_binary = "model/gltf-binary"
    application_gzip = "application/gzip"
    image_webp = "image/webp"
    application_x_ipynb_json = "application/x-ipynb+json"


class ContributionCreate(BaseModel):
    agent_id: Annotated[UUID, Field(title="Agent Id")]
    role_id: Annotated[UUID, Field(title="Role Id")]
    entity_id: Annotated[UUID, Field(title="Entity Id")]


class DeleteResponse(BaseModel):
    id: Annotated[UUID, Field(title="Id")]


class DerivationType(StrEnum):
    circuit_extraction = "circuit_extraction"
    circuit_rewiring = "circuit_rewiring"
    unspecified = "unspecified"


class DetailedFile(BaseModel):
    name: Annotated[str, Field(title="Name")]
    size: Annotated[int, Field(title="Size")]
    last_modified: Annotated[AwareDatetime, Field(title="Last Modified")]


class DetailedFileList(BaseModel):
    files: Annotated[dict[str, DetailedFile], Field(title="Files")]


class Magnification(RootModel[float]):
    root: Annotated[float, Field(ge=0.0, title="Magnification")]


class TissueShrinkage(RootModel[float]):
    root: Annotated[float, Field(ge=0.0, title="Tissue Shrinkage")]


class DirectoryUpload(BaseModel):
    directory_name: Annotated[Path, Field(title="Directory Name")]
    files: Annotated[list[Path], Field(title="Files")]
    meta: Annotated[dict[str, Any] | None, Field(title="Meta")] = None
    label: AssetLabel


class DockerDependency(BaseModel):
    image_repository: Annotated[
        str, Field(examples=["openbraininstitute/obi-notebook-image"], title="Image Repository")
    ]
    image_tag: Annotated[str | None, Field(examples=[">=2025.09.24-2"], title="Image Tag")] = None
    image_digest: Annotated[
        str | None,
        Field(
            description="SHA256 digest",
            examples=["3406990b6e4c7192317b6fdc5680498744f6142f01f0287f4ee0420d8c74063c"],
            title="Image Digest",
        ),
    ] = None
    docker_version: Annotated[
        str | None, Field(examples=[">=20.10,<29.0"], title="Docker Version")
    ] = None


class DockerRuntimeInfo(BaseModel):
    image_repository: Annotated[
        str, Field(examples=["openbraininstitute/obi-notebook-image"], title="Image Repository")
    ]
    image_tag: Annotated[str, Field(examples=["2025.09.24-2"], title="Image Tag")]
    image_digest: Annotated[
        str | None,
        Field(
            description="SHA256 digest",
            examples=["3406990b6e4c7192317b6fdc5680498744f6142f01f0287f4ee0420d8c74063c"],
            title="Image Digest",
        ),
    ] = None
    docker_version: Annotated[str | None, Field(examples=["28.4.0"], title="Docker Version")] = None


class EMCellMeshGenerationMethod(StrEnum):
    marching_cubes = "marching_cubes"


class EMCellMeshType(StrEnum):
    static = "static"
    dynamic = "dynamic"


class EMCellMeshUserUpdate(BaseModel):
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    release_version: Annotated[int | str | None, Field(title="Release Version")] = "<NOT_SET>"
    dense_reconstruction_cell_id: Annotated[
        int | str | None, Field(title="Dense Reconstruction Cell Id")
    ] = "<NOT_SET>"
    generation_method: Annotated[
        EMCellMeshGenerationMethod | str | None, Field(title="Generation Method")
    ] = "<NOT_SET>"
    level_of_detail: Annotated[int | str | None, Field(title="Level Of Detail")] = "<NOT_SET>"
    generation_parameters: Annotated[
        dict[str, Any] | str | None, Field(title="Generation Parameters")
    ] = "<NOT_SET>"
    mesh_type: Annotated[EMCellMeshType | str | None, Field(title="Mesh Type")] = "<NOT_SET>"
    em_dense_reconstruction_dataset_id: Annotated[
        UUID | str | None, Field(title="Em Dense Reconstruction Dataset Id")
    ] = "<NOT_SET>"


class EModelAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    iteration: Annotated[str | None, Field(title="Iteration")] = "<NOT_SET>"
    score: Annotated[float | str | None, Field(title="Score")] = "<NOT_SET>"
    seed: Annotated[int | str | None, Field(title="Seed")] = "<NOT_SET>"
    species_id: Annotated[UUID | str | None, Field(title="Species Id")] = "<NOT_SET>"
    strain_id: Annotated[UUID | str | None, Field(title="Strain Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    exemplar_morphology_id: Annotated[UUID | str | None, Field(title="Exemplar Morphology Id")] = (
        "<NOT_SET>"
    )


class EModelCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    description: Annotated[str, Field(title="Description")]
    name: Annotated[str, Field(title="Name")]
    iteration: Annotated[str, Field(title="Iteration")]
    score: Annotated[float, Field(title="Score")]
    seed: Annotated[int, Field(title="Seed")]
    species_id: Annotated[UUID, Field(title="Species Id")]
    strain_id: Annotated[UUID | None, Field(title="Strain Id")] = None
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    exemplar_morphology_id: Annotated[UUID, Field(title="Exemplar Morphology Id")]


class EModelUserUpdate(BaseModel):
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    iteration: Annotated[str | None, Field(title="Iteration")] = "<NOT_SET>"
    score: Annotated[float | str | None, Field(title="Score")] = "<NOT_SET>"
    seed: Annotated[int | str | None, Field(title="Seed")] = "<NOT_SET>"
    species_id: Annotated[UUID | str | None, Field(title="Species Id")] = "<NOT_SET>"
    strain_id: Annotated[UUID | str | None, Field(title="Strain Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    exemplar_morphology_id: Annotated[UUID | str | None, Field(title="Exemplar Morphology Id")] = (
        "<NOT_SET>"
    )


class ETypeClassificationCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    entity_id: Annotated[UUID, Field(title="Entity Id")]
    etype_class_id: Annotated[UUID, Field(title="Etype Class Id")]


class ElectricalRecordingOrigin(StrEnum):
    in_vivo = "in_vivo"
    in_vitro = "in_vitro"
    in_silico = "in_silico"
    unknown = "unknown"


class ElectricalRecordingStimulusShape(StrEnum):
    cheops = "cheops"
    constant = "constant"
    pulse = "pulse"
    step = "step"
    ramp = "ramp"
    noise = "noise"
    sinusoidal = "sinusoidal"
    other = "other"
    two_steps = "two_steps"
    unknown = "unknown"


class ElectricalRecordingStimulusType(StrEnum):
    voltage_clamp = "voltage_clamp"
    current_clamp = "current_clamp"
    conductance_clamp = "conductance_clamp"
    extracellular = "extracellular"
    other = "other"
    unknown = "unknown"


class ElectricalRecordingStimulusUserUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    dt: Annotated[float | str | None, Field(title="Dt")] = "<NOT_SET>"
    injection_type: Annotated[
        ElectricalRecordingStimulusType | str | None, Field(title="Injection Type")
    ] = "<NOT_SET>"
    shape: Annotated[ElectricalRecordingStimulusShape | str | None, Field(title="Shape")] = (
        "<NOT_SET>"
    )
    start_time: Annotated[float | str | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[float | str | None, Field(title="End Time")] = "<NOT_SET>"
    recording_id: Annotated[UUID | str | None, Field(title="Recording Id")] = "<NOT_SET>"


class ElectricalRecordingType(StrEnum):
    intracellular = "intracellular"
    extracellular = "extracellular"
    both = "both"
    unknown = "unknown"


class EntityCountRead(RootModel[dict[str, int]]):
    root: dict[str, int]


class EntityRoute(StrEnum):
    analysis_software_source_code = "analysis-software-source-code"
    brain_atlas = "brain-atlas"
    brain_atlas_region = "brain-atlas-region"
    cell_composition = "cell-composition"
    cell_morphology = "cell-morphology"
    cell_morphology_protocol = "cell-morphology-protocol"
    electrical_cell_recording = "electrical-cell-recording"
    electrical_recording = "electrical-recording"
    electrical_recording_stimulus = "electrical-recording-stimulus"
    emodel = "emodel"
    experimental_bouton_density = "experimental-bouton-density"
    experimental_neuron_density = "experimental-neuron-density"
    experimental_synapses_per_connection = "experimental-synapses-per-connection"
    external_url = "external-url"
    ion_channel_model = "ion-channel-model"
    ion_channel_recording = "ion-channel-recording"
    memodel = "memodel"
    memodel_calibration_result = "memodel-calibration-result"
    me_type_density = "me-type-density"
    simulation = "simulation"
    simulation_campaign = "simulation-campaign"
    simulation_result = "simulation-result"
    scientific_artifact = "scientific-artifact"
    single_neuron_simulation = "single-neuron-simulation"
    single_neuron_synaptome = "single-neuron-synaptome"
    single_neuron_synaptome_simulation = "single-neuron-synaptome-simulation"
    subject = "subject"
    validation_result = "validation-result"
    circuit = "circuit"
    em_dense_reconstruction_dataset = "em-dense-reconstruction-dataset"
    em_cell_mesh = "em-cell-mesh"
    analysis_notebook_template = "analysis-notebook-template"
    analysis_notebook_environment = "analysis-notebook-environment"
    analysis_notebook_result = "analysis-notebook-result"


class EntityType(StrEnum):
    analysis_software_source_code = "analysis_software_source_code"
    brain_atlas = "brain_atlas"
    brain_atlas_region = "brain_atlas_region"
    cell_composition = "cell_composition"
    cell_morphology = "cell_morphology"
    cell_morphology_protocol = "cell_morphology_protocol"
    electrical_cell_recording = "electrical_cell_recording"
    electrical_recording = "electrical_recording"
    electrical_recording_stimulus = "electrical_recording_stimulus"
    emodel = "emodel"
    experimental_bouton_density = "experimental_bouton_density"
    experimental_neuron_density = "experimental_neuron_density"
    experimental_synapses_per_connection = "experimental_synapses_per_connection"
    external_url = "external_url"
    ion_channel_model = "ion_channel_model"
    ion_channel_recording = "ion_channel_recording"
    memodel = "memodel"
    memodel_calibration_result = "memodel_calibration_result"
    me_type_density = "me_type_density"
    simulation = "simulation"
    simulation_campaign = "simulation_campaign"
    simulation_result = "simulation_result"
    scientific_artifact = "scientific_artifact"
    single_neuron_simulation = "single_neuron_simulation"
    single_neuron_synaptome = "single_neuron_synaptome"
    single_neuron_synaptome_simulation = "single_neuron_synaptome_simulation"
    subject = "subject"
    validation_result = "validation_result"
    circuit = "circuit"
    em_dense_reconstruction_dataset = "em_dense_reconstruction_dataset"
    em_cell_mesh = "em_cell_mesh"
    analysis_notebook_template = "analysis_notebook_template"
    analysis_notebook_environment = "analysis_notebook_environment"
    analysis_notebook_result = "analysis_notebook_result"


class EntityTypeWithBrainRegion(StrEnum):
    brain_atlas_region = "brain_atlas_region"
    cell_composition = "cell_composition"
    cell_morphology = "cell_morphology"
    circuit = "circuit"
    electrical_cell_recording = "electrical_cell_recording"
    electrical_recording = "electrical_recording"
    em_cell_mesh = "em_cell_mesh"
    em_dense_reconstruction_dataset = "em_dense_reconstruction_dataset"
    emodel = "emodel"
    experimental_bouton_density = "experimental_bouton_density"
    experimental_neuron_density = "experimental_neuron_density"
    experimental_synapses_per_connection = "experimental_synapses_per_connection"
    ion_channel_model = "ion_channel_model"
    ion_channel_recording = "ion_channel_recording"
    me_type_density = "me_type_density"
    memodel = "memodel"
    scientific_artifact = "scientific_artifact"
    single_neuron_simulation = "single_neuron_simulation"
    single_neuron_synaptome = "single_neuron_synaptome"
    single_neuron_synaptome_simulation = "single_neuron_synaptome_simulation"


class ErrorResponse(BaseModel):
    error_code: ApiErrorCode
    message: Annotated[str, Field(title="Message")]
    details: Annotated[Any | None, Field(title="Details")] = None


class ExternalSource(StrEnum):
    channelpedia = "channelpedia"
    modeldb = "modeldb"
    icgenealogy = "icgenealogy"


class ExternalUrlCreate(BaseModel):
    source: ExternalSource
    url: Annotated[AnyUrl, Field(title="Url")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]


class Facet(BaseModel):
    id: Annotated[UUID | int, Field(title="Id")]
    label: Annotated[str, Field(title="Label")]
    count: Annotated[int, Field(title="Count")]
    type: Annotated[str | None, Field(title="Type")] = None


class Facets(RootModel[dict[str, list[Facet]]]):
    root: dict[str, list[Facet]]


class HierarchyNode(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[str, Field(title="Name")]
    parent_id: Annotated[UUID | None, Field(title="Parent Id")] = None
    children: Annotated[list[HierarchyNode] | None, Field(title="Children")] = []
    authorized_public: Annotated[bool, Field(title="Authorized Public")]
    authorized_project_id: Annotated[UUID, Field(title="Authorized Project Id")]


class HierarchyTree(BaseModel):
    derivation_type: DerivationType
    data: Annotated[list[HierarchyNode], Field(title="Data")]


class IonChannelAdminUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    label: Annotated[str | None, Field(title="Label")] = "<NOT_SET>"
    gene: Annotated[str | None, Field(title="Gene")] = "<NOT_SET>"
    synonyms: Annotated[list[str] | str | None, Field(title="Synonyms")] = "<NOT_SET>"


class IonChannelCreate(BaseModel):
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    label: Annotated[str, Field(title="Label")]
    gene: Annotated[str, Field(title="Gene")]
    synonyms: Annotated[list[str], Field(title="Synonyms")]


class IonChannelRecordingAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    ljp: Annotated[float | str | None, Field(title="Ljp")] = "<NOT_SET>"
    recording_location: Annotated[list[str] | str | None, Field(title="Recording Location")] = (
        "<NOT_SET>"
    )
    recording_type: Annotated[
        ElectricalRecordingType | str | None, Field(title="Recording Type")
    ] = "<NOT_SET>"
    recording_origin: Annotated[
        ElectricalRecordingOrigin | str | None, Field(title="Recording Origin")
    ] = "<NOT_SET>"
    temperature: Annotated[float | str | None, Field(title="Temperature")] = "<NOT_SET>"
    comment: Annotated[str | None, Field(title="Comment")] = "<NOT_SET>"
    legacy_id: Annotated[list[str] | str | None, Field(title="Legacy Id")] = "<NOT_SET>"
    cell_line: Annotated[str | None, Field(title="Cell Line")] = "<NOT_SET>"
    ion_channel_id: Annotated[UUID | str | None, Field(title="Ion Channel Id")] = "<NOT_SET>"


class IonChannelRecordingCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license_id: Annotated[UUID | None, Field(title="License Id")] = None
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    subject_id: Annotated[UUID, Field(title="Subject Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    ljp: Annotated[
        float | None,
        Field(
            description="Correction applied to the voltage trace, in mV",
            title="Liquid Junction Potential",
        ),
    ] = 0.0
    recording_location: Annotated[
        list[str],
        Field(
            description="Location on the cell where recording was performed, in hoc-compatible format.",
            title="Recording Location",
        ),
    ]
    recording_type: Annotated[
        ElectricalRecordingType,
        Field(
            description="Recording type. One of: [<ElectricalRecordingStimulusType.conductance_clamp: 'conductance_clamp'>, <ElectricalRecordingStimulusType.current_clamp: 'current_clamp'>, <ElectricalRecordingStimulusType.extracellular: 'extracellular'>, <ElectricalRecordingStimulusType.other: 'other'>, <ElectricalRecordingStimulusType.unknown: 'unknown'>, <ElectricalRecordingStimulusType.voltage_clamp: 'voltage_clamp'>]",
            title="Recording Type",
        ),
    ]
    recording_origin: Annotated[
        ElectricalRecordingOrigin,
        Field(
            description="Recording origin. One of: [<ElectricalRecordingOrigin.in_silico: 'in_silico'>, <ElectricalRecordingOrigin.in_vitro: 'in_vitro'>, <ElectricalRecordingOrigin.in_vivo: 'in_vivo'>, <ElectricalRecordingOrigin.unknown: 'unknown'>]",
            title="Recording Origin",
        ),
    ]
    temperature: Annotated[
        float | None,
        Field(
            description="Temperature at which the recording was performed, in degrees Celsius.",
            title="Temperature",
        ),
    ] = None
    comment: Annotated[
        str | None, Field(description="Comment with further details.", title="Comment")
    ] = None
    legacy_id: Annotated[list[str] | None, Field(title="Legacy Id")] = None
    cell_line: Annotated[
        str,
        Field(
            description="The cell line from which the ion channel was recorded", title="Cell Line"
        ),
    ]
    ion_channel_id: Annotated[
        UUID,
        Field(
            description="The id of the ion channel that was recorded from", title="Ion Channel ID"
        ),
    ]


class IonChannelRecordingUserUpdate(BaseModel):
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    ljp: Annotated[float | str | None, Field(title="Ljp")] = "<NOT_SET>"
    recording_location: Annotated[list[str] | str | None, Field(title="Recording Location")] = (
        "<NOT_SET>"
    )
    recording_type: Annotated[
        ElectricalRecordingType | str | None, Field(title="Recording Type")
    ] = "<NOT_SET>"
    recording_origin: Annotated[
        ElectricalRecordingOrigin | str | None, Field(title="Recording Origin")
    ] = "<NOT_SET>"
    temperature: Annotated[float | str | None, Field(title="Temperature")] = "<NOT_SET>"
    comment: Annotated[str | None, Field(title="Comment")] = "<NOT_SET>"
    legacy_id: Annotated[list[str] | str | None, Field(title="Legacy Id")] = "<NOT_SET>"
    cell_line: Annotated[str | None, Field(title="Cell Line")] = "<NOT_SET>"
    ion_channel_id: Annotated[UUID | str | None, Field(title="Ion Channel Id")] = "<NOT_SET>"


class LicenseAdminUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    label: Annotated[str | None, Field(title="Label")] = "<NOT_SET>"


class LicenseCreate(BaseModel):
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    label: Annotated[str, Field(title="Label")]


class LicenseRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    label: Annotated[str, Field(title="Label")]


class MEModelCalibrationResultAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    holding_current: Annotated[float | str | None, Field(title="Holding Current")] = "<NOT_SET>"
    threshold_current: Annotated[float | str | None, Field(title="Threshold Current")] = "<NOT_SET>"
    rin: Annotated[float | str | None, Field(title="Rin")] = "<NOT_SET>"
    calibrated_entity_id: Annotated[UUID | str | None, Field(title="Calibrated Entity Id")] = (
        "<NOT_SET>"
    )


class MEModelCalibrationResultCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    holding_current: Annotated[float, Field(title="Holding Current")]
    threshold_current: Annotated[float, Field(title="Threshold Current")]
    rin: Annotated[float | None, Field(title="Rin")] = None
    calibrated_entity_id: Annotated[UUID, Field(title="Calibrated Entity Id")]


class MEModelCalibrationResultUserUpdate(BaseModel):
    holding_current: Annotated[float | str | None, Field(title="Holding Current")] = "<NOT_SET>"
    threshold_current: Annotated[float | str | None, Field(title="Threshold Current")] = "<NOT_SET>"
    rin: Annotated[float | str | None, Field(title="Rin")] = "<NOT_SET>"
    calibrated_entity_id: Annotated[UUID | str | None, Field(title="Calibrated Entity Id")] = (
        "<NOT_SET>"
    )


class MTypeClassificationCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    entity_id: Annotated[UUID, Field(title="Entity Id")]
    mtype_class_id: Annotated[UUID, Field(title="Mtype Class Id")]


class MeasurableEntity(StrEnum):
    cell_morphology = "cell_morphology"


class MeasurementStatistic(StrEnum):
    mean = "mean"
    median = "median"
    mode = "mode"
    variance = "variance"
    data_point = "data_point"
    sample_size = "sample_size"
    standard_error = "standard_error"
    standard_deviation = "standard_deviation"
    raw = "raw"
    minimum = "minimum"
    maximum = "maximum"
    sum = "sum"


class MeasurementUnit(StrEnum):
    dimensionless = "dimensionless"
    field_1_μm = "1/μm"
    field_1_mm_ = "1/mm³"
    μm = "μm"
    μm_ = "μm²"
    μm__1 = "μm³"
    radian = "radian"


class ModifiedMorphologyMethodType(StrEnum):
    cloned = "cloned"
    mix_and_match = "mix_and_match"
    mousified = "mousified"
    ratified = "ratified"


class ModifiedReconstructionCellMorphologyProtocolCreate(BaseModel):
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    protocol_design: CellMorphologyProtocolDesign
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[Literal["modified_reconstruction"], Field(title="Generation Type")]
    method_type: ModifiedMorphologyMethodType


class NestedComputationallySynthesizedCellMorphologyProtocolRead(BaseModel):
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    protocol_design: CellMorphologyProtocolDesign
    id: Annotated[UUID, Field(title="Id")]
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[
        Literal["computationally_synthesized"], Field(title="Generation Type")
    ]
    method_type: Annotated[str, Field(title="Method Type")]


class NestedConsortiumRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    pref_label: Annotated[str, Field(title="Pref Label")]
    alternative_name: Annotated[str | None, Field(title="Alternative Name")] = None
    type: Annotated[str, Field(title="Type")]


class NestedElectricalRecordingStimulusRead(BaseModel):
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    dt: Annotated[float | None, Field(title="Dt")] = None
    injection_type: ElectricalRecordingStimulusType
    shape: ElectricalRecordingStimulusShape
    start_time: Annotated[float | None, Field(title="Start Time")] = None
    end_time: Annotated[float | None, Field(title="End Time")] = None
    recording_id: Annotated[UUID, Field(title="Recording Id")]


class NestedEntityRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    type: Annotated[str, Field(title="Type")]
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool, Field(title="Authorized Public")]


class NestedExternalUrlRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    source: ExternalSource
    url: Annotated[AnyUrl, Field(title="Url")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    source_name: Annotated[str, Field(title="Source Name")]


class NestedIonChannelRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    label: Annotated[str, Field(title="Label")]
    gene: Annotated[str, Field(title="Gene")]
    synonyms: Annotated[list[str], Field(title="Synonyms")]


class NestedModifiedReconstructionCellMorphologyProtocolRead(BaseModel):
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    protocol_design: CellMorphologyProtocolDesign
    id: Annotated[UUID, Field(title="Id")]
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[Literal["modified_reconstruction"], Field(title="Generation Type")]
    method_type: ModifiedMorphologyMethodType


class NestedOrganizationRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    pref_label: Annotated[str, Field(title="Pref Label")]
    alternative_name: Annotated[str | None, Field(title="Alternative Name")] = None
    type: Annotated[str, Field(title="Type")]


class NestedPersonRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    given_name: Annotated[str | None, Field(title="Given Name")] = None
    family_name: Annotated[str | None, Field(title="Family Name")] = None
    pref_label: Annotated[str, Field(title="Pref Label")]
    type: Annotated[str, Field(title="Type")]
    sub_id: Annotated[UUID | None, Field(title="Sub Id")] = None


class NestedPlaceholderCellMorphologyProtocolRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[Literal["placeholder"], Field(title="Generation Type")]


class NestedPublicationRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    DOI: Annotated[str, Field(title="Doi")]
    title: Annotated[str | None, Field(title="Title")] = None
    authors: Annotated[list[Author] | None, Field(title="Authors")] = None
    publication_year: Annotated[int | None, Field(title="Publication Year")] = None
    abstract: Annotated[str | None, Field(title="Abstract")] = None


class NestedScientificArtifactRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None


class NestedSimulationRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    type: EntityType | None = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    simulation_campaign_id: Annotated[UUID, Field(title="Simulation Campaign Id")]
    entity_id: Annotated[UUID, Field(title="Entity Id")]
    scan_parameters: Annotated[dict[str, Any], Field(title="Scan Parameters")]


class NestedSpeciesRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[str, Field(title="Name")]
    taxonomy_id: Annotated[str, Field(title="Taxonomy Id")]


class NestedStrainRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[str, Field(title="Name")]
    taxonomy_id: Annotated[str, Field(title="Taxonomy Id")]
    species_id: Annotated[UUID, Field(title="Species Id")]


class Weight(RootModel[float]):
    root: Annotated[float, Field(description="Weight in grams", gt=0.0, title="Weight")]


class NestedSynaptome(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    seed: Annotated[int, Field(title="Seed")]


class NotSet(RootModel[Literal["<NOT_SET>"]]):
    root: Literal["<NOT_SET>"]


class OrganizationCreate(BaseModel):
    pref_label: Annotated[str, Field(title="Pref Label")]
    alternative_name: Annotated[str | None, Field(title="Alternative Name")] = None
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = None


class OrganizationRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    pref_label: Annotated[str, Field(title="Pref Label")]
    alternative_name: Annotated[str | None, Field(title="Alternative Name")] = None
    type: Annotated[str, Field(title="Type")]


class OsRuntimeInfo(BaseModel):
    system: Annotated[
        str, Field(description="Output of `platform.system()`", examples=["Linux"], title="System")
    ]
    release: Annotated[
        str,
        Field(
            description="Output of `platform.release()`",
            examples=["5.14.0-427.28.1.el9_4.x86_64"],
            title="Release",
        ),
    ]
    version: Annotated[
        str,
        Field(
            description="Output of `platform.version()`",
            examples=["#1 SMP PREEMPT_DYNAMIC Fri Aug 2 03:44:10 EDT 2024"],
            title="Version",
        ),
    ]
    machine: Annotated[
        str,
        Field(description="Output of `platform.machine()`", examples=["x86_64"], title="Machine"),
    ]
    processor: Annotated[
        str,
        Field(
            description="Output of `platform.processor()`", examples=["x86_64"], title="Processor"
        ),
    ]


class PaginationResponse(BaseModel):
    page: Annotated[int, Field(title="Page")]
    page_size: Annotated[int, Field(title="Page Size")]
    total_items: Annotated[int, Field(title="Total Items")]


class PersonCreate(BaseModel):
    given_name: Annotated[str | None, Field(title="Given Name")] = None
    family_name: Annotated[str | None, Field(title="Family Name")] = None
    pref_label: Annotated[str, Field(title="Pref Label")]
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = None


class PersonRead(BaseModel):
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    given_name: Annotated[str | None, Field(title="Given Name")] = None
    family_name: Annotated[str | None, Field(title="Family Name")] = None
    pref_label: Annotated[str, Field(title="Pref Label")]
    type: Annotated[str, Field(title="Type")]
    sub_id: Annotated[UUID | None, Field(title="Sub Id")] = None


class PlaceholderCellMorphologyProtocolCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[Literal["placeholder"], Field(title="Generation Type")]


class PlaceholderCellMorphologyProtocolRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[Literal["placeholder"], Field(title="Generation Type")]


class PointLocationBase(BaseModel):
    x: Annotated[float, Field(title="X")]
    y: Annotated[float, Field(title="Y")]
    z: Annotated[float, Field(title="Z")]


class PublicationAdminUpdate(BaseModel):
    DOI: Annotated[str | None, Field(title="Doi")] = "<NOT_SET>"
    title: Annotated[str | None, Field(title="Title")] = "<NOT_SET>"
    authors: Annotated[list[Author] | str | None, Field(title="Authors")] = "<NOT_SET>"
    publication_year: Annotated[int | str | None, Field(title="Publication Year")] = "<NOT_SET>"
    abstract: Annotated[str | None, Field(title="Abstract")] = "<NOT_SET>"


class PublicationCreate(BaseModel):
    DOI: Annotated[str, Field(title="Doi")]
    title: Annotated[str | None, Field(title="Title")] = None
    authors: Annotated[list[Author] | None, Field(title="Authors")] = None
    publication_year: Annotated[int | None, Field(title="Publication Year")] = None
    abstract: Annotated[str | None, Field(title="Abstract")] = None


class PublicationRead(BaseModel):
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    DOI: Annotated[str, Field(title="Doi")]
    title: Annotated[str | None, Field(title="Title")] = None
    authors: Annotated[list[Author] | None, Field(title="Authors")] = None
    publication_year: Annotated[int | None, Field(title="Publication Year")] = None
    abstract: Annotated[str | None, Field(title="Abstract")] = None


class PublicationType(StrEnum):
    entity_source = "entity_source"
    component_source = "component_source"
    application = "application"


class PythonDependency(BaseModel):
    version: Annotated[str, Field(examples=[">=3.10,<3.12"], title="Version")]


class PythonRuntimeInfo(BaseModel):
    version: Annotated[
        str,
        Field(
            description="Output of `platform.python_version()`",
            examples=["3.9.21"],
            title="Version",
        ),
    ]
    implementation: Annotated[
        str,
        Field(
            description="Output of `platform.python_implementation()`",
            examples=["CPython"],
            title="Implementation",
        ),
    ]
    executable: Annotated[
        str,
        Field(
            description="Output of `sys.executable`",
            examples=["/usr/bin/python"],
            title="Executable",
        ),
    ]


class ResourceRoute(StrEnum):
    analysis_notebook_environment = "analysis-notebook-environment"
    analysis_notebook_execution = "analysis-notebook-execution"
    analysis_notebook_result = "analysis-notebook-result"
    analysis_notebook_template = "analysis-notebook-template"
    analysis_software_source_code = "analysis-software-source-code"
    brain_atlas = "brain-atlas"
    brain_atlas_region = "brain-atlas-region"
    brain_region = "brain-region"
    brain_region_hierarchy = "brain-region-hierarchy"
    calibration = "calibration"
    cell_composition = "cell-composition"
    cell_morphology = "cell-morphology"
    cell_morphology_protocol = "cell-morphology-protocol"
    circuit = "circuit"
    consortium = "consortium"
    contribution = "contribution"
    derivation = "derivation"
    electrical_cell_recording = "electrical-cell-recording"
    electrical_recording = "electrical-recording"
    electrical_recording_stimulus = "electrical-recording-stimulus"
    em_cell_mesh = "em-cell-mesh"
    em_dense_reconstruction_dataset = "em-dense-reconstruction-dataset"
    emodel = "emodel"
    etype = "etype"
    etype_classification = "etype-classification"
    experimental_bouton_density = "experimental-bouton-density"
    experimental_neuron_density = "experimental-neuron-density"
    experimental_synapses_per_connection = "experimental-synapses-per-connection"
    external_url = "external-url"
    ion = "ion"
    ion_channel = "ion-channel"
    ion_channel_model = "ion-channel-model"
    ion_channel_recording = "ion-channel-recording"
    license = "license"
    me_type_density = "me-type-density"
    measurement_annotation = "measurement-annotation"
    memodel = "memodel"
    memodel_calibration_result = "memodel-calibration-result"
    mtype = "mtype"
    mtype_classification = "mtype-classification"
    organization = "organization"
    person = "person"
    publication = "publication"
    role = "role"
    scientific_artifact = "scientific-artifact"
    scientific_artifact_external_url_link = "scientific-artifact-external-url-link"
    scientific_artifact_publication_link = "scientific-artifact-publication-link"
    simulation = "simulation"
    simulation_campaign = "simulation-campaign"
    simulation_execution = "simulation-execution"
    simulation_generation = "simulation-generation"
    simulation_result = "simulation-result"
    single_neuron_simulation = "single-neuron-simulation"
    single_neuron_synaptome = "single-neuron-synaptome"
    single_neuron_synaptome_simulation = "single-neuron-synaptome-simulation"
    species = "species"
    strain = "strain"
    subject = "subject"
    validation = "validation"
    validation_result = "validation-result"


class RoleAdminUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    role_id: Annotated[str | None, Field(title="Role Id")] = "<NOT_SET>"


class RoleCreate(BaseModel):
    name: Annotated[str, Field(title="Name")]
    role_id: Annotated[str, Field(title="Role Id")]


class RoleRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    role_id: Annotated[str, Field(title="Role Id")]


class RuntimeInfo(BaseModel):
    schema_version: Annotated[int | None, Field(title="Schema Version")] = 1
    python: PythonRuntimeInfo
    docker: DockerRuntimeInfo | None = None
    os: OsRuntimeInfo | None = None


class ScientificArtifactExternalUrlLinkCreate(BaseModel):
    external_url_id: Annotated[UUID, Field(title="External Url Id")]
    scientific_artifact_id: Annotated[UUID, Field(title="Scientific Artifact Id")]


class ScientificArtifactExternalUrlLinkRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    external_url: NestedExternalUrlRead
    scientific_artifact: NestedScientificArtifactRead


class ScientificArtifactPublicationLinkCreate(BaseModel):
    publication_type: PublicationType
    publication_id: Annotated[UUID, Field(title="Publication Id")]
    scientific_artifact_id: Annotated[UUID, Field(title="Scientific Artifact Id")]


class ScientificArtifactPublicationLinkRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    publication_type: PublicationType
    publication: NestedPublicationRead
    scientific_artifact: NestedScientificArtifactRead


class Sex(StrEnum):
    male = "male"
    female = "female"
    unknown = "unknown"


class SimulationAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    simulation_campaign_id: Annotated[UUID | str | None, Field(title="Simulation Campaign Id")] = (
        "<NOT_SET>"
    )
    entity_id: Annotated[UUID | str | None, Field(title="Entity Id")] = "<NOT_SET>"
    scan_parameters: Annotated[dict[str, Any] | str | None, Field(title="Scan Parameters")] = (
        "<NOT_SET>"
    )


class SimulationCampaignAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    scan_parameters: Annotated[dict[str, Any] | str | None, Field(title="Scan Parameters")] = (
        "<NOT_SET>"
    )
    entity_id: Annotated[UUID | str | None, Field(title="Entity Id")] = "<NOT_SET>"


class SimulationCampaignCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    scan_parameters: Annotated[dict[str, Any], Field(title="Scan Parameters")]
    entity_id: Annotated[UUID, Field(title="Entity Id")]


class SimulationCampaignUserUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    scan_parameters: Annotated[dict[str, Any] | str | None, Field(title="Scan Parameters")] = (
        "<NOT_SET>"
    )
    entity_id: Annotated[UUID | str | None, Field(title="Entity Id")] = "<NOT_SET>"


class SimulationCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    simulation_campaign_id: Annotated[UUID, Field(title="Simulation Campaign Id")]
    entity_id: Annotated[UUID, Field(title="Entity Id")]
    scan_parameters: Annotated[dict[str, Any], Field(title="Scan Parameters")]


class SimulationExecutionStatus(StrEnum):
    created = "created"
    pending = "pending"
    running = "running"
    done = "done"
    error = "error"


class SimulationExecutionUserUpdate(BaseModel):
    start_time: Annotated[AwareDatetime | NotSet | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[AwareDatetime | NotSet | None, Field(title="End Time")] = "<NOT_SET>"
    generated_ids: Annotated[list[UUID] | NotSet | None, Field(title="Generated Ids")] = "<NOT_SET>"
    status: SimulationExecutionStatus | None = None


class SimulationGenerationAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    start_time: Annotated[AwareDatetime | str | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[AwareDatetime | str | None, Field(title="End Time")] = "<NOT_SET>"
    used_ids: Annotated[list[UUID] | str | None, Field(title="Used Ids")] = "<NOT_SET>"
    generated_ids: Annotated[list[UUID] | str | None, Field(title="Generated Ids")] = "<NOT_SET>"


class SimulationGenerationCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    start_time: Annotated[AwareDatetime | None, Field(title="Start Time")] = None
    end_time: Annotated[AwareDatetime | None, Field(title="End Time")] = None
    used_ids: Annotated[list[UUID] | None, Field(title="Used Ids")] = []
    generated_ids: Annotated[list[UUID] | None, Field(title="Generated Ids")] = []


class SimulationGenerationRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    id: Annotated[UUID, Field(title="Id")]
    type: ActivityType | None = None
    start_time: Annotated[AwareDatetime | None, Field(title="Start Time")] = None
    end_time: Annotated[AwareDatetime | None, Field(title="End Time")] = None
    used: Annotated[list[NestedEntityRead], Field(title="Used")]
    generated: Annotated[list[NestedEntityRead], Field(title="Generated")]


class SimulationGenerationUserUpdate(BaseModel):
    start_time: Annotated[AwareDatetime | NotSet | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[AwareDatetime | NotSet | None, Field(title="End Time")] = "<NOT_SET>"
    generated_ids: Annotated[list[UUID] | NotSet | None, Field(title="Generated Ids")] = "<NOT_SET>"


class SimulationResultAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    simulation_id: Annotated[UUID | str | None, Field(title="Simulation Id")] = "<NOT_SET>"


class SimulationResultCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    simulation_id: Annotated[UUID, Field(title="Simulation Id")]


class SimulationResultUserUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    simulation_id: Annotated[UUID | str | None, Field(title="Simulation Id")] = "<NOT_SET>"


class SimulationUserUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    simulation_campaign_id: Annotated[UUID | str | None, Field(title="Simulation Campaign Id")] = (
        "<NOT_SET>"
    )
    entity_id: Annotated[UUID | str | None, Field(title="Entity Id")] = "<NOT_SET>"
    scan_parameters: Annotated[dict[str, Any] | str | None, Field(title="Scan Parameters")] = (
        "<NOT_SET>"
    )


class SingleNeuronSimulationStatus(StrEnum):
    started = "started"
    failure = "failure"
    success = "success"


class SingleNeuronSimulationUserUpdate(BaseModel):
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    seed: Annotated[int | str | None, Field(title="Seed")] = "<NOT_SET>"
    status: Annotated[SingleNeuronSimulationStatus | str | None, Field(title="Status")] = (
        "<NOT_SET>"
    )
    injection_location: Annotated[list[str] | str | None, Field(title="Injection Location")] = (
        "<NOT_SET>"
    )
    recording_location: Annotated[list[str] | str | None, Field(title="Recording Location")] = (
        "<NOT_SET>"
    )
    me_model_id: Annotated[UUID | str | None, Field(title="Me Model Id")] = "<NOT_SET>"


class SingleNeuronSynaptomeAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    seed: Annotated[int | str | None, Field(title="Seed")] = "<NOT_SET>"
    me_model_id: Annotated[UUID | str | None, Field(title="Me Model Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"


class SingleNeuronSynaptomeCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    seed: Annotated[int, Field(title="Seed")]
    me_model_id: Annotated[UUID, Field(title="Me Model Id")]
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]


class SingleNeuronSynaptomeSimulationAdminUpdate(BaseModel):
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    seed: Annotated[int | str | None, Field(title="Seed")] = "<NOT_SET>"
    status: Annotated[SingleNeuronSimulationStatus | str | None, Field(title="Status")] = (
        "<NOT_SET>"
    )
    injection_location: Annotated[list[str] | str | None, Field(title="Injection Location")] = (
        "<NOT_SET>"
    )
    recording_location: Annotated[list[str] | str | None, Field(title="Recording Location")] = (
        "<NOT_SET>"
    )
    synaptome_id: Annotated[UUID | str | None, Field(title="Synaptome Id")] = "<NOT_SET>"


class SingleNeuronSynaptomeSimulationCreate(BaseModel):
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    seed: Annotated[int, Field(title="Seed")]
    status: SingleNeuronSimulationStatus
    injection_location: Annotated[list[str], Field(title="Injection Location")]
    recording_location: Annotated[list[str], Field(title="Recording Location")]
    synaptome_id: Annotated[UUID, Field(title="Synaptome Id")]


class SingleNeuronSynaptomeSimulationUserUpdate(BaseModel):
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    seed: Annotated[int | str | None, Field(title="Seed")] = "<NOT_SET>"
    status: Annotated[SingleNeuronSimulationStatus | str | None, Field(title="Status")] = (
        "<NOT_SET>"
    )
    injection_location: Annotated[list[str] | str | None, Field(title="Injection Location")] = (
        "<NOT_SET>"
    )
    recording_location: Annotated[list[str] | str | None, Field(title="Recording Location")] = (
        "<NOT_SET>"
    )
    synaptome_id: Annotated[UUID | str | None, Field(title="Synaptome Id")] = "<NOT_SET>"


class SingleNeuronSynaptomeUserUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    seed: Annotated[int | str | None, Field(title="Seed")] = "<NOT_SET>"
    me_model_id: Annotated[UUID | str | None, Field(title="Me Model Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"


class SlicingDirectionType(StrEnum):
    coronal = "coronal"
    sagittal = "sagittal"
    horizontal = "horizontal"
    custom = "custom"


class SpeciesAdminUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    taxonomy_id: Annotated[str | None, Field(title="Taxonomy Id")] = "<NOT_SET>"


class SpeciesCreate(BaseModel):
    name: Annotated[str, Field(title="Name")]
    taxonomy_id: Annotated[str, Field(title="Taxonomy Id")]


class SpeciesRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    taxonomy_id: Annotated[str, Field(title="Taxonomy Id")]


class StainingType(StrEnum):
    golgi = "golgi"
    nissl = "nissl"
    luxol_fast_blue = "luxol_fast_blue"
    fluorescent_nissl = "fluorescent_nissl"
    fluorescent_dyes = "fluorescent_dyes"
    fluorescent_protein_expression = "fluorescent_protein_expression"
    immunohistochemistry = "immunohistochemistry"
    other = "other"


class StorageType(StrEnum):
    aws_s3_internal = "aws_s3_internal"
    aws_s3_open = "aws_s3_open"


class StrainAdminUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    taxonomy_id: Annotated[str | None, Field(title="Taxonomy Id")] = "<NOT_SET>"
    species_id: Annotated[UUID | str | None, Field(title="Species Id")] = "<NOT_SET>"


class StrainCreate(BaseModel):
    name: Annotated[str, Field(title="Name")]
    taxonomy_id: Annotated[str, Field(title="Taxonomy Id")]
    species_id: Annotated[UUID, Field(title="Species Id")]


class StrainRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    taxonomy_id: Annotated[str, Field(title="Taxonomy Id")]
    species_id: Annotated[UUID, Field(title="Species Id")]


class StructuralDomain(StrEnum):
    apical_dendrite = "apical_dendrite"
    basal_dendrite = "basal_dendrite"
    axon = "axon"
    soma = "soma"
    neuron_morphology = "neuron_morphology"


class SubjectAdminUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    sex: Annotated[Sex | str | None, Field(title="Sex")] = "<NOT_SET>"
    weight: Annotated[float | str | None, Field(title="Weight")] = "<NOT_SET>"
    age_value: Annotated[timedelta | str | None, Field(title="Age Value")] = "<NOT_SET>"
    age_min: Annotated[timedelta | str | None, Field(title="Age Min")] = "<NOT_SET>"
    age_max: Annotated[timedelta | str | None, Field(title="Age Max")] = "<NOT_SET>"
    age_period: Annotated[AgePeriod | str | None, Field(title="Age Period")] = "<NOT_SET>"
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    species_id: Annotated[UUID | str | None, Field(title="Species Id")] = "<NOT_SET>"
    strain_id: Annotated[UUID | str | None, Field(title="Strain Id")] = "<NOT_SET>"


class SubjectCreate(BaseModel):
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    sex: Annotated[Sex, Field(description="Sex of the subject")]
    weight: Annotated[Weight | None, Field(description="Weight in grams", title="Weight")] = None
    age_value: Annotated[
        float | None, Field(description="Age value interval.", title="Age value")
    ] = None
    age_min: Annotated[
        float | None, Field(description="Minimum age range", title="Minimum age range")
    ] = None
    age_max: Annotated[
        float | None, Field(description="Maximum age range", title="Maximum age range")
    ] = None
    age_period: AgePeriod | None = None
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    species_id: Annotated[UUID, Field(title="Species Id")]
    strain_id: Annotated[UUID | None, Field(title="Strain Id")] = None


class SubjectRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    sex: Annotated[Sex, Field(description="Sex of the subject")]
    weight: Annotated[Weight | None, Field(description="Weight in grams", title="Weight")] = None
    age_value: Annotated[
        float | None, Field(description="Age value interval.", title="Age value")
    ] = None
    age_min: Annotated[
        float | None, Field(description="Minimum age range", title="Minimum age range")
    ] = None
    age_max: Annotated[
        float | None, Field(description="Maximum age range", title="Maximum age range")
    ] = None
    age_period: AgePeriod | None = None
    species: NestedSpeciesRead
    strain: NestedStrainRead | None = None


class SubjectUserUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    sex: Annotated[Sex | str | None, Field(title="Sex")] = "<NOT_SET>"
    weight: Annotated[float | str | None, Field(title="Weight")] = "<NOT_SET>"
    age_value: Annotated[timedelta | str | None, Field(title="Age Value")] = "<NOT_SET>"
    age_min: Annotated[timedelta | str | None, Field(title="Age Min")] = "<NOT_SET>"
    age_max: Annotated[timedelta | str | None, Field(title="Age Max")] = "<NOT_SET>"
    age_period: Annotated[AgePeriod | str | None, Field(title="Age Period")] = "<NOT_SET>"
    species_id: Annotated[UUID | str | None, Field(title="Species Id")] = "<NOT_SET>"
    strain_id: Annotated[UUID | str | None, Field(title="Strain Id")] = "<NOT_SET>"


class UseIon(BaseModel):
    ion_name: Annotated[str, Field(title="Ion Name")]
    read: Annotated[list[str] | None, Field(title="Read")] = []
    write: Annotated[list[str] | None, Field(title="Write")] = []
    valence: Annotated[int | None, Field(title="Valence")] = None
    main_ion: Annotated[bool | None, Field(title="Main Ion")] = None


class ValidationAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    start_time: Annotated[AwareDatetime | str | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[AwareDatetime | str | None, Field(title="End Time")] = "<NOT_SET>"
    used_ids: Annotated[list[UUID] | str | None, Field(title="Used Ids")] = "<NOT_SET>"
    generated_ids: Annotated[list[UUID] | str | None, Field(title="Generated Ids")] = "<NOT_SET>"


class ValidationCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    start_time: Annotated[AwareDatetime | None, Field(title="Start Time")] = None
    end_time: Annotated[AwareDatetime | None, Field(title="End Time")] = None
    used_ids: Annotated[list[UUID] | None, Field(title="Used Ids")] = []
    generated_ids: Annotated[list[UUID] | None, Field(title="Generated Ids")] = []


class ValidationRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    id: Annotated[UUID, Field(title="Id")]
    type: ActivityType | None = None
    start_time: Annotated[AwareDatetime | None, Field(title="Start Time")] = None
    end_time: Annotated[AwareDatetime | None, Field(title="End Time")] = None
    used: Annotated[list[NestedEntityRead], Field(title="Used")]
    generated: Annotated[list[NestedEntityRead], Field(title="Generated")]


class ValidationResultAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    passed: Annotated[bool | str | None, Field(title="Passed")] = "<NOT_SET>"
    validated_entity_id: Annotated[UUID | str | None, Field(title="Validated Entity Id")] = (
        "<NOT_SET>"
    )


class ValidationResultCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    passed: Annotated[bool, Field(title="Passed")]
    validated_entity_id: Annotated[UUID, Field(title="Validated Entity Id")]


class ValidationResultUserUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    passed: Annotated[bool | str | None, Field(title="Passed")] = "<NOT_SET>"
    validated_entity_id: Annotated[UUID | str | None, Field(title="Validated Entity Id")] = (
        "<NOT_SET>"
    )


class ValidationStatus(StrEnum):
    created = "created"
    initialized = "initialized"
    running = "running"
    done = "done"
    error = "error"


class ValidationUserUpdate(BaseModel):
    start_time: Annotated[AwareDatetime | NotSet | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[AwareDatetime | NotSet | None, Field(title="End Time")] = "<NOT_SET>"
    generated_ids: Annotated[list[UUID] | NotSet | None, Field(title="Generated Ids")] = "<NOT_SET>"


class AgentRead(RootModel[NestedPersonRead | NestedOrganizationRead | NestedConsortiumRead]):
    root: NestedPersonRead | NestedOrganizationRead | NestedConsortiumRead


class AnalysisNotebookEnvironmentAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    runtime_info: Annotated[RuntimeInfo | str | None, Field(title="Runtime Info")] = "<NOT_SET>"


class AnalysisNotebookEnvironmentCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    runtime_info: RuntimeInfo | None = None


class AnalysisNotebookEnvironmentUpdate(BaseModel):
    runtime_info: Annotated[RuntimeInfo | str | None, Field(title="Runtime Info")] = "<NOT_SET>"


class AnalysisNotebookExecutionUpdate(BaseModel):
    start_time: Annotated[AwareDatetime | NotSet | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[AwareDatetime | NotSet | None, Field(title="End Time")] = "<NOT_SET>"
    generated_ids: Annotated[list[UUID] | NotSet | None, Field(title="Generated Ids")] = "<NOT_SET>"
    analysis_notebook_template_id: Annotated[
        UUID | None, Field(title="Analysis Notebook Template Id")
    ] = None
    analysis_notebook_environment_id: Annotated[
        UUID | None, Field(title="Analysis Notebook Environment Id")
    ] = None


class AnalysisNotebookTemplateInputType(BaseModel):
    name: Annotated[str, Field(title="Name")]
    entity_type: EntityType
    is_list: Annotated[bool | None, Field(title="Is List")] = False
    count_min: Annotated[int | None, Field(ge=0, title="Count Min")] = 1
    count_max: Annotated[CountMax | None, Field(title="Count Max")] = 1


class AnalysisNotebookTemplateSpecificationsInput(BaseModel):
    schema_version: Annotated[int | None, Field(title="Schema Version")] = 1
    python: PythonDependency | None = None
    docker: DockerDependency | None = None
    inputs: Annotated[list[AnalysisNotebookTemplateInputType] | None, Field(title="Inputs")] = []


class AnalysisNotebookTemplateSpecificationsOutput(BaseModel):
    schema_version: Annotated[int | None, Field(title="Schema Version")] = 1
    python: PythonDependency | None = None
    docker: DockerDependency | None = None
    inputs: Annotated[list[AnalysisNotebookTemplateInputType] | None, Field(title="Inputs")] = []


class AnalysisNotebookTemplateUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    specifications: Annotated[
        AnalysisNotebookTemplateSpecificationsInput | str | None, Field(title="Specifications")
    ] = "<NOT_SET>"
    scale: Annotated[AnalysisScale | str | None, Field(title="Scale")] = "<NOT_SET>"


class AssetRead(BaseModel):
    size: Annotated[int, Field(title="Size")]
    sha256_digest: Annotated[str | None, Field(title="Sha256 Digest")] = None
    path: Annotated[str, Field(title="Path")]
    full_path: Annotated[str, Field(title="Full Path")]
    is_directory: Annotated[bool, Field(title="Is Directory")]
    content_type: ContentType
    meta: Annotated[dict[str, Any] | None, Field(title="Meta")] = {}
    label: AssetLabel
    storage_type: StorageType
    id: Annotated[UUID, Field(title="Id")]
    status: AssetStatus


class AssetRegister(BaseModel):
    path: Annotated[str, Field(title="Path")]
    full_path: Annotated[str, Field(title="Full Path")]
    is_directory: Annotated[bool, Field(title="Is Directory")]
    content_type: ContentType
    meta: Annotated[dict[str, Any] | None, Field(title="Meta")] = {}
    label: AssetLabel
    storage_type: StorageType


class BasicEntityRead(BaseModel):
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]


class BrainAtlasRead(BaseModel):
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    id: Annotated[UUID, Field(title="Id")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    hierarchy_id: Annotated[UUID, Field(title="Hierarchy Id")]
    species: NestedSpeciesRead


class BrainAtlasRegionRead(BaseModel):
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    volume: Annotated[float | None, Field(title="Volume")] = None
    is_leaf_region: Annotated[bool, Field(title="Is Leaf Region")]
    brain_atlas_id: Annotated[UUID, Field(title="Brain Atlas Id")]
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]


class BrainRegionHierarchyRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]


class CalibrationRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    id: Annotated[UUID, Field(title="Id")]
    type: ActivityType | None = None
    start_time: Annotated[AwareDatetime | None, Field(title="Start Time")] = None
    end_time: Annotated[AwareDatetime | None, Field(title="End Time")] = None
    used: Annotated[list[NestedEntityRead], Field(title="Used")]
    generated: Annotated[list[NestedEntityRead], Field(title="Generated")]


class CalibrationUserUpdate(BaseModel):
    start_time: Annotated[AwareDatetime | NotSet | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[AwareDatetime | NotSet | None, Field(title="End Time")] = "<NOT_SET>"
    generated_ids: Annotated[list[UUID] | NotSet | None, Field(title="Generated Ids")] = "<NOT_SET>"


class CellMorphologyAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    location: Annotated[PointLocationBase | str | None, Field(title="Location")] = "<NOT_SET>"
    legacy_id: Annotated[list[str] | str | None, Field(title="Legacy Id")] = "<NOT_SET>"
    cell_morphology_protocol_id: Annotated[
        UUID | str | None, Field(title="Cell Morphology Protocol Id")
    ] = "<NOT_SET>"


class CellMorphologyCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license_id: Annotated[UUID | None, Field(title="License Id")] = None
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    subject_id: Annotated[UUID, Field(title="Subject Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    location: PointLocationBase | None = None
    legacy_id: Annotated[list[str] | None, Field(title="Legacy Id")] = None
    cell_morphology_protocol_id: Annotated[
        UUID | None, Field(title="Cell Morphology Protocol Id")
    ] = None


class CellMorphologyUserUpdate(BaseModel):
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    location: Annotated[PointLocationBase | str | None, Field(title="Location")] = "<NOT_SET>"
    legacy_id: Annotated[list[str] | str | None, Field(title="Legacy Id")] = "<NOT_SET>"
    cell_morphology_protocol_id: Annotated[
        UUID | str | None, Field(title="Cell Morphology Protocol Id")
    ] = "<NOT_SET>"


class CircuitAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    has_morphologies: Annotated[bool | str | None, Field(title="Has Morphologies")] = "<NOT_SET>"
    has_point_neurons: Annotated[bool | str | None, Field(title="Has Point Neurons")] = "<NOT_SET>"
    has_electrical_cell_models: Annotated[
        bool | str | None, Field(title="Has Electrical Cell Models")
    ] = "<NOT_SET>"
    has_spines: Annotated[bool | str | None, Field(title="Has Spines")] = "<NOT_SET>"
    number_neurons: Annotated[int | str | None, Field(title="Number Neurons")] = "<NOT_SET>"
    number_synapses: Annotated[int | str | None, Field(title="Number Synapses")] = "<NOT_SET>"
    number_connections: Annotated[int | str | None, Field(title="Number Connections")] = "<NOT_SET>"
    scale: Annotated[CircuitScale | str | None, Field(title="Scale")] = "<NOT_SET>"
    build_category: Annotated[CircuitBuildCategory | str | None, Field(title="Build Category")] = (
        "<NOT_SET>"
    )
    root_circuit_id: Annotated[UUID | str | None, Field(title="Root Circuit Id")] = "<NOT_SET>"
    atlas_id: Annotated[UUID | str | None, Field(title="Atlas Id")] = "<NOT_SET>"


class CircuitCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license_id: Annotated[UUID | None, Field(title="License Id")] = None
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    subject_id: Annotated[UUID, Field(title="Subject Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    has_morphologies: Annotated[bool | None, Field(title="Has Morphologies")] = False
    has_point_neurons: Annotated[bool | None, Field(title="Has Point Neurons")] = False
    has_electrical_cell_models: Annotated[
        bool | None, Field(title="Has Electrical Cell Models")
    ] = False
    has_spines: Annotated[bool | None, Field(title="Has Spines")] = False
    number_neurons: Annotated[int, Field(title="Number Neurons")]
    number_synapses: Annotated[int, Field(title="Number Synapses")]
    number_connections: Annotated[int | None, Field(title="Number Connections")] = None
    scale: CircuitScale
    build_category: CircuitBuildCategory
    root_circuit_id: Annotated[UUID | None, Field(title="Root Circuit Id")] = None
    atlas_id: Annotated[UUID | None, Field(title="Atlas Id")] = None


class ComputationallySynthesizedCellMorphologyProtocolRead(BaseModel):
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    protocol_design: CellMorphologyProtocolDesign
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[
        Literal["computationally_synthesized"], Field(title="Generation Type")
    ]
    method_type: Annotated[str, Field(title="Method Type")]


class ConsortiumRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    pref_label: Annotated[str, Field(title="Pref Label")]
    alternative_name: Annotated[str | None, Field(title="Alternative Name")] = None
    type: Annotated[str, Field(title="Type")]


class ContributionRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    agent: AgentRead
    role: RoleRead
    entity: NestedEntityRead


class DerivationCreate(BaseModel):
    used_id: Annotated[UUID, Field(title="Used Id")]
    generated_id: Annotated[UUID, Field(title="Generated Id")]
    derivation_type: DerivationType


class DerivationRead(BaseModel):
    used: BasicEntityRead
    generated: BasicEntityRead
    derivation_type: DerivationType


class DigitalReconstructionCellMorphologyProtocolCreate(BaseModel):
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    protocol_design: CellMorphologyProtocolDesign
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[Literal["digital_reconstruction"], Field(title="Generation Type")]
    staining_type: StainingType | None = None
    slicing_thickness: Annotated[float, Field(ge=0.0, title="Slicing Thickness")]
    slicing_direction: SlicingDirectionType | None = None
    magnification: Annotated[Magnification | None, Field(title="Magnification")] = None
    tissue_shrinkage: Annotated[TissueShrinkage | None, Field(title="Tissue Shrinkage")] = None
    corrected_for_shrinkage: Annotated[bool | None, Field(title="Corrected For Shrinkage")] = None


class DigitalReconstructionCellMorphologyProtocolRead(BaseModel):
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    protocol_design: CellMorphologyProtocolDesign
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[Literal["digital_reconstruction"], Field(title="Generation Type")]
    staining_type: StainingType | None = None
    slicing_thickness: Annotated[float, Field(ge=0.0, title="Slicing Thickness")]
    slicing_direction: SlicingDirectionType | None = None
    magnification: Annotated[Magnification | None, Field(title="Magnification")] = None
    tissue_shrinkage: Annotated[TissueShrinkage | None, Field(title="Tissue Shrinkage")] = None
    corrected_for_shrinkage: Annotated[bool | None, Field(title="Corrected For Shrinkage")] = None


class EMCellMeshCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license_id: Annotated[UUID | None, Field(title="License Id")] = None
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    subject_id: Annotated[UUID, Field(title="Subject Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    release_version: Annotated[int, Field(title="Release Version")]
    dense_reconstruction_cell_id: Annotated[int, Field(title="Dense Reconstruction Cell Id")]
    generation_method: EMCellMeshGenerationMethod
    level_of_detail: Annotated[int, Field(title="Level Of Detail")]
    generation_parameters: Annotated[
        dict[str, Any] | None, Field(title="Generation Parameters")
    ] = None
    mesh_type: EMCellMeshType
    em_dense_reconstruction_dataset_id: Annotated[
        UUID, Field(title="Em Dense Reconstruction Dataset Id")
    ]


class EMDenseReconstructionDatasetCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license_id: Annotated[UUID | None, Field(title="License Id")] = None
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    subject_id: Annotated[UUID, Field(title="Subject Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    fixation: Annotated[str | None, Field(title="Fixation")] = None
    staining_type: Annotated[str | None, Field(title="Staining Type")] = None
    slicing_thickness: Annotated[float | None, Field(title="Slicing Thickness")] = None
    tissue_shrinkage: Annotated[float | None, Field(title="Tissue Shrinkage")] = None
    microscope_type: Annotated[str | None, Field(title="Microscope Type")] = None
    detector: Annotated[str | None, Field(title="Detector")] = None
    slicing_direction: SlicingDirectionType | None = None
    landmarks: Annotated[str | None, Field(title="Landmarks")] = None
    voltage: Annotated[float | None, Field(title="Voltage")] = None
    current: Annotated[float | None, Field(title="Current")] = None
    dose: Annotated[float | None, Field(title="Dose")] = None
    temperature: Annotated[float | None, Field(title="Temperature")] = None
    volume_resolution_x_nm: Annotated[float, Field(title="Volume Resolution X Nm")]
    volume_resolution_y_nm: Annotated[float, Field(title="Volume Resolution Y Nm")]
    volume_resolution_z_nm: Annotated[float, Field(title="Volume Resolution Z Nm")]
    release_url: Annotated[AnyUrl, Field(title="Release Url")]
    cave_client_url: Annotated[AnyUrl, Field(title="Cave Client Url")]
    cave_datastack: Annotated[str, Field(title="Cave Datastack")]
    precomputed_mesh_url: Annotated[AnyUrl, Field(title="Precomputed Mesh Url")]
    cell_identifying_property: Annotated[str, Field(title="Cell Identifying Property")]


class ETypeClassificationRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    entity_id: Annotated[UUID, Field(title="Entity Id")]
    etype_class_id: Annotated[UUID, Field(title="Etype Class Id")]


class ElectricalCellRecordingAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    ljp: Annotated[float | str | None, Field(title="Ljp")] = "<NOT_SET>"
    recording_location: Annotated[list[str] | str | None, Field(title="Recording Location")] = (
        "<NOT_SET>"
    )
    recording_type: Annotated[
        ElectricalRecordingType | str | None, Field(title="Recording Type")
    ] = "<NOT_SET>"
    recording_origin: Annotated[
        ElectricalRecordingOrigin | str | None, Field(title="Recording Origin")
    ] = "<NOT_SET>"
    temperature: Annotated[float | str | None, Field(title="Temperature")] = "<NOT_SET>"
    comment: Annotated[str | None, Field(title="Comment")] = "<NOT_SET>"
    legacy_id: Annotated[list[str] | str | None, Field(title="Legacy Id")] = "<NOT_SET>"


class ElectricalCellRecordingCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license_id: Annotated[UUID | None, Field(title="License Id")] = None
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    subject_id: Annotated[UUID, Field(title="Subject Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    ljp: Annotated[
        float | None,
        Field(
            description="Correction applied to the voltage trace, in mV",
            title="Liquid Junction Potential",
        ),
    ] = 0.0
    recording_location: Annotated[
        list[str],
        Field(
            description="Location on the cell where recording was performed, in hoc-compatible format.",
            title="Recording Location",
        ),
    ]
    recording_type: Annotated[
        ElectricalRecordingType,
        Field(
            description="Recording type. One of: [<ElectricalRecordingStimulusType.conductance_clamp: 'conductance_clamp'>, <ElectricalRecordingStimulusType.current_clamp: 'current_clamp'>, <ElectricalRecordingStimulusType.extracellular: 'extracellular'>, <ElectricalRecordingStimulusType.other: 'other'>, <ElectricalRecordingStimulusType.unknown: 'unknown'>, <ElectricalRecordingStimulusType.voltage_clamp: 'voltage_clamp'>]",
            title="Recording Type",
        ),
    ]
    recording_origin: Annotated[
        ElectricalRecordingOrigin,
        Field(
            description="Recording origin. One of: [<ElectricalRecordingOrigin.in_silico: 'in_silico'>, <ElectricalRecordingOrigin.in_vitro: 'in_vitro'>, <ElectricalRecordingOrigin.in_vivo: 'in_vivo'>, <ElectricalRecordingOrigin.unknown: 'unknown'>]",
            title="Recording Origin",
        ),
    ]
    temperature: Annotated[
        float | None,
        Field(
            description="Temperature at which the recording was performed, in degrees Celsius.",
            title="Temperature",
        ),
    ] = None
    comment: Annotated[
        str | None, Field(description="Comment with further details.", title="Comment")
    ] = None
    legacy_id: Annotated[list[str] | None, Field(title="Legacy Id")] = None


class ElectricalCellRecordingUserUpdate(BaseModel):
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    ljp: Annotated[float | str | None, Field(title="Ljp")] = "<NOT_SET>"
    recording_location: Annotated[list[str] | str | None, Field(title="Recording Location")] = (
        "<NOT_SET>"
    )
    recording_type: Annotated[
        ElectricalRecordingType | str | None, Field(title="Recording Type")
    ] = "<NOT_SET>"
    recording_origin: Annotated[
        ElectricalRecordingOrigin | str | None, Field(title="Recording Origin")
    ] = "<NOT_SET>"
    temperature: Annotated[float | str | None, Field(title="Temperature")] = "<NOT_SET>"
    comment: Annotated[str | None, Field(title="Comment")] = "<NOT_SET>"
    legacy_id: Annotated[list[str] | str | None, Field(title="Legacy Id")] = "<NOT_SET>"


class ElectricalRecordingStimulusAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    dt: Annotated[float | str | None, Field(title="Dt")] = "<NOT_SET>"
    injection_type: Annotated[
        ElectricalRecordingStimulusType | str | None, Field(title="Injection Type")
    ] = "<NOT_SET>"
    shape: Annotated[ElectricalRecordingStimulusShape | str | None, Field(title="Shape")] = (
        "<NOT_SET>"
    )
    start_time: Annotated[float | str | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[float | str | None, Field(title="End Time")] = "<NOT_SET>"
    recording_id: Annotated[UUID | str | None, Field(title="Recording Id")] = "<NOT_SET>"


class ElectricalRecordingStimulusCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    dt: Annotated[float | None, Field(title="Dt")] = None
    injection_type: ElectricalRecordingStimulusType
    shape: ElectricalRecordingStimulusShape
    start_time: Annotated[float | None, Field(title="Start Time")] = None
    end_time: Annotated[float | None, Field(title="End Time")] = None
    recording_id: Annotated[UUID, Field(title="Recording Id")]


class ElectricalRecordingStimulusRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    dt: Annotated[float | None, Field(title="Dt")] = None
    injection_type: ElectricalRecordingStimulusType
    shape: ElectricalRecordingStimulusShape
    start_time: Annotated[float | None, Field(title="Start Time")] = None
    end_time: Annotated[float | None, Field(title="End Time")] = None
    recording_id: Annotated[UUID, Field(title="Recording Id")]


class EntityRead(BaseModel):
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    id: Annotated[UUID, Field(title="Id")]
    type: Annotated[str, Field(title="Type")]
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool, Field(title="Authorized Public")]


class ExemplarMorphology(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    location: PointLocationBase | None = None
    legacy_id: Annotated[list[str] | None, Field(title="Legacy Id")] = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]


class ExternalUrlRead(BaseModel):
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    source: ExternalSource
    url: Annotated[AnyUrl, Field(title="Url")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    source_name: Annotated[str, Field(title="Source Name")]


class IonChannelRead(BaseModel):
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    label: Annotated[str, Field(title="Label")]
    gene: Annotated[str, Field(title="Gene")]
    synonyms: Annotated[list[str], Field(title="Synonyms")]


class ListResponseAnnotationRead(BaseModel):
    data: Annotated[list[AnnotationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseAssetRead(BaseModel):
    data: Annotated[list[AssetRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseBasicEntityRead(BaseModel):
    data: Annotated[list[BasicEntityRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseBrainAtlasRead(BaseModel):
    data: Annotated[list[BrainAtlasRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseBrainAtlasRegionRead(BaseModel):
    data: Annotated[list[BrainAtlasRegionRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseBrainRegionHierarchyRead(BaseModel):
    data: Annotated[list[BrainRegionHierarchyRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseBrainRegionRead(BaseModel):
    data: Annotated[list[BrainRegionRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseCalibrationRead(BaseModel):
    data: Annotated[list[CalibrationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseConsortiumRead(BaseModel):
    data: Annotated[list[ConsortiumRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseContributionRead(BaseModel):
    data: Annotated[list[ContributionRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseETypeClassificationRead(BaseModel):
    data: Annotated[list[ETypeClassificationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseElectricalRecordingStimulusRead(BaseModel):
    data: Annotated[list[ElectricalRecordingStimulusRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseExternalUrlRead(BaseModel):
    data: Annotated[list[ExternalUrlRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseIonChannelRead(BaseModel):
    data: Annotated[list[IonChannelRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseLicenseRead(BaseModel):
    data: Annotated[list[LicenseRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseOrganizationRead(BaseModel):
    data: Annotated[list[OrganizationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponsePersonRead(BaseModel):
    data: Annotated[list[PersonRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponsePublicationRead(BaseModel):
    data: Annotated[list[PublicationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseRoleRead(BaseModel):
    data: Annotated[list[RoleRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseScientificArtifactExternalUrlLinkRead(BaseModel):
    data: Annotated[list[ScientificArtifactExternalUrlLinkRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseScientificArtifactPublicationLinkRead(BaseModel):
    data: Annotated[list[ScientificArtifactPublicationLinkRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseSimulationGenerationRead(BaseModel):
    data: Annotated[list[SimulationGenerationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseSpeciesRead(BaseModel):
    data: Annotated[list[SpeciesRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseStrainRead(BaseModel):
    data: Annotated[list[StrainRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseSubjectRead(BaseModel):
    data: Annotated[list[SubjectRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseValidationRead(BaseModel):
    data: Annotated[list[ValidationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class MEModelAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    validation_status: Annotated[
        ValidationStatus | str | None, Field(title="Validation Status")
    ] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    morphology_id: Annotated[UUID | str | None, Field(title="Morphology Id")] = "<NOT_SET>"
    emodel_id: Annotated[UUID | str | None, Field(title="Emodel Id")] = "<NOT_SET>"
    species_id: Annotated[UUID | str | None, Field(title="Species Id")] = "<NOT_SET>"
    strain_id: Annotated[UUID | str | None, Field(title="Strain Id")] = "<NOT_SET>"


class MEModelCalibrationResultRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    holding_current: Annotated[float, Field(title="Holding Current")]
    threshold_current: Annotated[float, Field(title="Threshold Current")]
    rin: Annotated[float | None, Field(title="Rin")] = None
    calibrated_entity_id: Annotated[UUID, Field(title="Calibrated Entity Id")]


class MEModelCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    validation_status: ValidationStatus | None = "created"
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    morphology_id: Annotated[UUID, Field(title="Morphology Id")]
    emodel_id: Annotated[UUID, Field(title="Emodel Id")]
    species_id: Annotated[UUID, Field(title="Species Id")]
    strain_id: Annotated[UUID | None, Field(title="Strain Id")] = None


class MEModelUserUpdate(BaseModel):
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    validation_status: Annotated[
        ValidationStatus | str | None, Field(title="Validation Status")
    ] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    morphology_id: Annotated[UUID | str | None, Field(title="Morphology Id")] = "<NOT_SET>"
    emodel_id: Annotated[UUID | str | None, Field(title="Emodel Id")] = "<NOT_SET>"
    species_id: Annotated[UUID | str | None, Field(title="Species Id")] = "<NOT_SET>"
    strain_id: Annotated[UUID | str | None, Field(title="Strain Id")] = "<NOT_SET>"


class MTypeClassificationRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    entity_id: Annotated[UUID, Field(title="Entity Id")]
    mtype_class_id: Annotated[UUID, Field(title="Mtype Class Id")]


class MeasurementItem(BaseModel):
    name: MeasurementStatistic | None = None
    unit: MeasurementUnit | None = None
    value: Annotated[float | None, Field(title="Value")] = None


class MeasurementKindCreate(BaseModel):
    structural_domain: StructuralDomain
    measurement_items: Annotated[list[MeasurementItem], Field(title="Measurement Items")]
    pref_label: Annotated[str, Field(title="Pref Label")]


class MeasurementKindRead(BaseModel):
    structural_domain: StructuralDomain
    measurement_items: Annotated[list[MeasurementItem], Field(title="Measurement Items")]
    pref_label: Annotated[str, Field(title="Pref Label")]


class MeasurementRecordCreate(BaseModel):
    name: MeasurementStatistic
    unit: MeasurementUnit
    value: Annotated[float, Field(title="Value")]


class MeasurementRecordRead(BaseModel):
    name: MeasurementStatistic
    unit: MeasurementUnit
    value: Annotated[float, Field(title="Value")]
    id: Annotated[int, Field(title="Id")]


class ModifiedReconstructionCellMorphologyProtocolRead(BaseModel):
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    protocol_design: CellMorphologyProtocolDesign
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[Literal["modified_reconstruction"], Field(title="Generation Type")]
    method_type: ModifiedMorphologyMethodType


class NestedAnalysisNotebookEnvironmentRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    type: EntityType | None = None
    runtime_info: RuntimeInfo | None = None


class NestedAnalysisNotebookTemplateRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    type: EntityType | None = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    specifications: AnalysisNotebookTemplateSpecificationsOutput | None = None
    scale: AnalysisScale


class NestedContributionRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    agent: AgentRead
    role: RoleRead


class NestedDigitalReconstructionCellMorphologyProtocolRead(BaseModel):
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    protocol_design: CellMorphologyProtocolDesign
    id: Annotated[UUID, Field(title="Id")]
    type: Annotated[Literal["cell_morphology_protocol"], Field(title="Type")] = (
        "cell_morphology_protocol"
    )
    generation_type: Annotated[Literal["digital_reconstruction"], Field(title="Generation Type")]
    staining_type: StainingType | None = None
    slicing_thickness: Annotated[float, Field(ge=0.0, title="Slicing Thickness")]
    slicing_direction: SlicingDirectionType | None = None
    magnification: Annotated[Magnification | None, Field(title="Magnification")] = None
    tissue_shrinkage: Annotated[TissueShrinkage | None, Field(title="Tissue Shrinkage")] = None
    corrected_for_shrinkage: Annotated[bool | None, Field(title="Corrected For Shrinkage")] = None


class NestedMEModel(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    validation_status: ValidationStatus | None = "created"
    mtypes: Annotated[list[AnnotationRead] | None, Field(title="Mtypes")] = None
    etypes: Annotated[list[AnnotationRead] | None, Field(title="Etypes")] = None


class NestedSubjectRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    sex: Annotated[Sex, Field(description="Sex of the subject")]
    weight: Annotated[Weight | None, Field(description="Weight in grams", title="Weight")] = None
    age_value: Annotated[
        float | None, Field(description="Age value interval.", title="Age value")
    ] = None
    age_min: Annotated[
        float | None, Field(description="Minimum age range", title="Minimum age range")
    ] = None
    age_max: Annotated[
        float | None, Field(description="Maximum age range", title="Maximum age range")
    ] = None
    age_period: AgePeriod | None = None
    species: NestedSpeciesRead
    strain: NestedStrainRead | None = None


class NeuronBlock(BaseModel):
    global_: Annotated[
        list[dict[str, str | None]] | None, Field(alias="global", title="Global")
    ] = []
    range: Annotated[list[dict[str, str | None]] | None, Field(title="Range")] = []
    useion: Annotated[list[UseIon] | None, Field(title="Useion")] = []
    nonspecific: Annotated[list[dict[str, str | None]] | None, Field(title="Nonspecific")] = []


class SimulationCampaignRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    id: Annotated[UUID, Field(title="Id")]
    type: EntityType | None = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    scan_parameters: Annotated[dict[str, Any], Field(title="Scan Parameters")]
    entity_id: Annotated[UUID, Field(title="Entity Id")]
    simulations: Annotated[list[NestedSimulationRead], Field(title="Simulations")]


class SimulationExecutionAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    start_time: Annotated[AwareDatetime | str | None, Field(title="Start Time")] = "<NOT_SET>"
    end_time: Annotated[AwareDatetime | str | None, Field(title="End Time")] = "<NOT_SET>"
    used_ids: Annotated[list[UUID] | str | None, Field(title="Used Ids")] = "<NOT_SET>"
    generated_ids: Annotated[list[UUID] | str | None, Field(title="Generated Ids")] = "<NOT_SET>"
    status: Annotated[SimulationExecutionStatus | str | None, Field(title="Status")] = "<NOT_SET>"


class SimulationExecutionCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    start_time: Annotated[AwareDatetime | None, Field(title="Start Time")] = None
    end_time: Annotated[AwareDatetime | None, Field(title="End Time")] = None
    used_ids: Annotated[list[UUID] | None, Field(title="Used Ids")] = []
    generated_ids: Annotated[list[UUID] | None, Field(title="Generated Ids")] = []
    status: SimulationExecutionStatus


class SimulationExecutionRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    id: Annotated[UUID, Field(title="Id")]
    type: ActivityType | None = None
    start_time: Annotated[AwareDatetime | None, Field(title="Start Time")] = None
    end_time: Annotated[AwareDatetime | None, Field(title="End Time")] = None
    used: Annotated[list[NestedEntityRead], Field(title="Used")]
    generated: Annotated[list[NestedEntityRead], Field(title="Generated")]
    status: SimulationExecutionStatus


class SimulationRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    id: Annotated[UUID, Field(title="Id")]
    type: EntityType | None = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    simulation_campaign_id: Annotated[UUID, Field(title="Simulation Campaign Id")]
    entity_id: Annotated[UUID, Field(title="Entity Id")]
    scan_parameters: Annotated[dict[str, Any], Field(title="Scan Parameters")]


class SimulationResultRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    id: Annotated[UUID, Field(title="Id")]
    type: EntityType | None = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    simulation_id: Annotated[UUID, Field(title="Simulation Id")]


class SingleNeuronSimulationAdminUpdate(BaseModel):
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    seed: Annotated[int | str | None, Field(title="Seed")] = "<NOT_SET>"
    status: Annotated[SingleNeuronSimulationStatus | str | None, Field(title="Status")] = (
        "<NOT_SET>"
    )
    injection_location: Annotated[list[str] | str | None, Field(title="Injection Location")] = (
        "<NOT_SET>"
    )
    recording_location: Annotated[list[str] | str | None, Field(title="Recording Location")] = (
        "<NOT_SET>"
    )
    me_model_id: Annotated[UUID | str | None, Field(title="Me Model Id")] = "<NOT_SET>"


class SingleNeuronSimulationCreate(BaseModel):
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    seed: Annotated[int, Field(title="Seed")]
    status: SingleNeuronSimulationStatus
    injection_location: Annotated[list[str], Field(title="Injection Location")]
    recording_location: Annotated[list[str], Field(title="Recording Location")]
    me_model_id: Annotated[UUID, Field(title="Me Model Id")]


class SingleNeuronSimulationRead(BaseModel):
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    type: EntityType | None = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    brain_region: BrainRegionRead
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    seed: Annotated[int, Field(title="Seed")]
    status: SingleNeuronSimulationStatus
    injection_location: Annotated[list[str], Field(title="Injection Location")]
    recording_location: Annotated[list[str], Field(title="Recording Location")]
    me_model: NestedMEModel


class SingleNeuronSynaptomeRead(BaseModel):
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    type: EntityType | None = None
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    seed: Annotated[int, Field(title="Seed")]
    me_model: NestedMEModel
    brain_region: BrainRegionRead


class SingleNeuronSynaptomeSimulationRead(BaseModel):
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    type: EntityType | None = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    id: Annotated[UUID, Field(title="Id")]
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    brain_region: BrainRegionRead
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    seed: Annotated[int, Field(title="Seed")]
    status: SingleNeuronSimulationStatus
    injection_location: Annotated[list[str], Field(title="Injection Location")]
    recording_location: Annotated[list[str], Field(title="Recording Location")]
    synaptome: NestedSynaptome


class ValidationResultRead(BaseModel):
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    passed: Annotated[bool, Field(title="Passed")]
    validated_entity_id: Annotated[UUID, Field(title="Validated Entity Id")]


class AnalysisNotebookEnvironmentRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    id: Annotated[UUID, Field(title="Id")]
    type: EntityType | None = None
    runtime_info: RuntimeInfo | None = None


class AnalysisNotebookExecutionRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    id: Annotated[UUID, Field(title="Id")]
    type: ActivityType | None = None
    start_time: Annotated[AwareDatetime | None, Field(title="Start Time")] = None
    end_time: Annotated[AwareDatetime | None, Field(title="End Time")] = None
    used: Annotated[list[NestedEntityRead], Field(title="Used")]
    generated: Annotated[list[NestedEntityRead], Field(title="Generated")]
    analysis_notebook_template: NestedAnalysisNotebookTemplateRead | None = None
    analysis_notebook_environment: NestedAnalysisNotebookEnvironmentRead


class AnalysisNotebookResultRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    id: Annotated[UUID, Field(title="Id")]
    type: EntityType | None = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]


class AnalysisNotebookTemplateAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    specifications: Annotated[
        AnalysisNotebookTemplateSpecificationsInput | str | None, Field(title="Specifications")
    ] = "<NOT_SET>"
    scale: Annotated[AnalysisScale | str | None, Field(title="Scale")] = "<NOT_SET>"


class AnalysisNotebookTemplateCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    specifications: AnalysisNotebookTemplateSpecificationsInput | None = None
    scale: AnalysisScale


class AnalysisNotebookTemplateRead(BaseModel):
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    id: Annotated[UUID, Field(title="Id")]
    type: EntityType | None = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    specifications: AnalysisNotebookTemplateSpecificationsOutput | None = None
    scale: AnalysisScale


class AssetAndPresignedURLS(BaseModel):
    asset: AssetRead
    files: Annotated[dict[str, AnyUrl], Field(title="Files")]


class CellCompositionRead(BaseModel):
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]


class CellMorphologyProtocolCreate(
    RootModel[
        DigitalReconstructionCellMorphologyProtocolCreate
        | ModifiedReconstructionCellMorphologyProtocolCreate
        | ComputationallySynthesizedCellMorphologyProtocolCreate
        | PlaceholderCellMorphologyProtocolCreate
    ]
):
    root: Annotated[
        DigitalReconstructionCellMorphologyProtocolCreate
        | ModifiedReconstructionCellMorphologyProtocolCreate
        | ComputationallySynthesizedCellMorphologyProtocolCreate
        | PlaceholderCellMorphologyProtocolCreate,
        Field(discriminator="generation_type"),
    ]


class CellMorphologyProtocolRead(
    RootModel[
        DigitalReconstructionCellMorphologyProtocolRead
        | ModifiedReconstructionCellMorphologyProtocolRead
        | ComputationallySynthesizedCellMorphologyProtocolRead
        | PlaceholderCellMorphologyProtocolRead
    ]
):
    root: Annotated[
        DigitalReconstructionCellMorphologyProtocolRead
        | ModifiedReconstructionCellMorphologyProtocolRead
        | ComputationallySynthesizedCellMorphologyProtocolRead
        | PlaceholderCellMorphologyProtocolRead,
        Field(discriminator="generation_type"),
    ]


class CircuitRead(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    license: LicenseRead | None = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    brain_region: BrainRegionRead
    subject: NestedSubjectRead
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    has_morphologies: Annotated[bool | None, Field(title="Has Morphologies")] = False
    has_point_neurons: Annotated[bool | None, Field(title="Has Point Neurons")] = False
    has_electrical_cell_models: Annotated[
        bool | None, Field(title="Has Electrical Cell Models")
    ] = False
    has_spines: Annotated[bool | None, Field(title="Has Spines")] = False
    number_neurons: Annotated[int, Field(title="Number Neurons")]
    number_synapses: Annotated[int, Field(title="Number Synapses")]
    number_connections: Annotated[int | None, Field(title="Number Connections")] = None
    scale: CircuitScale
    build_category: CircuitBuildCategory
    root_circuit_id: Annotated[UUID | None, Field(title="Root Circuit Id")] = None
    atlas_id: Annotated[UUID | None, Field(title="Atlas Id")] = None


class EMCellMeshRead(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    license: LicenseRead | None = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    brain_region: BrainRegionRead
    subject: NestedSubjectRead
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    release_version: Annotated[int, Field(title="Release Version")]
    dense_reconstruction_cell_id: Annotated[int, Field(title="Dense Reconstruction Cell Id")]
    generation_method: EMCellMeshGenerationMethod
    level_of_detail: Annotated[int, Field(title="Level Of Detail")]
    generation_parameters: Annotated[
        dict[str, Any] | None, Field(title="Generation Parameters")
    ] = None
    mesh_type: EMCellMeshType
    em_dense_reconstruction_dataset: BasicEntityRead


class EMDenseReconstructionDatasetRead(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    license: LicenseRead | None = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    brain_region: BrainRegionRead
    subject: NestedSubjectRead
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    protocol_document: Annotated[ProtocolDocument | None, Field(title="Protocol Document")] = None
    fixation: Annotated[str | None, Field(title="Fixation")] = None
    staining_type: Annotated[str | None, Field(title="Staining Type")] = None
    slicing_thickness: Annotated[float | None, Field(title="Slicing Thickness")] = None
    tissue_shrinkage: Annotated[float | None, Field(title="Tissue Shrinkage")] = None
    microscope_type: Annotated[str | None, Field(title="Microscope Type")] = None
    detector: Annotated[str | None, Field(title="Detector")] = None
    slicing_direction: SlicingDirectionType | None = None
    landmarks: Annotated[str | None, Field(title="Landmarks")] = None
    voltage: Annotated[float | None, Field(title="Voltage")] = None
    current: Annotated[float | None, Field(title="Current")] = None
    dose: Annotated[float | None, Field(title="Dose")] = None
    temperature: Annotated[float | None, Field(title="Temperature")] = None
    volume_resolution_x_nm: Annotated[float, Field(title="Volume Resolution X Nm")]
    volume_resolution_y_nm: Annotated[float, Field(title="Volume Resolution Y Nm")]
    volume_resolution_z_nm: Annotated[float, Field(title="Volume Resolution Z Nm")]
    release_url: Annotated[AnyUrl, Field(title="Release Url")]
    cave_client_url: Annotated[AnyUrl, Field(title="Cave Client Url")]
    cave_datastack: Annotated[str, Field(title="Cave Datastack")]
    precomputed_mesh_url: Annotated[AnyUrl, Field(title="Precomputed Mesh Url")]
    cell_identifying_property: Annotated[str, Field(title="Cell Identifying Property")]


class EModelRead(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    type: EntityType | None = None
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    description: Annotated[str, Field(title="Description")]
    name: Annotated[str, Field(title="Name")]
    iteration: Annotated[str, Field(title="Iteration")]
    score: Annotated[float, Field(title="Score")]
    seed: Annotated[int, Field(title="Seed")]
    id: Annotated[UUID, Field(title="Id")]
    species: NestedSpeciesRead
    strain: NestedStrainRead | None = None
    brain_region: BrainRegionRead
    mtypes: Annotated[list[AnnotationRead] | None, Field(title="Mtypes")] = None
    etypes: Annotated[list[AnnotationRead] | None, Field(title="Etypes")] = None
    exemplar_morphology: ExemplarMorphology


class ElectricalCellRecordingRead(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    license: LicenseRead | None = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    brain_region: BrainRegionRead
    subject: NestedSubjectRead
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    ljp: Annotated[
        float | None,
        Field(
            description="Correction applied to the voltage trace, in mV",
            title="Liquid Junction Potential",
        ),
    ] = 0.0
    recording_location: Annotated[
        list[str],
        Field(
            description="Location on the cell where recording was performed, in hoc-compatible format.",
            title="Recording Location",
        ),
    ]
    recording_type: Annotated[
        ElectricalRecordingType,
        Field(
            description="Recording type. One of: [<ElectricalRecordingStimulusType.conductance_clamp: 'conductance_clamp'>, <ElectricalRecordingStimulusType.current_clamp: 'current_clamp'>, <ElectricalRecordingStimulusType.extracellular: 'extracellular'>, <ElectricalRecordingStimulusType.other: 'other'>, <ElectricalRecordingStimulusType.unknown: 'unknown'>, <ElectricalRecordingStimulusType.voltage_clamp: 'voltage_clamp'>]",
            title="Recording Type",
        ),
    ]
    recording_origin: Annotated[
        ElectricalRecordingOrigin,
        Field(
            description="Recording origin. One of: [<ElectricalRecordingOrigin.in_silico: 'in_silico'>, <ElectricalRecordingOrigin.in_vitro: 'in_vitro'>, <ElectricalRecordingOrigin.in_vivo: 'in_vivo'>, <ElectricalRecordingOrigin.unknown: 'unknown'>]",
            title="Recording Origin",
        ),
    ]
    temperature: Annotated[
        float | None,
        Field(
            description="Temperature at which the recording was performed, in degrees Celsius.",
            title="Temperature",
        ),
    ] = None
    comment: Annotated[
        str | None, Field(description="Comment with further details.", title="Comment")
    ] = None
    legacy_id: Annotated[list[str] | None, Field(title="Legacy Id")] = None
    stimuli: Annotated[
        list[NestedElectricalRecordingStimulusRead] | None,
        Field(
            description="List of stimuli applied to the cell with their respective time steps",
            title="Electrical Recording Stimuli",
        ),
    ] = None
    etypes: Annotated[list[AnnotationRead] | None, Field(title="Etypes")] = None


class ExperimentalBoutonDensityAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = "<NOT_SET>"
    measurements: Annotated[
        list[MeasurementRecordCreate] | str | None, Field(title="Measurements")
    ] = "<NOT_SET>"


class ExperimentalBoutonDensityCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license_id: Annotated[UUID | None, Field(title="License Id")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    subject_id: Annotated[UUID, Field(title="Subject Id")]
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = None
    measurements: Annotated[list[MeasurementRecordCreate], Field(title="Measurements")]


class ExperimentalBoutonDensityRead(BaseModel):
    subject: NestedSubjectRead
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    type: EntityType | None = None
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license: LicenseRead | None = None
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    measurements: Annotated[list[MeasurementRecordRead], Field(title="Measurements")]
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    brain_region: BrainRegionRead
    mtypes: Annotated[list[AnnotationRead] | None, Field(title="Mtypes")] = None


class ExperimentalBoutonDensityUserUpdate(BaseModel):
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = "<NOT_SET>"
    measurements: Annotated[
        list[MeasurementRecordCreate] | str | None, Field(title="Measurements")
    ] = "<NOT_SET>"


class ExperimentalNeuronDensityAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = "<NOT_SET>"
    measurements: Annotated[
        list[MeasurementRecordCreate] | str | None, Field(title="Measurements")
    ] = "<NOT_SET>"


class ExperimentalNeuronDensityCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license_id: Annotated[UUID | None, Field(title="License Id")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    subject_id: Annotated[UUID, Field(title="Subject Id")]
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = None
    measurements: Annotated[list[MeasurementRecordCreate], Field(title="Measurements")]


class ExperimentalNeuronDensityRead(BaseModel):
    subject: NestedSubjectRead
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    type: EntityType | None = None
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license: LicenseRead | None = None
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    measurements: Annotated[list[MeasurementRecordRead], Field(title="Measurements")]
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    brain_region: BrainRegionRead
    mtypes: Annotated[list[AnnotationRead] | None, Field(title="Mtypes")] = None
    etypes: Annotated[list[AnnotationRead] | None, Field(title="Etypes")] = None


class ExperimentalNeuronDensityUserUpdate(BaseModel):
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = "<NOT_SET>"
    measurements: Annotated[
        list[MeasurementRecordCreate] | str | None, Field(title="Measurements")
    ] = "<NOT_SET>"


class ExperimentalSynapsesPerConnectionAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = "<NOT_SET>"
    measurements: Annotated[
        list[MeasurementRecordCreate] | str | None, Field(title="Measurements")
    ] = "<NOT_SET>"
    pre_mtype_id: Annotated[UUID | str | None, Field(title="Pre Mtype Id")] = "<NOT_SET>"
    post_mtype_id: Annotated[UUID | str | None, Field(title="Post Mtype Id")] = "<NOT_SET>"
    pre_region_id: Annotated[UUID | str | None, Field(title="Pre Region Id")] = "<NOT_SET>"
    post_region_id: Annotated[UUID | str | None, Field(title="Post Region Id")] = "<NOT_SET>"


class ExperimentalSynapsesPerConnectionCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license_id: Annotated[UUID | None, Field(title="License Id")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    subject_id: Annotated[UUID, Field(title="Subject Id")]
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = None
    measurements: Annotated[list[MeasurementRecordCreate], Field(title="Measurements")]
    pre_mtype_id: Annotated[UUID, Field(title="Pre Mtype Id")]
    post_mtype_id: Annotated[UUID, Field(title="Post Mtype Id")]
    pre_region_id: Annotated[UUID, Field(title="Pre Region Id")]
    post_region_id: Annotated[UUID, Field(title="Post Region Id")]


class ExperimentalSynapsesPerConnectionRead(BaseModel):
    subject: NestedSubjectRead
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    type: EntityType | None = None
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license: LicenseRead | None = None
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    measurements: Annotated[list[MeasurementRecordRead], Field(title="Measurements")]
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    brain_region: BrainRegionRead
    pre_mtype: AnnotationRead
    post_mtype: AnnotationRead
    pre_region: BrainRegionRead
    post_region: BrainRegionRead


class ExperimentalSynapsesPerConnectionUserUpdate(BaseModel):
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    legacy_id: Annotated[str | None, Field(title="Legacy Id")] = "<NOT_SET>"
    measurements: Annotated[
        list[MeasurementRecordCreate] | str | None, Field(title="Measurements")
    ] = "<NOT_SET>"
    pre_mtype_id: Annotated[UUID | str | None, Field(title="Pre Mtype Id")] = "<NOT_SET>"
    post_mtype_id: Annotated[UUID | str | None, Field(title="Post Mtype Id")] = "<NOT_SET>"
    pre_region_id: Annotated[UUID | str | None, Field(title="Pre Region Id")] = "<NOT_SET>"
    post_region_id: Annotated[UUID | str | None, Field(title="Post Region Id")] = "<NOT_SET>"


class IonChannelModelAdminUpdate(BaseModel):
    authorized_public: Annotated[bool | str | None, Field(title="Authorized Public")] = "<NOT_SET>"
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    nmodl_suffix: Annotated[str | None, Field(title="Nmodl Suffix")] = "<NOT_SET>"
    is_ljp_corrected: Annotated[bool | str | None, Field(title="Is Ljp Corrected")] = "<NOT_SET>"
    is_temperature_dependent: Annotated[
        bool | str | None, Field(title="Is Temperature Dependent")
    ] = "<NOT_SET>"
    temperature_celsius: Annotated[int | str | None, Field(title="Temperature Celsius")] = (
        "<NOT_SET>"
    )
    is_stochastic: Annotated[bool | str | None, Field(title="Is Stochastic")] = "<NOT_SET>"
    neuron_block: Annotated[NeuronBlock | str | None, Field(title="Neuron Block")] = "<NOT_SET>"


class IonChannelModelCreate(BaseModel):
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    license_id: Annotated[UUID | None, Field(title="License Id")] = None
    brain_region_id: Annotated[UUID, Field(title="Brain Region Id")]
    subject_id: Annotated[UUID, Field(title="Subject Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    description: Annotated[str, Field(title="Description")]
    name: Annotated[str, Field(title="Name")]
    nmodl_suffix: Annotated[str, Field(title="Nmodl Suffix")]
    is_ljp_corrected: Annotated[bool | None, Field(title="Is Ljp Corrected")] = False
    is_temperature_dependent: Annotated[bool | None, Field(title="Is Temperature Dependent")] = (
        False
    )
    temperature_celsius: Annotated[int, Field(title="Temperature Celsius")]
    is_stochastic: Annotated[bool | None, Field(title="Is Stochastic")] = False
    neuron_block: NeuronBlock


class IonChannelModelExpanded(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    license: LicenseRead | None = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    brain_region: BrainRegionRead
    subject: NestedSubjectRead
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    description: Annotated[str, Field(title="Description")]
    name: Annotated[str, Field(title="Name")]
    nmodl_suffix: Annotated[str, Field(title="Nmodl Suffix")]
    is_ljp_corrected: Annotated[bool | None, Field(title="Is Ljp Corrected")] = False
    is_temperature_dependent: Annotated[bool | None, Field(title="Is Temperature Dependent")] = (
        False
    )
    temperature_celsius: Annotated[int, Field(title="Temperature Celsius")]
    is_stochastic: Annotated[bool | None, Field(title="Is Stochastic")] = False
    neuron_block: NeuronBlock


class IonChannelModelRead(BaseModel):
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    brain_region: BrainRegionRead
    subject: NestedSubjectRead
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    description: Annotated[str, Field(title="Description")]
    name: Annotated[str, Field(title="Name")]
    nmodl_suffix: Annotated[str, Field(title="Nmodl Suffix")]
    is_ljp_corrected: Annotated[bool | None, Field(title="Is Ljp Corrected")] = False
    is_temperature_dependent: Annotated[bool | None, Field(title="Is Temperature Dependent")] = (
        False
    )
    temperature_celsius: Annotated[int, Field(title="Temperature Celsius")]
    is_stochastic: Annotated[bool | None, Field(title="Is Stochastic")] = False
    neuron_block: NeuronBlock


class IonChannelModelUserUpdate(BaseModel):
    license_id: Annotated[UUID | str | None, Field(title="License Id")] = "<NOT_SET>"
    brain_region_id: Annotated[UUID | str | None, Field(title="Brain Region Id")] = "<NOT_SET>"
    subject_id: Annotated[UUID | str | None, Field(title="Subject Id")] = "<NOT_SET>"
    experiment_date: Annotated[AwareDatetime | str | None, Field(title="Experiment Date")] = (
        "<NOT_SET>"
    )
    contact_email: Annotated[str | None, Field(title="Contact Email")] = "<NOT_SET>"
    published_in: Annotated[str | None, Field(title="Published In")] = "<NOT_SET>"
    description: Annotated[str | None, Field(title="Description")] = "<NOT_SET>"
    name: Annotated[str | None, Field(title="Name")] = "<NOT_SET>"
    nmodl_suffix: Annotated[str | None, Field(title="Nmodl Suffix")] = "<NOT_SET>"
    is_ljp_corrected: Annotated[bool | str | None, Field(title="Is Ljp Corrected")] = "<NOT_SET>"
    is_temperature_dependent: Annotated[
        bool | str | None, Field(title="Is Temperature Dependent")
    ] = "<NOT_SET>"
    temperature_celsius: Annotated[int | str | None, Field(title="Temperature Celsius")] = (
        "<NOT_SET>"
    )
    is_stochastic: Annotated[bool | str | None, Field(title="Is Stochastic")] = "<NOT_SET>"
    neuron_block: Annotated[NeuronBlock | str | None, Field(title="Neuron Block")] = "<NOT_SET>"


class IonChannelModelWAssets(BaseModel):
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    brain_region: BrainRegionRead
    subject: NestedSubjectRead
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    description: Annotated[str, Field(title="Description")]
    name: Annotated[str, Field(title="Name")]
    nmodl_suffix: Annotated[str, Field(title="Nmodl Suffix")]
    is_ljp_corrected: Annotated[bool | None, Field(title="Is Ljp Corrected")] = False
    is_temperature_dependent: Annotated[bool | None, Field(title="Is Temperature Dependent")] = (
        False
    )
    temperature_celsius: Annotated[int, Field(title="Temperature Celsius")]
    is_stochastic: Annotated[bool | None, Field(title="Is Stochastic")] = False
    neuron_block: NeuronBlock


class IonChannelRecordingRead(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    license: LicenseRead | None = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    brain_region: BrainRegionRead
    subject: NestedSubjectRead
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    ljp: Annotated[
        float | None,
        Field(
            description="Correction applied to the voltage trace, in mV",
            title="Liquid Junction Potential",
        ),
    ] = 0.0
    recording_location: Annotated[
        list[str],
        Field(
            description="Location on the cell where recording was performed, in hoc-compatible format.",
            title="Recording Location",
        ),
    ]
    recording_type: Annotated[
        ElectricalRecordingType,
        Field(
            description="Recording type. One of: [<ElectricalRecordingStimulusType.conductance_clamp: 'conductance_clamp'>, <ElectricalRecordingStimulusType.current_clamp: 'current_clamp'>, <ElectricalRecordingStimulusType.extracellular: 'extracellular'>, <ElectricalRecordingStimulusType.other: 'other'>, <ElectricalRecordingStimulusType.unknown: 'unknown'>, <ElectricalRecordingStimulusType.voltage_clamp: 'voltage_clamp'>]",
            title="Recording Type",
        ),
    ]
    recording_origin: Annotated[
        ElectricalRecordingOrigin,
        Field(
            description="Recording origin. One of: [<ElectricalRecordingOrigin.in_silico: 'in_silico'>, <ElectricalRecordingOrigin.in_vitro: 'in_vitro'>, <ElectricalRecordingOrigin.in_vivo: 'in_vivo'>, <ElectricalRecordingOrigin.unknown: 'unknown'>]",
            title="Recording Origin",
        ),
    ]
    temperature: Annotated[
        float | None,
        Field(
            description="Temperature at which the recording was performed, in degrees Celsius.",
            title="Temperature",
        ),
    ] = None
    comment: Annotated[
        str | None, Field(description="Comment with further details.", title="Comment")
    ] = None
    legacy_id: Annotated[list[str] | None, Field(title="Legacy Id")] = None
    cell_line: Annotated[
        str,
        Field(
            description="The cell line from which the ion channel was recorded", title="Cell Line"
        ),
    ]
    ion_channel: Annotated[
        NestedIonChannelRead,
        Field(description="The ion channel that was recorded from", title="Ion Channel"),
    ]
    stimuli: Annotated[
        list[NestedElectricalRecordingStimulusRead] | None,
        Field(
            description="List of stimuli applied to the cell with their respective time steps",
            title="Electrical Recording Stimuli",
        ),
    ] = None


class ListResponseAnalysisNotebookEnvironmentRead(BaseModel):
    data: Annotated[list[AnalysisNotebookEnvironmentRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseAnalysisNotebookExecutionRead(BaseModel):
    data: Annotated[list[AnalysisNotebookExecutionRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseAnalysisNotebookResultRead(BaseModel):
    data: Annotated[list[AnalysisNotebookResultRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseAnalysisNotebookTemplateRead(BaseModel):
    data: Annotated[list[AnalysisNotebookTemplateRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseCellCompositionRead(BaseModel):
    data: Annotated[list[CellCompositionRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseCellMorphologyProtocolRead(BaseModel):
    data: Annotated[list[CellMorphologyProtocolRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseCircuitRead(BaseModel):
    data: Annotated[list[CircuitRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseEMCellMeshRead(BaseModel):
    data: Annotated[list[EMCellMeshRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseEMDenseReconstructionDatasetRead(BaseModel):
    data: Annotated[list[EMDenseReconstructionDatasetRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseElectricalCellRecordingRead(BaseModel):
    data: Annotated[list[ElectricalCellRecordingRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseExperimentalBoutonDensityRead(BaseModel):
    data: Annotated[list[ExperimentalBoutonDensityRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseExperimentalNeuronDensityRead(BaseModel):
    data: Annotated[list[ExperimentalNeuronDensityRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseExperimentalSynapsesPerConnectionRead(BaseModel):
    data: Annotated[list[ExperimentalSynapsesPerConnectionRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseIonChannelModelRead(BaseModel):
    data: Annotated[list[IonChannelModelRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseIonChannelRecordingRead(BaseModel):
    data: Annotated[list[IonChannelRecordingRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseMEModelCalibrationResultRead(BaseModel):
    data: Annotated[list[MEModelCalibrationResultRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseMTypeClassificationRead(BaseModel):
    data: Annotated[list[MTypeClassificationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseSimulationCampaignRead(BaseModel):
    data: Annotated[list[SimulationCampaignRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseSimulationExecutionRead(BaseModel):
    data: Annotated[list[SimulationExecutionRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseSimulationRead(BaseModel):
    data: Annotated[list[SimulationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseSimulationResultRead(BaseModel):
    data: Annotated[list[SimulationResultRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseSingleNeuronSimulationRead(BaseModel):
    data: Annotated[list[SingleNeuronSimulationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseSingleNeuronSynaptomeRead(BaseModel):
    data: Annotated[list[SingleNeuronSynaptomeRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseSingleNeuronSynaptomeSimulationRead(BaseModel):
    data: Annotated[list[SingleNeuronSynaptomeSimulationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseValidationResultRead(BaseModel):
    data: Annotated[list[ValidationResultRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class MeasurementAnnotationAdminUpdate(BaseModel):
    entity_id: Annotated[UUID | str | None, Field(title="Entity Id")] = "<NOT_SET>"
    entity_type: Annotated[MeasurableEntity | str | None, Field(title="Entity Type")] = "<NOT_SET>"
    measurement_kinds: Annotated[
        list[MeasurementKindCreate] | str | None, Field(title="Measurement Kinds")
    ] = "<NOT_SET>"


class MeasurementAnnotationCreate(BaseModel):
    entity_id: Annotated[UUID, Field(title="Entity Id")]
    entity_type: MeasurableEntity
    measurement_kinds: Annotated[list[MeasurementKindCreate], Field(title="Measurement Kinds")]


class MeasurementAnnotationRead(BaseModel):
    id: Annotated[UUID, Field(title="Id")]
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    entity_id: Annotated[UUID, Field(title="Entity Id")]
    entity_type: MeasurableEntity
    measurement_kinds: Annotated[list[MeasurementKindRead], Field(title="Measurement Kinds")]


class MeasurementAnnotationUserUpdate(BaseModel):
    entity_id: Annotated[UUID | str | None, Field(title="Entity Id")] = "<NOT_SET>"
    entity_type: Annotated[MeasurableEntity | str | None, Field(title="Entity Type")] = "<NOT_SET>"
    measurement_kinds: Annotated[
        list[MeasurementKindCreate] | str | None, Field(title="Measurement Kinds")
    ] = "<NOT_SET>"


class NestedCellMorphologyProtocolRead(
    RootModel[
        NestedDigitalReconstructionCellMorphologyProtocolRead
        | NestedModifiedReconstructionCellMorphologyProtocolRead
        | NestedComputationallySynthesizedCellMorphologyProtocolRead
        | NestedPlaceholderCellMorphologyProtocolRead
    ]
):
    root: Annotated[
        NestedDigitalReconstructionCellMorphologyProtocolRead
        | NestedModifiedReconstructionCellMorphologyProtocolRead
        | NestedComputationallySynthesizedCellMorphologyProtocolRead
        | NestedPlaceholderCellMorphologyProtocolRead,
        Field(discriminator="generation_type"),
    ]


class CellMorphologyAnnotationExpandedRead(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    license: LicenseRead | None = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    brain_region: BrainRegionRead
    subject: NestedSubjectRead
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    location: PointLocationBase | None = None
    legacy_id: Annotated[list[str] | None, Field(title="Legacy Id")] = None
    mtypes: Annotated[list[AnnotationRead] | None, Field(title="Mtypes")] = None
    cell_morphology_protocol: NestedCellMorphologyProtocolRead | None = None
    measurement_annotation: MeasurementAnnotationRead | None = None


class CellMorphologyRead(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    license: LicenseRead | None = None
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    brain_region: BrainRegionRead
    subject: NestedSubjectRead
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    type: EntityType | None = None
    id: Annotated[UUID, Field(title="Id")]
    experiment_date: Annotated[AwareDatetime | None, Field(title="Experiment Date")] = None
    contact_email: Annotated[str | None, Field(title="Contact Email")] = None
    published_in: Annotated[str | None, Field(title="Published In")] = None
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    location: PointLocationBase | None = None
    legacy_id: Annotated[list[str] | None, Field(title="Legacy Id")] = None
    mtypes: Annotated[list[AnnotationRead] | None, Field(title="Mtypes")] = None
    cell_morphology_protocol: NestedCellMorphologyProtocolRead | None = None


class EModelReadExpanded(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    assets: Annotated[list[AssetRead], Field(title="Assets")]
    type: EntityType | None = None
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    description: Annotated[str, Field(title="Description")]
    name: Annotated[str, Field(title="Name")]
    iteration: Annotated[str, Field(title="Iteration")]
    score: Annotated[float, Field(title="Score")]
    seed: Annotated[int, Field(title="Seed")]
    id: Annotated[UUID, Field(title="Id")]
    species: NestedSpeciesRead
    strain: NestedStrainRead | None = None
    brain_region: BrainRegionRead
    mtypes: Annotated[list[AnnotationRead] | None, Field(title="Mtypes")] = None
    etypes: Annotated[list[AnnotationRead] | None, Field(title="Etypes")] = None
    exemplar_morphology: ExemplarMorphology
    ion_channel_models: Annotated[list[IonChannelModelWAssets], Field(title="Ion Channel Models")]


class ListResponseCellMorphologyRead(BaseModel):
    data: Annotated[list[CellMorphologyRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseEModelReadExpanded(BaseModel):
    data: Annotated[list[EModelReadExpanded], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class ListResponseMeasurementAnnotationRead(BaseModel):
    data: Annotated[list[MeasurementAnnotationRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


class MEModelRead(BaseModel):
    contributions: Annotated[list[NestedContributionRead] | None, Field(title="Contributions")] = (
        None
    )
    created_by: NestedPersonRead
    updated_by: NestedPersonRead
    type: EntityType | None = None
    authorized_project_id: Annotated[UUID4, Field(title="Authorized Project Id")]
    authorized_public: Annotated[bool | None, Field(title="Authorized Public")] = False
    creation_date: Annotated[AwareDatetime, Field(title="Creation Date")]
    update_date: Annotated[AwareDatetime, Field(title="Update Date")]
    name: Annotated[str, Field(title="Name")]
    description: Annotated[str, Field(title="Description")]
    validation_status: ValidationStatus | None = "created"
    id: Annotated[UUID, Field(title="Id")]
    species: NestedSpeciesRead
    strain: NestedStrainRead | None = None
    brain_region: BrainRegionRead
    mtypes: Annotated[list[AnnotationRead] | None, Field(title="Mtypes")] = None
    etypes: Annotated[list[AnnotationRead] | None, Field(title="Etypes")] = None
    morphology: CellMorphologyRead
    emodel: EModelRead
    calibration_result: MEModelCalibrationResultRead | None = None


class ListResponseMEModelRead(BaseModel):
    data: Annotated[list[MEModelRead], Field(title="Data")]
    pagination: PaginationResponse
    facets: Facets | None = None


HierarchyNode.model_rebuild()
