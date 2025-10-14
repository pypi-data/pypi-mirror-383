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

import io
import json
import logging
import tarfile
import tempfile
import time
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Callable, TypeVar, Union, get_args

import pandas as pd
from nemo_microservices._exceptions import NotFoundError
from nemo_microservices.types.jobs import PlatformJobStatus

from ...config.analysis.dataset_profiler import DatasetProfilerResults
from ...config.utils.io_helpers import read_parquet_dataset
from ..utils.emoji_helpers import get_random_success_emoji
from .errors import DataDesignerJobError

if TYPE_CHECKING:
    from nemo_microservices import NeMoMicroservices
    from nemo_microservices.types.data_designer import DataDesignerJob

logger = logging.getLogger(__name__)


class StrEnum(str, Enum):
    pass


JobStatus = StrEnum("JobStatus", {s.upper(): s for s in get_args(PlatformJobStatus)})


CHECK_PROGRESS_LOG_MSG = (
    "To check on your job's progress, use the `get_job_status` method. "
    "If you want to wait until it's complete, use the `wait_until_done` method."
)
TERMINAL_JOB_STATUSES = [JobStatus.CANCELLED, JobStatus.CANCELLING, JobStatus.ERROR]
WAIT_INTERVAL_SECONDS = 1
MAX_CONSECUTIVE_POLL_ERRORS = 5
DATASET_RESULT_NAME = "dataset"
ANALYSIS_RESULT_NAME = "analysis"

T = TypeVar("T")


