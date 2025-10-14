# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import json
import logging
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union

import pandas as pd
from nemo_microservices import NeMoMicroservices
from nemo_microservices.resources.data_designer.jobs.jobs import DataDesignerJobConfigParam

from ..config.analysis.dataset_profiler import DatasetProfilerResults
from ..config.config_builder import DataDesignerConfigBuilder
from ..config.datastore import DatastoreSettings, resolve_datastore_settings, upload_to_hf_hub
from ..config.seed import SeedDatasetReference
from .errors import DataDesignerClientError, handle_api_exceptions
from .results.jobs import DataDesignerJobResults
from .results.preview import MessageType, PreviewResults
from .utils.emoji_helpers import get_random_success_emoji

logger = logging.getLogger(__name__)

DEFAULT_PREVIEW_TIMEOUT = 120
DEFAULT_NUM_RECORDS_FOR_PREVIEW = 10


class NeMoDataDesignerClient:
    """Client for interacting with the NeMo Data Designer service.

    The NeMoDataDesignerClient provides a high-level interface for generating synthetic datasets
    using the NeMo Data Designer service. It supports creating batch data generation jobs,
    running data generation previews, and managing datasets through the datastore.

    The client can be initialized with either an existing NeMoMicroservices client or a base URL
    to create a new connection.
    """

    def __init__(self, *, client: Optional[NeMoMicroservices] = None, base_url: Optional[str] = None, **kwargs):
        """Initialize the NeMoDataDesignerClient.

        Args:
            client: An existing NeMoMicroservices client instance. If provided, this will be used
                instead of creating a new client. Mutually exclusive with base_url.
            base_url: The base URL of the NeMo Microservices instance. Used to create a new
                NeMoMicroservices client if no client is provided. Mutually exclusive with client.
            **kwargs: Additional keyword arguments passed to NeMoMicroservices constructor when
                creating a new client. Ignored if client is provided.

        Raises:
            DataDesignerClientError: If neither client nor base_url is provided.

        Note:
            Either client or base_url must be provided, but not both. If both are provided,
            the client parameter takes precedence.
        """
        if client is None and base_url is None:
            raise DataDesignerClientError("🛑 Either client or base_url must be provided")

        self._client = client or NeMoMicroservices(base_url=base_url, **kwargs)
        self._data_designer_resource = self._client.data_designer
        self._datastore_settings: DatastoreSettings | None = None

    def create(
        self,
        config_builder: DataDesignerConfigBuilder,
        *,
        num_records: int = 100,
        wait_until_done: bool = False,
        name: str = "nemo-data-designer-job",
        project: str = "nemo-data-designer",
    ) -> DataDesignerJobResults:
        """Create a Data Designer generation job.

        Args:
            config_builder: Data Designer configuration builder.
            num_records: The number of records to generate.
            wait_until_done: Whether to halt your program until the job is done.
            name: Name label for the job within the NeMo Microservices project.
            project: Name of the NeMo Microservices project.

        Returns:
            An object with methods for querying the job's status and results.
        """
        logger.info("🎨 Creating Data Designer generation job")
        try:
            job = self._data_designer_resource.jobs.create(
                name=name,
                project=project,
                spec=DataDesignerJobConfigParam(
                    num_records=num_records,
                    config=config_builder.build(raise_exceptions=True),
                ),
            )
            logger.info(f"  |-- job_id: {job.id}")
            results = DataDesignerJobResults(job=job, client=self._client)
            if wait_until_done:
                results.wait_until_done()
            return results
        except Exception as e:
            handle_api_exceptions(e)

    def preview(
        self,
        config_builder: DataDesignerConfigBuilder,
        *,
        num_records: int | None = None,
        timeout: int | None = None,
    ) -> PreviewResults:
        """Generate a set of preview records based on your current Data Designer configuration.

        This method is meant for fast iteration on your Data Designer configuration.

        Args:
            config_builder: Data Designer configuration builder.
            num_records: The number of records to generate. Must be equal to or less than the max number of
                preview records set at deploy time.
            timeout: The timeout for the preview in seconds. If not provided, one will be set based on the model configs.

        Returns:
            An object containing the preview dataset and tools for inspecting the results.
        """
        try:
            return self._capture_preview_result(config_builder=config_builder, num_records=num_records, timeout=timeout)
        except Exception as e:
            handle_api_exceptions(e)

    def get_datastore_settings(self) -> Optional[DatastoreSettings]:
        """Get the current datastore settings.

        Returns:
            The current datastore settings if it has been set, None otherwise.
        """
        return self._datastore_settings

    def get_job_results(self, job_id: str) -> DataDesignerJobResults:
        """Retrieve results for an existing data generation job.

        Args:
            job_id: The unique identifier of the job to retrieve results for.

        Returns:
            An object containing methods for querying job status,
            retrieving the generated dataset, and accessing job metadata.

        Raises:
            ValueError: If the job ID provided is empty.
        """
        job = self._data_designer_resource.jobs.retrieve(job_id)
        return DataDesignerJobResults(job=job, client=self._client)

    def upload_seed_dataset(
        self,
        dataset: Union[str, Path, pd.DataFrame],
        repo_id: str,
        datastore_settings: DatastoreSettings,
    ) -> SeedDatasetReference:
        """Upload a dataset to the datastore and return the reference for fetching the dataset.

        This function handles different dataset input types and automatically manages temporary files
        for DataFrame uploads. For DataFrame inputs, a temporary parquet file is created and
        automatically cleaned up after upload.

        Args:
            dataset: Dataset to upload. Can be:
                - pandas.DataFrame: Will be saved as a temporary parquet file.
                - str: Path to an existing dataset file.
                - Path: Path object pointing to an existing dataset file.
            repo_id: Repository ID for the datastore where the dataset will be uploaded.
            datastore_settings: Configuration settings for the datastore connection.

        Returns:
            Seed dataset reference returned from the datastore upload.
        """
        self._datastore_settings = resolve_datastore_settings(datastore_settings)
        logger.info("🔄 Uploading seed dataset to datastore")
        with _dataset_filename_and_path(dataset) as file_info:
            dataset_id = upload_to_hf_hub(
                dataset_path=file_info["dataset_path"],
                filename=file_info["filename"],
                repo_id=repo_id,
                datastore_settings=self._datastore_settings,
            )
        return SeedDatasetReference(dataset=dataset_id, datastore_settings=self._datastore_settings)

    def _capture_preview_result(
        self,
        config_builder: DataDesignerConfigBuilder,
        num_records: int | None,
        timeout: int | None,
    ) -> PreviewResults:
        """Capture the results (including logs) of a workflow preview.

        Args:
            config_builder: The data designer configuration builder containing the generation
                parameters and column definitions.
            num_records: The number of records to generate for the preview. Must be equal to or less than the max number of
                preview records set at deploy time. If None, uses the default number of records for preview.
            timeout: The timeout in seconds for the preview operation. If None, a timeout
                will be calculated based on the model configurations.

        Returns:
            An object containing the generated dataset, analysis results, and the original configuration builder.
        """
        config = config_builder.build(raise_exceptions=True)

        dataset = None
        analysis = None
        log_levels_seen = set()
        timeout = _resolve_timeout(timeout, config_builder, num_records)

        logger.info("🚀 Starting preview generation")
        for response in self._data_designer_resource.preview(config=config, num_records=num_records, timeout=timeout):
            if response.message_type == MessageType.HEARTBEAT:
                continue
            if response.message_type == MessageType.LOG:
                level = response.extra["level"].lower()
                log_levels_seen.add(level)
                if level == "info":
                    logger.info(response.message)
                elif level in {"warning", "warn"}:
                    logger.warning(response.message)
                elif level == "error":
                    logger.error(response.message)
            elif response.message_type == MessageType.DATASET:
                try:
                    dataset = pd.DataFrame.from_dict(json.loads(response.message))
                except Exception as e:
                    logger.error(f"🛑 Error loading dataset: {e}")
                    log_levels_seen.add("error")
            elif response.message_type == MessageType.ANALYSIS:
                try:
                    analysis = DatasetProfilerResults.model_validate_json(response.message)
                except Exception as e:
                    logger.error(f"🛑 Error loading analysis: {e}")
                    log_levels_seen.add("error")

        if "error" in log_levels_seen:
            logger.error("🛑 Preview completed with errors.")
        elif "warning" in log_levels_seen or "warn" in log_levels_seen:
            logger.warning("⚠️ Preview completed with warnings.")
        else:
            logger.info(f"{get_random_success_emoji()} Preview complete!")

        return PreviewResults(
            config_builder=config_builder,
            dataset=dataset,
            analysis=analysis,
        )


