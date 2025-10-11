"""Modules with classes for loading configurations with Pydantic validation."""

from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, PositiveInt, StringConstraints

from inatinqperf.adaptors.metric import Metric

NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]


class DatasetConfig(BaseModel):
    """Dataset definition within the main configuration."""

    dataset_id: NonEmptyStr
    # For multiple splits, HuggingFace accepts a single string with splits concatenated with the `+` symbol.
    splits: str
    directory: Path
    export_images: bool


class EmbeddingParams(BaseModel):
    """Configuration for the embedding model."""

    model_id: NonEmptyStr
    batch_size: PositiveInt
    directory: Path


class VectorDatabaseParams(BaseModel):
    """Configuration for parameters initializing a Vector Database."""

    metric: Metric | None
    model_config = ConfigDict(extra="allow")
    nlist: int | None = None
    m: int | None = None
    nbits: int | None = None
    nprobe: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return parameters, including extra fields, omitting unset values."""
        return {key: value for key, value in self.model_dump().items() if value is not None}


class VectorDatabaseConfig(BaseModel):
    """Configuration for Vector Database."""

    type: NonEmptyStr
    params: VectorDatabaseParams


class SearchParams(BaseModel):
    """Configuration for search parameters."""

    topk: int
    queries_file: Path


class Config(BaseModel):
    """Class encapsulating benchmark configuration with data validation."""

    dataset: DatasetConfig
    embedding: EmbeddingParams
    vectordb: VectorDatabaseConfig
    search: SearchParams
    update: dict[str, PositiveInt]
