# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .shared_params.upload import Upload
from .shared_params.parse_options import ParseOptions
from .shared_params.config_v3_async_config import ConfigV3AsyncConfig

__all__ = [
    "ExtractRunParams",
    "SyncExtractConfig",
    "SyncExtractConfigInput",
    "SyncExtractConfigInstructions",
    "SyncExtractConfigSettings",
    "SyncExtractConfigSettingsCitations",
    "AsyncExtractConfig",
    "AsyncExtractConfigInput",
    "AsyncExtractConfigInstructions",
    "AsyncExtractConfigSettings",
    "AsyncExtractConfigSettingsCitations",
]


class SyncExtractConfig(TypedDict, total=False):
    input: Required[SyncExtractConfigInput]
    """The URL of the document to be processed.

    You can provide one of the following: 1. A publicly available URL 2. A presigned
    S3 URL 3. A reducto:// prefixed URL obtained from the /upload endpoint after
    directly uploading a document 4. A jobid:// prefixed URL obtained from a
    previous /parse invocation
    """

    instructions: SyncExtractConfigInstructions
    """The instructions to use for the extraction."""

    parsing: ParseOptions
    """The configuration options for parsing the document.

    If you are passing in a jobid:// URL for the file, then this configuration will
    be ignored.
    """

    settings: SyncExtractConfigSettings
    """The settings to use for the extraction."""


SyncExtractConfigInput: TypeAlias = Union[str, Upload]


class SyncExtractConfigInstructions(TypedDict, total=False):
    schema: object
    """The JSON schema to use for the extraction."""

    system_prompt: str
    """The system prompt to use for the extraction."""


class SyncExtractConfigSettingsCitations(TypedDict, total=False):
    enabled: bool
    """If True, include citations in the extraction."""

    numerical_confidence: bool
    """If True, enable numeric citation confidence scores. Defaults to True."""


class SyncExtractConfigSettings(TypedDict, total=False):
    array_extract: bool
    """If True, use array extraction."""

    citations: SyncExtractConfigSettingsCitations
    """The citations to use for the extraction."""

    include_images: bool
    """If True, include images in the extraction."""

    optimize_for_latency: bool
    """
    If True, jobs will be processed with a higher throughput and priority at a
    higher cost. Defaults to False.
    """


class AsyncExtractConfig(TypedDict, total=False):
    input: Required[AsyncExtractConfigInput]
    """The URL of the document to be processed.

    You can provide one of the following: 1. A publicly available URL 2. A presigned
    S3 URL 3. A reducto:// prefixed URL obtained from the /upload endpoint after
    directly uploading a document 4. A jobid:// prefixed URL obtained from a
    previous /parse invocation
    """

    async_: Annotated[ConfigV3AsyncConfig, PropertyInfo(alias="async")]
    """The configuration options for asynchronous processing (default synchronous)."""

    instructions: AsyncExtractConfigInstructions
    """The instructions to use for the extraction."""

    parsing: ParseOptions
    """The configuration options for parsing the document.

    If you are passing in a jobid:// URL for the file, then this configuration will
    be ignored.
    """

    settings: AsyncExtractConfigSettings
    """The settings to use for the extraction."""


AsyncExtractConfigInput: TypeAlias = Union[str, Upload]


class AsyncExtractConfigInstructions(TypedDict, total=False):
    schema: object
    """The JSON schema to use for the extraction."""

    system_prompt: str
    """The system prompt to use for the extraction."""


class AsyncExtractConfigSettingsCitations(TypedDict, total=False):
    enabled: bool
    """If True, include citations in the extraction."""

    numerical_confidence: bool
    """If True, enable numeric citation confidence scores. Defaults to True."""


class AsyncExtractConfigSettings(TypedDict, total=False):
    array_extract: bool
    """If True, use array extraction."""

    citations: AsyncExtractConfigSettingsCitations
    """The citations to use for the extraction."""

    include_images: bool
    """If True, include images in the extraction."""

    optimize_for_latency: bool
    """
    If True, jobs will be processed with a higher throughput and priority at a
    higher cost. Defaults to False.
    """


ExtractRunParams: TypeAlias = Union[SyncExtractConfig, AsyncExtractConfig]
