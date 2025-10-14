"""Models for OmnibusX SDK."""

from pydantic import BaseModel


class SequencingTechnology:
    """A namespace for sequencing technologies."""

    SC_RNA_SEQ = "sc_rna_seq"
    BULK_RNA_SEQ = "bulk_rna_seq"
    SC_ATAC_SEQ = "sc_atac_seq"
    BULK_ATAC_SEQ = "bulk_atac_seq"
    WELL_BASED_SPATIAL = "well_based_spatial"


class SequencingPlatform:
    """A namespace for sequencing platform."""

    class ScRnaSeq:
        """A namespace for scRNAseq sequencing platform."""

        CHROMIUM_10X = "10x"
        CHROMIUM_AND_IMMUNE_RECEPTOR_10X = "immune_10x"
        CITE_SEQ = "cite_seq"
        SMART_SEQ_2 = "smart_seq2"
        DROP_SEQ = "drop_seq"
        OTHERS = "unknown"

    class BulkRnaSeq:
        """A namespace for bulk RNAseq sequencing platform."""

        ILLUMINA = "illumina"

    class ScAtacSeq:
        """A namespace for scATACseq sequencing platform."""

        ATACSEQ_10X = "10x_atacseq"
        ATACSEQ_GEX_10X = "10x_atacseq_gex"

    class WellBasedSpatial:
        """A namespace for well-based spatial sequencing platform."""

        VISIUM_10X = "10x_visium"
        VISIUM_HD_10X = "10x_visium_hd"
        GEOMX_DSP = "geomx_dsp"
        SLIDE_SEQ = "slide_seq"


class DataFormat:
    """A namespace for data formats."""

    SCANPY = "scanpy"
    SEURAT = "seurat"
    TEXT = "text"
    TAB = "tab"
    TAB_HTSEQ = "tab_htseq"
    TAB_KALLISTO = "tab_kallisto"
    TAB_FEATURECOUNTS = "tab_featurecounts"
    TAB_STAR = "tab_star"
    H5_10X = "h5_10x"
    MTX_10X = "mtx_10x"
    IMMUNE_10X = "immune_10x"
    VISIUM = "visium"
    VISIUM_HD = "visium_hd"
    VISIUM_AGGR = "visium_aggr"
    GEOMX_DSP = "geomx_dsp"
    GEOMX_IPA = "geomx_ipa"
    ATAC_H5 = "atac_h5"
    ATAC_MTX = "atac_mtx"
    ATAC_GEX_H5 = "atac_gex_h5"
    ATAC_GEX_MTX = "atac_gex_mtx"


class GeneReferenceVersion:
    """A namespace for gene reference versions."""

    ENSEMBL_111 = 111


class Species:
    """A namespace for species."""

    HUMAN = "Homo_sapiens"
    MOUSE = "Mus_musculus"


class FileLocation:
    """A namespace for file location."""

    SERVER = "server"


class TaskType:
    """A namespace for task type."""

    IMPORT_OMNIBUSX_FILE = "IMPORT_OMNIBUSX_FILE"
    PREPROCESS_DATASET = "PREPROCESS_DATASET"


class TaskStatus:
    """A namespace for task status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"


class SampleBatch(BaseModel):
    """A namespace for sample batch."""

    file_path: str
    batch_name: str


class UserGroup(BaseModel):
    """A namespace for user group."""

    user_group_id: str
    name: str
    description: str


class ImportOmnibusXFileParams(BaseModel):
    """A namespace for importing an omnibusx file parameters."""

    omnibusx_file_path: str
    group_id: str


class AddTaskParams(BaseModel):
    """A namespace for adding new task parameters."""

    task_type: str
    params: ImportOmnibusXFileParams | dict


class AddTaskResponse(BaseModel):
    """A namespace for add task response."""

    task_id: str


class TaskLog(BaseModel):
    """A namespace for task."""

    id: str
    task_type: str
    dataset_id: str
    created_at: int
    finished_at: int
    status: str
    log: str
    params: str
    result: str
    is_committed: bool