def _resolve_timeout(
    timeout: int | None,
    config_builder: DataDesignerConfigBuilder,
    num_records: int | None,
) -> int:
    """Resolve the appropriate timeout value for preview operations.

    This function calculates the appropriate timeout based on the configuration and
    number of records. If a timeout is explicitly provided, it uses that value.
    Otherwise, it calculates a timeout based on the model configurations and
    the number of records to generate.

    Args:
        timeout: Explicit timeout value in seconds. If provided, this value is
            returned without further calculation.
        config_builder: The data designer configuration builder containing model
            configurations with their individual timeout settings.
        num_records: The number of records to generate. Used in timeout calculation
            if no explicit timeout is provided. If None, uses the default number
            of records for preview.

    Returns:
        The resolved timeout value in seconds. This will be either the explicit
        timeout, a calculated timeout based on model configurations, or the
        default preview timeout.

    Note:
        The calculated timeout is based on the maximum timeout from all model
        configurations, multiplied by the number of LLM generation columns and
        the number of records. This provides a reasonable estimate for the time
        needed to complete the preview operation.
    """
    if timeout is not None:
        return timeout
    timeouts = []
    for model_config in config_builder.model_configs:
        if model_config.inference_parameters.timeout is not None:
            timeouts.append(model_config.inference_parameters.timeout)
    if len(timeouts) > 0:
        # Multiply the highest timeout by the number of llm columns and the number of records
        return (
            max(timeouts) * len(config_builder.get_llm_gen_columns()) * (num_records or DEFAULT_NUM_RECORDS_FOR_PREVIEW)
        )
    return DEFAULT_PREVIEW_TIMEOUT


