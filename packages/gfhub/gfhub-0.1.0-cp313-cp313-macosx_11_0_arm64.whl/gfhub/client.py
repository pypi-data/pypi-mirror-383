"""DataLab Python SDK.

A Python client for interacting with the DataLab API.
"""

from __future__ import annotations

import io
import json
import time
from collections import deque
from itertools import batched
from pathlib import Path
from typing import BinaryIO, Iterable
from urllib.parse import urljoin

import pandas as pd
from tenacity import Retrying, stop_after_attempt, wait_exponential
from tqdm.auto import tqdm

from .gfhub import Client as _RustClient
from .entry import Entries

__all__ = ["Client"]


class Client:
    """DataLab client for managing files, functions, pipelines, and tags.

    Args:
        base_url: The base URL of the DataLab server (e.g., "http://localhost:8080").
    """

    def __init__(self, base_url: str = "http://localhost:8080") -> None:
        """Initialize the DataLab client.

        Args:
            base_url: The base URL of the DataLab server.
        """
        self._base_url, *ports = base_url.rsplit(":", 1)
        self._port = None if not ports else int(ports[0])
        self._client = _RustClient(base_url)

    @property
    def base_url(self) -> str:
        """Get the base URL of the DataLab server."""
        if self._port is not None:
            return f"{self._base_url}:{self._port}"
        return self._base_url

    def url(self, *parts: str) -> str:
        """Get the full URL for a given path."""
        views = ["files", "functions", "pipelines", "tags", "jobs"]
        if (port := self._port) == 8080:
            port = 3000 if parts[0] in views else port
        base_url = self._base_url if port is None else f"{self._base_url}:{port}"
        return urljoin(base_url, "/".join(parts))

    def add_file(
        self,
        data: str | Path | BinaryIO | pd.DataFrame,
        tags: Iterable[str] = (),
        *,
        filename: str | None = None,
        trigger_pipelines: bool = True,
    ) -> dict:
        """Upload a file to DataLab.

        Args:
            data: The data to upload. Can be:
                - str/Path: Path to a file to upload
                - BinaryIO: File-like object (e.g., io.BytesIO)
                - pandas.DataFrame: Will be converted to Parquet format
            tags: Optional list of tags to apply to the file. Tags can be simple names
                (e.g., "raw") or parameter tags with "key:value" format (e.g., "raw:3").
            filename: Optional filename to use on the server. Required when uploading
                from BinaryIO or DataFrame. Optional when uploading from a path
                (defaults to the actual filename).
            trigger_pipelines: Whether to automatically trigger matching pipelines.
                Defaults to True.

        Returns:
            Dictionary containing the upload response with file metadata.

        Raises:
            RuntimeError: If the file upload fails.
            ValueError: If filename is not provided when uploading
                from BinaryIO or DataFrame.

        """
        tags_lst = None if not tags else [str(t) for t in tags]

        # Handle different input types
        if isinstance(data, (str, Path)):
            # Upload from file path
            path_obj = Path(data).resolve()
            if not path_obj.exists():
                msg = f"File not found: {path_obj}"
                raise FileNotFoundError(msg)

            if filename is not None:
                # Custom filename provided - read file and upload as bytes
                file_bytes = path_obj.read_bytes()
                mime_type = None  # Let server guess from filename
                return json.loads(
                    self._client.add_file_from_bytes(
                        file_bytes,
                        filename,
                        mime_type,
                        tags_lst,
                        bool(trigger_pipelines),
                    )
                )
            # Use original filename
            path_str = str(path_obj)
            return json.loads(
                self._client.add_file(path_str, tags_lst, bool(trigger_pipelines))
            )

        # Handle pandas DataFrame
        if isinstance(data, pd.DataFrame):
            if filename is None:
                msg = "filename parameter is required when uploading a DataFrame"
                raise ValueError(msg)
            # Convert DataFrame to Parquet bytes
            buffer = io.BytesIO()
            data.to_parquet(buffer, index=False)
            buffer.seek(0)
            file_bytes = buffer.read()
            mime_type = "application/octet-stream"

            # Ensure filename has .parquet extension
            if not filename.endswith(".parquet"):
                filename = f"{filename}.parquet"

            return json.loads(
                self._client.add_file_from_bytes(
                    file_bytes,
                    filename,
                    mime_type,
                    tags_lst,
                    bool(trigger_pipelines),
                )
            )

        # Handle BinaryIO (file-like object)
        if hasattr(data, "read"):
            if filename is None:
                msg = "filename parameter is required when uploading a buffer"
                raise ValueError(msg)
            file_bytes = data.read()
            if isinstance(file_bytes, str):
                file_bytes = file_bytes.encode("utf-8")
            mime_type = None  # Let server guess from filename
            return json.loads(
                self._client.add_file_from_bytes(
                    file_bytes,
                    filename,
                    mime_type,
                    tags_lst,
                    bool(trigger_pipelines),
                )
            )

        msg = f"Unsupported data type: {type(data)}"
        raise TypeError(msg)

    def add_function(
        self,
        name: str,
        script: Path | str,
        *,
        update: bool = True,
    ) -> dict:
        """Add or update a Python function.

        Args:
            name: Name of the function.
            script: Either the Python script content (if it contains newlines)
                or a path to a Python script file. The function must have a valid
                signature with `main(path: Path, /, *, kwargs) -> Path`.
            update: If True, updates the function if it already exists. If False,
                raises an error on conflict. Defaults to True.

        Returns:
            Dictionary containing the function response with metadata.

        Raises:
            RuntimeError: If the function validation or upload fails.
        """
        script_or_path = str(script.resolve()) if isinstance(script, Path) else script
        if "\n" not in script_or_path:
            script_or_path = str(Path(script_or_path).resolve())
        return json.loads(
            self._client.add_function(str(name), script_or_path, bool(update))
        )

    def add_pipeline(
        self,
        name: str,
        schema: dict,
        *,
        update: bool = True,
    ) -> dict:
        """Add or update a pipeline.

        Args:
            name: Name of the pipeline.
            schema: JSON string containing the pipeline schema with this structure:
                - steps: Dict mapping step names to step definitions
                - connections: List of connections between steps
                - input_tags: Dict mapping input ports to required tags
                - output_tags: Dict mapping output ports to applied tags
                - enabled: Whether the pipeline is enabled (default: False)
            update: If True, updates the pipeline if it already exists. If False,
                raises an error on conflict. Defaults to True.

        Returns:
            Dictionary containing the pipeline response with metadata.

        Raises:
            RuntimeError: If the pipeline creation or update fails.

        Example:
            >>> schema = {
            ...     "steps": {"csv2parquet": {"function": "csv2parquet"}},
            ...     "connections": [],
            ...     "input_tags": {"csv2parquet,0": [".csv"]},
            ...     "output_tags": {"csv2parquet,0": [".parquet"]},
            ...     "enabled": False,
            ... }
            >>> client.add_pipeline("csv_converter", schema)
            >>>
            >>> # Tags can include parameter values using "tag:value" format
            >>> schema_with_params = {
            ...     "steps": {"process": {"function": "process_data"}},
            ...     "connections": [],
            ...     "input_tags": {"process,0": ["wafer_id:wafer1", ".parquet"]},
            ...     "output_tags": {"process,0": ["status:processed", "view"]},
            ...     "enabled": True,
            ... }
            >>> client.add_pipeline("process_wafer1", schema_with_params)
        """
        if "steps" not in schema:
            schema["steps"] = {}

        # be a bit more lenient with the schema
        if isinstance(schema["steps"], list):
            schema["steps"] = {
                f"step{i}": step for i, step in enumerate(schema["steps"])
            }
        for step_name in list(schema["steps"]):
            if isinstance(schema["steps"][step_name], str):
                schema["steps"][step_name] = {
                    "function": schema["steps"][step_name],
                    "settings": {},
                }

        return json.loads(
            self._client.add_pipeline(str(name), json.dumps(schema), bool(update))
        )

    def add_tag(
        self,
        name: str,
        color: str,
        *,
        update: bool = True,
    ) -> dict:
        """Add or update a tag.

        Args:
            name: Name of the tag.
            color: Hex color code for the tag (e.g., "#ef4444").
            update: If True, updates the tag if it already exists. If False,
                raises an error on conflict. Defaults to True.

        Returns:
            Dictionary containing the tag response with metadata.

        Raises:
            RuntimeError: If the tag creation or update fails.
        """
        return json.loads(self._client.add_tag(str(name), str(color), bool(update)))

    def query_files(
        self,
        *,
        name: str | None = None,
        tags: Iterable[str] = (),
    ) -> Entries:
        """Query files by name pattern and/or tags.

        Args:
            name: Optional filename pattern to filter by. Supports glob patterns:
                - Exact match: "lattice.gds" (case-insensitive)
                - Glob pattern: "*.csv", "data*.parquet", "lattice*"
            tags: Optional list of tags to filter by. Files must have ALL given tags.
                Supports wildcards (e.g., "wafer_id:*") to match any parameter value.

        Returns:
            Dictionary containing a list of matching files with their metadata.

        Raises:
            RuntimeError: If the query fails.

        Example:
            >>> # Find all CSV files by extension tag
            >>> client.query_files(tags=[".csv"])
            >>>
            >>> # Find files by exact name (case-insensitive)
            >>> client.query_files(name="lattice.gds")
            >>>
            >>> # Find files by glob pattern
            >>> client.query_files(name="*.csv")
            >>> client.query_files(name="data*.parquet")
            >>>
            >>> # Find files with specific parameter values
            >>> client.query_files(tags=["wafer_id:wafer1", ".parquet"])
            >>>
            >>> # Combine name pattern and tags
            >>> client.query_files(name="*.parquet", tags=["wafer_id:*"])
            >>>
            >>> # Get all files
            >>> client.query_files()
        """
        tags_list = None if not tags else [str(t) for t in tags]
        entries = Entries(json.loads(self._client.query_files(name, tags_list)))
        for entry in entries:
            if "tags" not in entry:
                entry["tags"] = {}
            else:
                # entry names are unique, so this is more convenient:
                entry["tags"] = {t["name"]: t for t in entry["tags"]}
        return entries

    def add_cascaded_pipeline(
        self,
        name: str,
        steps: Iterable[str | dict] = (),
        input_tags: Iterable[str] = (),
        output_tags: Iterable[str] = (),
        *,
        update: bool = True,
        enabled: bool = False,
    ) -> dict:
        """Create a cascaded pipeline where functions are chained sequentially.

        The first output of each function flows into the first input of the next.
        Input tags are applied to the first input of the first function.
        Output tags are applied to the first output of the last function.

        Args:
            name: Name of the pipeline.
            steps: Variable number of functions to chain together. Each can be:
                - A string: function name (no parameters)
                - A dict: {"function": "name", "settings": {"param": value}}
            input_tags: Tags to apply to the first input of the first function.
                Can include parameter values using "tag:value" format.
                Defaults to empty tuple.
            output_tags: Tags to apply to the first output of the last function.
                Can include parameter values using "tag:value" format.
                Defaults to empty tuple.
            update: If True, updates the pipeline if it already exists. If False,
                raises an error on conflict. Defaults to True.
            enabled: Whether the pipeline is enabled. Defaults to False.

        Returns:
            Dictionary containing the pipeline response with metadata.

        Raises:
            RuntimeError: If the pipeline creation or update fails.
            ValueError: If less than one function is provided.

        """
        functions = list(steps)
        if len(functions) < 1:
            msg = "At least one function must be provided"
            raise ValueError(msg)

        # Build steps
        steps = {}
        for i, func in enumerate(functions):
            step_name = f"step{i}"
            if isinstance(func, str):
                steps[step_name] = {"function": func, "settings": {}}
            elif isinstance(func, dict):
                steps[step_name] = {
                    "function": func.get("function", ""),
                    "settings": func.get("settings", {}),
                }
            else:
                msg = f"Function at position {i} must be a string or dict"
                raise TypeError(msg)

        # Build connections (chain steps together)
        connections = [
            {"from": f"step{i},0", "to": f"step{i + 1},0"}
            for i in range(len(functions) - 1)
        ]

        # Build input_tags (first input of first function)
        input_tags_dict = {}
        if input_tags:
            input_tags_dict["step0,0"] = list(input_tags)

        # Build output_tags (first output of last function)
        output_tags_dict = {}
        if output_tags:
            last_step = f"step{len(functions) - 1}"
            output_tags_dict[f"{last_step},0"] = list(output_tags)

        # Create schema
        schema = {
            "steps": steps,
            "connections": connections,
            "input_tags": input_tags_dict,
            "output_tags": output_tags_dict,
            "enabled": enabled,
        }

        return self.add_pipeline(name, schema, update=update)

    def download_file(
        self,
        upload_id: str,
        output: str | Path | BinaryIO | None = None,
    ) -> io.BytesIO | None:
        """Download a file by upload ID.

        Args:
            upload_id: ID of the file to download.
            output: Where to write the file. Can be:
                - str/Path: File path to write to
                - File handle opened in binary mode (e.g., open('file', 'wb'))
                - io.BytesIO: BytesIO buffer to write to
                - None: Return new BytesIO buffer with file contents

        Returns:
            None if output is a path or file handle, io.BytesIO if output is None.

        Raises:
            RuntimeError: If the download fails.

        Example:
            >>> # Download to file path
            >>> client.download_file("upload_123", "downloaded_file.csv")
            >>>
            >>> # Download to file handle
            >>> with open("output.csv", "wb") as f:
            ...     client.download_file("upload_123", f)
            >>>
            >>> # Download to BytesIO
            >>> import io
            >>> buffer = io.BytesIO()
            >>> client.download_file("upload_123", buffer)
            >>> buffer.seek(0)
            >>>
            >>> # Get BytesIO directly
            >>> buffer = client.download_file("upload_123")
            >>> data = buffer.read()
        """
        file_bytes = bytes(self._client.download_file_bytes(str(upload_id)))

        if output is None:
            return io.BytesIO(file_bytes)
        if isinstance(output, (str, Path)):
            output_path = Path(output).resolve()
            with output_path.open("wb") as f:
                f.write(file_bytes)
            return None

        # File handle or BytesIO
        output.write(file_bytes)
        return None

    def trigger_pipeline(
        self,
        pipeline_name: str,
        upload_ids: str | Iterable[str],
    ) -> dict:
        """Trigger a pipeline manually with one or more files.

        Args:
            pipeline_name: Name of the pipeline to trigger.
            upload_ids: Single upload id or list of upload IDs to process.

        Returns:
            Dictionary containing the job metadata with job ID.

        Raises:
            RuntimeError: If the pipeline trigger fails or pipeline not found.

        Example:
            >>> # Trigger with single file
            >>> job = client.trigger_pipeline("csv2json", "upload_123")
            >>> print(job["id"])  # Job ID
            >>>
            >>> # Trigger with multiple files
            >>> job = client.trigger_pipeline("csv2json", ["upload_1", "upload_2"])
            >>> print(job["id"])  # Job ID
        """
        if isinstance(upload_ids, str):
            upload_ids = [upload_ids]
        return json.loads(
            self._client.trigger_pipeline(str(pipeline_name), list(upload_ids))
        )

    def get_job(self, job_id: str) -> dict:
        """Get job details by ID.

        Args:
            job_id: The job ID to retrieve

        Returns:
            Job details including status, inputs, outputs, timestamps, etc.

        Example:
            >>> job = client.get_job("job_123")
            >>> print(job["status"])  # QUEUED, RUNNING, SUCCESS, or FAILED
            >>> print(job["pipeline_name"])  # Name of the pipeline
        """
        return json.loads(self._client.get_job(str(job_id)))

    def wait_for_job(
        self,
        job_id: str,
        poll_interval: float = 1.0,
    ) -> dict:
        """Wait for a job to complete (SUCCESS or FAILED status).

        Args:
            job_id: The job ID to wait for
            timeout: Maximum seconds to wait (default: 300)
            poll_interval: Seconds between polls (default: 1.0)

        Returns:
            Final job details with status SUCCESS or FAILED

        Raises:
            RuntimeError: If job is not found

        Example:
            >>> job = client.trigger_pipeline("csv2json", "upload_123")
            >>> final_job = client.wait_for_job(job["id"])
            >>> print(final_job["status"])  # SUCCESS or FAILED
            >>> if final_job["status"] == "SUCCESS":
            >>>     print(final_job["output_filenames"])
        """
        while True:
            job = self.get_job(job_id)
            status = job["status"]
            if status in ("SUCCESS", "FAILED"):
                return job
            time.sleep(poll_interval)

    def wait_for_jobs(
        self, job_ids: list[str], poll_interval: float = 1.0
    ) -> list[dict]:
        """Wait for multiple jobs to complete.

        Args:
            job_ids: List of job IDs to wait for
            poll_interval: Seconds between polling cycles (default: 1.0)

        Returns:
            List of final job details with status SUCCESS or FAILED

        Raises:
            RuntimeError: If any job is not found

        Example:
            >>> jobs = client.wait_for_jobs(["job_123", "job_456"])
            >>> for job in jobs:
            >>>     print(job["status"])  # SUCCESS or FAILED
        """
        completed = {}
        remaining = set(job_ids)

        with tqdm(total=len(job_ids)) as pbar:
            while remaining:
                # Check all remaining jobs in one cycle
                for job_id in list(remaining):
                    job = self.get_job(job_id)
                    status = job["status"]
                    if status in ("SUCCESS", "FAILED"):
                        completed[job_id] = job
                        remaining.remove(job_id)
                        pbar.update(1)

                # Sleep once per cycle, not per job
                if remaining:
                    time.sleep(poll_interval)

        # Return in original order
        return [completed[job_id] for job_id in job_ids]