class DataDesignerJobResults:
    def __init__(self, *, job: DataDesignerJob, client: NeMoMicroservices):
        """Creates a new instance with results from a Data Designer batch job run.

        Args:
            job: A data designer job object.
            client: A nemo microservices client object.
        """
        self._job = job
        self._client = client
        self._data_designer_resource = self._client.data_designer
        self._consecutive_poll_errors = 0

    def get_job(self) -> DataDesignerJob:
        """Get the current job object.

        Returns:
            The job object with up-to-date details.
        """
        self._refresh_job()
        return self._job

    def get_job_status(self) -> str:
        """Get the current status of the job.

        Returns:
            The current job status.
        """
        return self.get_job().status

    def download_artifacts(
        self,
        output_path: Union[Path, str],
        *,
        artifacts_folder_name: str = "artifacts",
    ) -> Path:
        """Download and save the Job's artifacts to the specified path.

        Args:
            output_path: Save artifacts to this path.
            artifacts_folder_name: Name of the folder that will contain the artifacts.

        Returns:
            Path to the saved artifacts folder.
        """
        self._check_if_result_available(DATASET_RESULT_NAME)
        try:
            output_path = Path(output_path)
            logger.info(f"🏺 Downloading artifacts from Job with ID '{self._job.id}'")
            self._download_dataset(output_path / artifacts_folder_name)
            try:
                self._download_analysis(output_path / artifacts_folder_name)
            except NotFoundError:
                logger.warning(f"Did not find {ANALYSIS_RESULT_NAME!r} result for job")
            logger.info(f"✅ Artifacts downloaded to {output_path / artifacts_folder_name}")
            return output_path / artifacts_folder_name

        except Exception as e:
            raise DataDesignerJobError(f"🛑 Error downloading artifacts: {e}")

    def load_dataset(self) -> pd.DataFrame:
        """Download dataset and return it as a pandas DataFrame.

        Returns:
            The generated dataset as a pandas DataFrame.

        Raises:
            DataDesignerJobError: If the job is not completed or if there's an error loading the dataset.
        """
        self._check_if_result_available(DATASET_RESULT_NAME)
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                temp_dir = Path(temp_dir)
                self._download_dataset(temp_dir)
                return read_parquet_dataset(temp_dir / DATASET_RESULT_NAME)
            except Exception as e:
                raise DataDesignerJobError(f"🛑 Error loading dataset: {e}")

    def load_analysis(self) -> DatasetProfilerResults:
        """Download dataset analysis and return it as a DatasetProfilerResults object.

        Returns:
            The analysis results containing dataset statistics and profiling information.

        Raises:
            DataDesignerJobError: If the job is not completed or if there's an error loading the analysis.
        """
        self._check_if_result_available(ANALYSIS_RESULT_NAME)
        try:
            return DatasetProfilerResults.model_validate(
                self._data_designer_resource.jobs.results.download_analysis(job_id=self._job.id)
            )
        except Exception as e:
            raise DataDesignerJobError(f"🛑 Error loading analysis: {e}")

    def wait_until_done(self) -> None:
        """Wait for the job to complete and monitor its progress.

        This method blocks execution until the job reaches a terminal state.
        During the wait, it continuously monitors job logs and displays relevant messages to the user.

        The method will:
        - Poll the job status at regular intervals
        - Display log messages from the data designer service
        - Handle warnings and errors appropriately
        - Provide final status summary when complete
        """
        error_occurred = False
        warning_occurred = False
        seen_logs = []
        job_status = self.get_job_status()
        while job_status != JobStatus.COMPLETED:
            time.sleep(WAIT_INTERVAL_SECONDS)
            current_logs = self._poll_safe(self._fetch_job_logs, seen_logs)
            if current_logs != seen_logs:
                for log in current_logs[len(seen_logs) :]:
                    seen_logs.append(log)
                    if "data_designer" not in log["name"]:
                        continue
                    level = log["levelname"].lower()
                    if level == "info":
                        logger.info(log["message"])
                    elif level in {"warning", "warn"}:
                        logger.warning(log["message"])
                        warning_occurred = True
                    elif level == "error":
                        logger.error(log["message"])
                        error_occurred = True
            if job_status in TERMINAL_JOB_STATUSES:
                error_occurred = True
                logger.error(f"🛑 Terminating generation job with status `{job_status}`.")
                break
            job_status = self._poll_safe(self.get_job_status, job_status)
        if error_occurred:
            logger.error("🛑 Dataset generation completed with errors.")
        elif warning_occurred:
            logger.warning("⚠️ Dataset generation completed with warnings.")
        else:
            logger.info(f"{get_random_success_emoji()} Dataset generation completed successfully.")

    def check_if_complete(self, *, raise_if_not_complete: bool = False) -> bool:
        """Check if the job is in a completed state.

        Args:
            raise_if_not_complete: If True, raises DataDesignerJobError when job is not complete.
                                   If False, only logs warnings/errors without raising exceptions.

        Returns:
            True if job is completed, False otherwise.

        Raises:
            DataDesignerJobError: If raise_if_not_complete is True and job is not in completed state.
        """
        status = self.get_job_status()
        if status == JobStatus.COMPLETED:
            return True
        elif status == JobStatus.ACTIVE:
            msg = f"Your dataset generation job is still running. {CHECK_PROGRESS_LOG_MSG}"
            if raise_if_not_complete:
                raise DataDesignerJobError(f"🛑 {msg}")
            logger.warning(f"⏳ {msg}")
            return False
        elif status in TERMINAL_JOB_STATUSES:
            msg = f"🛑 Your dataset generation job stopped with status `{status}`."
            if raise_if_not_complete:
                raise DataDesignerJobError(msg)
            logger.error(msg)
            return False
        elif status in {JobStatus.CREATED, JobStatus.PENDING}:
            msg = (
                f"⏹️ Your dataset generation job is still in the queue with status `{status}`. {CHECK_PROGRESS_LOG_MSG}"
            )
            if raise_if_not_complete:
                raise DataDesignerJobError(msg)
            logger.warning(msg)
            return False
        else:
            msg = f"Your job is in an unknown state: `{status}`."
            if raise_if_not_complete:
                raise DataDesignerJobError(msg)
            logger.error(msg)
            return False
        return True

    def _check_if_result_available(self, result_name: str) -> None:
        status = self.get_job_status()
        if status == JobStatus.COMPLETED:
            pass
        elif status == JobStatus.ACTIVE or status in TERMINAL_JOB_STATUSES:
            try:
                self._data_designer_resource.jobs.results.retrieve(result_name, job_id=self._job.id)
                if status == JobStatus.ACTIVE:
                    logger.info("🍳 Your dataset is still cooking. Fetching completed results for your enjoyment.")
                else:
                    logger.warning(f"Job ended with status {status!r}. Fetching completed {result_name} result.")
            except NotFoundError:
                raise DataDesignerJobError(f"{result_name!r} result is not available.")
            except Exception as e:
                raise DataDesignerJobError(f"🛑 Error loading dataset: {e}")
        else:
            raise DataDesignerJobError(f"Current job status is {status!r}, results are not available.")

    def _download_analysis(self, artifact_path: Path) -> None:
        """Download and save the analysis results to a JSON file.

        Args:
            artifact_path: The directory path where the analysis file should be saved.
        """
        analysis_download = self._data_designer_resource.jobs.results.download_analysis(job_id=self._job.id)
        with open(artifact_path / f"{ANALYSIS_RESULT_NAME}.json", "w") as f:
            json.dump(analysis_download, f, indent=4)

    def _download_dataset(self, artifact_path: Path) -> None:
        """Download and extract the dataset from a tar archive.

        Args:
            artifact_path: The directory path where the dataset should be extracted.
        """
        dataset_download = self._data_designer_resource.jobs.results.download_dataset(job_id=self._job.id)
        with tarfile.open(fileobj=io.BytesIO(dataset_download.read()), mode="r:*") as tar:
            tar.extractall(path=artifact_path)

    def _fetch_job_logs(self) -> list[dict[str, str]]:
        """Page through and fetch all job logs.

        Args:
            job_id: The ID of the job to fetch logs for.

        Returns:
            A list of log entries, where each entry is a dictionary containing log information.
        """
        logs = []
        page_cursor = None
        while True:
            response = self._client.jobs.get_logs(self._job.id, page_cursor=page_cursor)
            for log in response.data:
                try:
                    deserialized = json.loads(log.message)
                    if isinstance(deserialized, dict) and "message" in deserialized:
                        logs.append(deserialized)
                except Exception:
                    pass
            if response.next_page is None:
                break
            page_cursor = response.next_page
        return logs

    def _refresh_job(self) -> None:
        """Refresh the job object with the latest status from the server."""
        self._job = self._data_designer_resource.jobs.retrieve(self._job.id)

    def _poll_safe(self, fn: Callable[[], T], fallback: T) -> T:
        """Wrapper function to add resilience to network calls made while polling.

        This method will call the provided function and, in the happy path,
        reset the consecutive errors counter and return the result.

        If an error occurs, the consecutive errors counter is incremented.
        - If the threshold is not yet met, the fallback value is returned. Typically
          the fallback value is the last cached response from the network call.
        - If the counter has met the threshold, the counter is reset for future use
          and the caught error is raised.
        """
        try:
            response = fn()
            self._consecutive_poll_errors = 0
            return response
        except Exception as e:
            self._consecutive_poll_errors += 1
            if self._consecutive_poll_errors >= MAX_CONSECUTIVE_POLL_ERRORS:
                self._consecutive_poll_errors = 0
                raise e
            else:
                return fallback