@contextmanager
def _dataset_filename_and_path(dataset: Union[str, Path, pd.DataFrame]) -> Generator[dict[str, str], None, None]:
    """Context manager for handling different dataset input types.

    This context manager provides a unified interface for handling different types of
    dataset inputs (DataFrame, file path, or Path object) and ensures proper cleanup
    of temporary files when needed.

    For DataFrame inputs, a temporary parquet file is created and automatically
    cleaned up when the context exits. For file path inputs, the existing file
    is used directly.

    Args:
        dataset: The dataset to process. Can be:
            - pandas.DataFrame: Will be saved as a temporary parquet file that is
              automatically cleaned up when the context exits.
            - str: Path to an existing dataset file as a string.
            - Path: Path object pointing to an existing dataset file.

    Yields:
        A dictionary containing:
            - "filename": The filename to use for the dataset (extracted from path
              or set to a default name for DataFrames).
            - "dataset_path": The actual file path to the dataset (temporary file
              for DataFrames, original path for file inputs).
    """
    if isinstance(dataset, pd.DataFrame):
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=True) as temp_file:
            dataset.to_parquet(temp_file.name, index=False)
            yield {"filename": "seed-dataset-dataframe.parquet", "dataset_path": temp_file.name}
    else:
        # For Path or str, use the dataset as the path and extract filename
        dataset_path = str(dataset)
        filename = Path(dataset).name
        yield {"filename": filename, "dataset_path": dataset_path}
