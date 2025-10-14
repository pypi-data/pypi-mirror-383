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

import logging
import time
from base64 import b64encode
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import pandas as pd
from typing_extensions import Self

if TYPE_CHECKING:
    from nemo_microservices import NeMoMicroservices
    from nemo_microservices.types.beta.safe_synthesizer.jobs.results.safe_synthesizer_summary import (
        SafeSynthesizerSummary,
    )
    from nemo_microservices.types.jobs.platform_job_log import PlatformJobLog

logger = logging.getLogger(__name__)


class ReportHtml(object):
    """Class to hold the HTML report string."""

    def __init__(self, html: str):
        self.raw_html = html
        self.as_data_uri = f"data:text/html;base64,{b64encode(self.raw_html.encode()).decode()}"

    def save(self, path: str | Path) -> None:
        """Save the evaluation report to a file.

        Args:
            path: The path to save the report to.
        """
        with open(path, "w") as f:
            f.write(self.raw_html)

    def display_report_in_notebook(self, width="100%", height=1000) -> None:
        """Display the evaluation report in a jupyter notebook.

        Requires the IPython library to be installed.

        Args:
            width: The width of the iframe to display the report in.
            height: The height of the iframe to display the report in.
        """
        try:
            from IPython.display import IFrame, display
        except ImportError:
            logger.warning("IPython is required to display reports in notebooks. Report will not be displayed.")
            return

        display(IFrame(self.as_data_uri, width=width, height=height))

    @classmethod
    def read(cls, path: str | Path) -> Self:
        """Read the evaluation report from a file.

        Args:
            path: The path to read the report from.
        """
        with open(path, "r") as f:
            raw_html = f.read()
        return cls(raw_html)


class SafeSynthesizerJob:
    """Interface for convenient interaction with Safe Synthesizer jobs.

    This class provides a wrapper around the Safe Synthesizer job SDK to make common operations easier.

    An instance is returned from the `create_job` method of the `SafeSynthesizerBuilder` class.
    Or create an instance with a job id and a NeMoMicroservices client.

    Examples:
        ```python
        >>> from nemo_microservices import NeMoMicroservices
        >>> from nemo_microservices.beta.safe_synthesizer.sdk.job import SafeSynthesizerJob

        >>> client = NeMoMicroservices(base_url=..., inference_base_url=...)
        >>> job = SafeSynthesizerJob(job_id=..., client=client)
        >>> job.fetch_status()
        >>> job.wait_for_completion()
        >>> job.fetch_summary()
        >>> df = job.fetch_data()
        >>> job.save_report("./evaluation_report.html")
        ```

        And in a jupyter notebook to display the report inline:
        ```python
        >>> job.display_report_in_notebook()
        ```
    """

    def __init__(self, job_id: str, client: NeMoMicroservices):
        """Initialize a SafeSynthesizerJob instance.

        Args:
            job_id: The id of the job to interact with.
            client: The NeMoMicroservices client to use to interact with the job.
        """
        self.job_id = job_id
        self._client = client

    def fetch_status(self) -> str:
        """Fetch the status of the job.

        Returns:
            The status of the job.
        """
        return self._client.beta.safe_synthesizer.jobs.get_status(self.job_id).status

    def wait_for_completion(self, poll_interval: int = 10, verbose: bool = True) -> None:
        """Block until the job is completed.

        Prints the logs by default

        Args:
            poll_interval: The interval in seconds to poll the job status.
            verbose: Gets logs and prints them at this interval. Default: True
        """
        log_msgs = set()
        while self.fetch_status() not in ["completed", "error", "cancelled"]:
            if verbose:
                logging_level = None
                try:
                    httpx_logger = logging.getLogger("httpx")
                    logging_level = httpx_logger.level
                    httpx_logger.setLevel("ERROR")
                    new_logs: list[PlatformJobLog] = list(log for log in self.fetch_logs())
                    for new_log in new_logs:
                        msg: str = new_log.message.strip()
                        if msg not in log_msgs:
                            print(msg)
                            log_msgs.add(msg)
                finally:
                    if logging_level:
                        logging.getLogger("httpx").setLevel(logging_level)
            time.sleep(poll_interval)
        print(f"Job ended with status: {self.fetch_status()}")

    def fetch_summary(self) -> SafeSynthesizerSummary:
        """Fetch the summary of the job.

        Returns:
            A summary of machine-readable metrics for a completed job. Raises a 404 error if the job is not finished.
        """
        return self._client.beta.safe_synthesizer.jobs.results.summary.download(self.job_id)

    def fetch_report(self) -> ReportHtml:
        """Fetch the evaluation report of the job as a string of html.

        Recommended to use save_report or display_report_in_notebook for most use cases.

        Returns:
            A string containing the html representation of the evaluation report.
        """
        response = self._client.beta.safe_synthesizer.jobs.results.evaluation_report.download(self.job_id)
        return ReportHtml(html=response.read().decode("utf-8"))

    def display_report_in_notebook(self, width="100%", height=1000) -> None:
        """Display the evaluation report in a jupyter notebook.

        Requires the IPython library to be installed.

        Args:
            width: The width of the iframe to display the report in.
            height: The height of the iframe to display the report in.
        """

        report = self.fetch_report()
        # Create a data URI from the report HTML
        report.display_report_in_notebook()

    def save_report(self, path: str | Path) -> None:
        """Save the evaluation report to a file.

        Args:
            path: The path to save the report to.
        """
        report = self.fetch_report()
        report.save(path)

    def fetch_data(self) -> pd.DataFrame:
        """Fetch the synthetic data of the job as a pandas DataFrame.

        Returns:
            A pandas DataFrame containing the synthetic data.
        """
        response = self._client.beta.safe_synthesizer.jobs.results.synthetic_data.download(self.job_id)
        return pd.read_csv(BytesIO(response.read()))

    def fetch_logs(self) -> Iterator[PlatformJobLog]:
        """Fetch the logs of the job as an iterator over log objects.

        Recommended to use print_logs for human-readable output. This method returns an iterator
        overlog objects and is useful for programmatic access.

        Returns:
            A generator for the log objects.
        """
        page_cursor = None
        while True:
            response = self._client.beta.safe_synthesizer.jobs.get_logs(self.job_id, page_cursor=page_cursor)
            yield from response.data
            if response.next_page is None:
                break
            page_cursor = response.next_page

    def print_logs(self) -> None:
        """Print the logs of the job to stdout."""
        for log in self.fetch_logs():
            print(log.message.strip())
