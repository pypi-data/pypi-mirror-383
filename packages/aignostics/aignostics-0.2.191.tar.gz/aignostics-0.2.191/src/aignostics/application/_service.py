"""Service of the application module."""

import base64
import re
import time
from collections.abc import Callable, Generator
from enum import StrEnum
from http import HTTPStatus
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import google_crc32c
import requests
import semver
from pydantic import BaseModel, computed_field

from aignostics.bucket import Service as BucketService
from aignostics.constants import WSI_SUPPORTED_FILE_EXTENSIONS
from aignostics.platform import (
    LIST_APPLICATION_RUNS_MAX_PAGE_SIZE,
    ApiException,
    Application,
    ApplicationRun,
    ApplicationRunData,
    ApplicationRunStatus,
    ApplicationVersion,
    Client,
    InputArtifact,
    InputItem,
    ItemResult,
    ItemStatus,
    NotFoundException,
    OutputArtifactElement,
)
from aignostics.platform import (
    Service as PlatformService,
)
from aignostics.utils import BaseService, Health, get_logger, sanitize_path_component
from aignostics.wsi import Service as WSIService

from ._settings import Settings
from ._utils import get_file_extension_for_artifact, get_mime_type_for_artifact

has_qupath_extra = find_spec("ijson")
if has_qupath_extra:
    from aignostics.qupath import AddProgress as QuPathAddProgress
    from aignostics.qupath import AnnotateProgress as QuPathAnnotateProgress
    from aignostics.qupath import Service as QuPathService


logger = get_logger(__name__)

APPLICATION_RUN_DOWNLOAD_SLEEP_SECONDS = 5
APPLICATION_RUN_FILE_READ_CHUNK_SIZE = 1024 * 1024 * 1024  # 1GB
APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB
APPLICATION_RUN_UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB


class DownloadProgressState(StrEnum):
    """Enum for download progress states."""

    INITIALIZING = "Initializing ..."
    QUPATH_ADD_INPUT = "Adding input slides to QuPath project ..."
    CHECKING = "Checking run status ..."
    WAITING = "Waiting for item completing ..."
    DOWNLOADING = "Downloading artifact ..."
    QUPATH_ADD_RESULTS = "Adding result images to QuPath project ..."
    QUPATH_ANNOTATE_INPUT_WITH_RESULTS = "Annotating input slides in QuPath project with results ..."
    COMPLETED = "Completed."


class DownloadProgress(BaseModel):
    status: DownloadProgressState = DownloadProgressState.INITIALIZING
    run: ApplicationRunData | None = None
    item: ItemResult | None = None
    item_count: int | None = None
    item_index: int | None = None
    item_reference: str | None = None
    artifact: OutputArtifactElement | None = None
    artifact_count: int | None = None
    artifact_index: int | None = None
    artifact_path: Path | None = None
    artifact_download_url: str | None = None
    artifact_size: int | None = None
    artifact_downloaded_chunk_size: int = 0
    artifact_downloaded_size: int = 0
    if has_qupath_extra:
        qupath_add_input_progress: QuPathAddProgress | None = None
        qupath_add_results_progress: QuPathAddProgress | None = None
        qupath_annotate_input_with_results_progress: QuPathAnnotateProgress | None = None

    @computed_field  # type: ignore
    @property
    def total_artifact_count(self) -> int | None:
        if self.item_count and self.artifact_count:
            return self.item_count * self.artifact_count
        return None

    @computed_field  # type: ignore
    @property
    def total_artifact_index(self) -> int | None:
        if self.item_count and self.artifact_count and self.item_index is not None and self.artifact_index is not None:
            return self.item_index * self.artifact_count + self.artifact_index
        return None

    @computed_field  # type: ignore
    @property
    def item_progress_normalized(self) -> float:  # noqa: PLR0911
        """Compute normalized item progress in range 0..1.

        Returns:
            float: The normalized item progress in range 0..1.
        """
        if self.status == DownloadProgressState.DOWNLOADING:
            if (not self.total_artifact_count) or self.total_artifact_index is None:
                return 0.0
            return min(1, float(self.total_artifact_index + 1) / float(self.total_artifact_count))
        if has_qupath_extra:
            if self.status == DownloadProgressState.QUPATH_ADD_INPUT and self.qupath_add_input_progress:
                return self.qupath_add_input_progress.progress_normalized
            if self.status == DownloadProgressState.QUPATH_ADD_RESULTS and self.qupath_add_results_progress:
                return self.qupath_add_results_progress.progress_normalized
            if self.status == DownloadProgressState.QUPATH_ANNOTATE_INPUT_WITH_RESULTS:
                if (not self.item_count) or (not self.item_index):
                    return 0.0
                return min(1, float(self.item_index + 1) / float(self.item_count))
        return 0.0

    @computed_field  # type: ignore
    @property
    def artifact_progress_normalized(self) -> float:
        """Compute normalized artifact progress in range 0..1.

        Returns:
            float: The normalized artifact progress in range 0..1.
        """
        if self.status == DownloadProgressState.DOWNLOADING:
            if not self.artifact_size:
                return 0.0
            return min(1, float(self.artifact_downloaded_size) / float(self.artifact_size))
        if (
            has_qupath_extra
            and self.status == DownloadProgressState.QUPATH_ANNOTATE_INPUT_WITH_RESULTS
            and self.qupath_annotate_input_with_results_progress
        ):
            return self.qupath_annotate_input_with_results_progress.progress_normalized
        return 0.0


class Service(BaseService):
    """Service of the application module."""

    _settings: Settings
    _client: Client | None = None
    _platform_service: PlatformService | None = None

    def __init__(self) -> None:
        """Initialize service."""
        super().__init__(Settings)  # automatically loads and validates the settings

    def info(self, mask_secrets: bool = True) -> dict[str, Any]:  # noqa: ARG002, PLR6301
        """Determine info of this service.

        Args:
            mask_secrets (bool): If True, mask sensitive information in the output.

        Returns:
            dict[str,Any]: The info of this service.
        """
        return {}

    def health(self) -> Health:  # noqa: PLR6301
        """Determine health of this service.

        Returns:
            Health: The health of the service.
        """
        return Health(
            status=Health.Code.UP,
        )

    def _get_platform_client(self) -> Client:
        """Get the platform client.

        Returns:
            Client: The platform client.

        Raises:
            Exception: If the client cannot be created.
        """
        if self._client is None:
            logger.debug("Creating platform client.")
            self._client = Client()
        else:
            logger.debug("Reusing platform client.")
        return self._client

    def _get_platform_service(self) -> PlatformService:
        """Get the platform service.

        Returns:
            PlatformService: The platform service.

        Raises:
            Exception: If the client cannot be created.
        """
        if self._platform_service is None:
            logger.debug("Creating platform service.")
            self._platform_service = PlatformService()
        else:
            logger.debug("Reusing platform service.")
        return self._platform_service

    @staticmethod
    def applications_static() -> list[Application]:
        """Get a list of all applications, static variant.

        Returns:
            list[str]: A list of all applications.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application list cannot be retrieved.
        """
        return Service().applications()

    def applications(self) -> list[Application]:
        """Get a list of all applications.

        Returns:
            list[str]: A list of all applications.

        Raises:
            Exception: If the client cannot be created.

        Raises:
            Exception: If the application list cannot be retrieved.
        """
        return [
            app
            for app in list(self._get_platform_client().applications.list())
            if app.application_id not in {"h-e-tme", "two-task-dummy"}
        ]

    def application(self, application_id: str) -> Application:
        """Get a specific application.

        Args:
            application_id (str): The ID of the application.

        Returns:
            Application: The application or None if not found.

        Raises:
            NotFoundException: If the application with the given ID is not found.
            RuntimeError: If the application cannot be retrieved unexpectedly.
        """
        try:
            return self._get_platform_client().application(application_id)
        except NotFoundException as e:
            message = f"Application with ID '{application_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except Exception as e:
            message = f"Failed to retrieve application with ID '{application_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_version(
        self, application_version_id: str, use_latest_if_no_version_given: bool = False
    ) -> ApplicationVersion:
        """Get a specific application version.

        Args:
            application_version_id (str): The ID of the application version
            use_latest_if_no_version_given (bool): If True, use the latest version if no specific version is given.

        Returns:
            ApplicationVersion: The application version

        Raises:
            ValueError: If the application version ID is invalid.
            NotFoundException: If the application with the given ID is not found.
            RuntimeError: If the application cannot be retrieved unexpectedly.
        """
        # Validate format: application_id:vX.Y.Z (where X.Y.Z is a semver)
        # This checks for proper format like "he-tme:v0.50.0" where "he-tme" is the application id
        # and "v0.50.0" is the version with proper semver format
        match = re.match(r"^([^:]+):v(.+)$", application_version_id)
        if not match or not semver.Version.is_valid(match.group(2)):
            if use_latest_if_no_version_given:
                application_id = match.group(1) if match else application_version_id
                latest_version = self.application_version_latest(self.application(application_id))
                if latest_version:
                    return latest_version
                message = (
                    f"No valid application version found for '{application_version_id}'no latest version available."
                )
                logger.warning(message)
                raise ValueError(message)
            message = f"Invalid application version id format: {application_version_id}. "
            message += "Expected format: application_id:vX.Y.Z"
            raise ValueError(message)

        application_id = match.group(1)
        application = self.application(application_id)
        for version in self.application_versions(application):
            if version.application_version_id == application_version_id:
                return version
        message = f"Application version with ID {application_version_id} not found in application {application_id}"
        raise NotFoundException(message)

    def application_versions(self, application: Application) -> list[ApplicationVersion]:
        """Get a list of all versions of the given application.

        Args:
            application (Application): The application to check for versions.

        Returns:
            list[ApplicationVersion]: A list of all application versions sorted by semantic versioning (latest first).

        Raises:
            RuntimeError: If version list cannot be retrieved unexpectedly.
        """
        try:
            return self._get_platform_client().applications.versions.list_sorted(application=application)
        except Exception as e:
            message = f"Failed to retrieve application versions for application '{application.application_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_version_latest(self, application: Application) -> ApplicationVersion | None:
        """Get a latest application version.

        Args:
            application (Application): The application to check for versions.

        Returns:
            ApplicationVersion | None: A list of all application versions.

        Raises:
            NotFoundException: If the application with the given ID is not found.
            RuntimeError: If version list cannot be retrieved unexpectedly.
        """
        versions = self.application_versions(application)
        return versions[0] if versions else None

    @staticmethod
    def _process_key_value_pair(entry: dict[str, Any], key_value: str, reference: str) -> None:
        """Process a single key-value pair from a mapping.

        Args:
            entry: The entry dictionary to update
            key_value: String in the format "key=value"
            reference: The reference value for logging
        """
        key, value = key_value.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            return

        if key not in entry:
            logger.warning("key '%s' not found in entry, ignoring mapping for '%s'", key, reference)
            return

        logger.debug("Updating key '%s' with value '%s' for reference '%s'.", key, value, reference)
        entry[key.strip()] = value.strip()

    @staticmethod
    def _apply_mappings_to_entry(entry: dict[str, Any], mappings: list[str]) -> None:
        """Apply key/value mappings to an entry.

        If the reference attribute of the entry matches the regex pattern in the mapping,
            the key/value pairs are applied.

        Args:
            entry: The entry dictionary to update with mapped values
            mappings: List of strings with format 'regex:key=value,...'
                where regex ismatched against the reference attribute in the entry
        """
        reference = entry["reference"]
        for mapping in mappings:
            parts = mapping.split(":", 1)
            if len(parts) != 2:  # noqa: PLR2004
                continue

            pattern = parts[0].strip()
            if not re.search(pattern, reference):
                continue

            key_value_pairs = parts[1].split(",")
            for key_value in key_value_pairs:
                Service._process_key_value_pair(entry, key_value, reference)

    @staticmethod
    def generate_metadata_from_source_directory(
        application_version_id: str,
        source_directory: Path,
        with_gui_metadata: bool = False,
        mappings: list[str] | None = None,
        with_extra_metadata: bool = False,
    ) -> list[dict[str, Any]]:
        """Generate metadata from the source directory.

        Steps:
        1. Recursively files ending with supported extensions in the source directory
        2. Creates a dict with the following columns
            - reference (str): The reference of the file, by default equivalent to the absolute file name
            - source (str): The absolute filename
            - checksum_base64_crc32c (str): The CRC32C checksum of the file constructed, base64 encoded
            - resolution_mpp (float): The microns per pixel, inspecting the base layer
            - height_px: The height of the image in pixels, inspecting the base layer
            - width_px: The width of the image in pixels, inspecting the base layer
            - Further attributes depending on the application and it's version
        3. Applies the optional mappings to fill in additional metadata fields in the dict.

        Args:
            application_version_id (str): The ID of the application version.
                If application id is given, the latest version of that application is used.
            source_directory (Path): The source directory to generate metadata from.
            with_gui_metadata (bool): If True, include additional metadata for GUI.
            mappings (list[str]): Mappings of the form '<regexp>:<key>:<value>,<key>:<value>,...'.
                The regular expression is matched against the reference attribute of the entry.
                The key/value pairs are applied to the entry if the pattern matches.
            with_extra_metadata (bool): If True, include extra metadata from the WSIService.

        Returns:
            dict[str, Any]: The generated metadata.

        Raises:
            Exception: If the metadata cannot be generated.

        Raises:
            NotFoundError: If the application version with the given ID is not found.
            ValueError: If the source directory does not exist or is not a directory.
            RuntimeError: If the metadata generation fails unexpectedly.
        """
        logger.debug("Generating metadata from source directory: %s", source_directory)

        # TODO(Helmut): Use it
        _ = Service().application_version(application_version_id, use_latest_if_no_version_given=True)

        metadata = []

        try:
            for extension in list(WSI_SUPPORTED_FILE_EXTENSIONS):
                for file_path in source_directory.glob(f"**/*{extension}"):
                    # Generate CRC32C checksum with google_crc32c and encode as base64
                    hash_sum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]
                    with file_path.open("rb") as f:
                        while chunk := f.read(1024):
                            hash_sum.update(chunk)  # type: ignore[no-untyped-call]
                    checksum = str(base64.b64encode(hash_sum.digest()), "UTF-8")  # type: ignore[no-untyped-call]
                    try:
                        image_metadata = WSIService().get_metadata(file_path)
                        width = image_metadata["dimensions"]["width"]
                        height = image_metadata["dimensions"]["height"]
                        mpp = image_metadata["resolution"]["mpp_x"]
                        file_size_human = image_metadata["file"]["size_human"]
                        reference = file_path.absolute()
                        entry = {
                            "reference": str(reference),
                            "reference_short": str(reference.name),
                            "source": str(file_path),
                            "checksum_base64_crc32c": checksum,
                            "resolution_mpp": mpp,
                            "width_px": width,
                            "height_px": height,
                            "staining_method": None,
                            "tissue": None,
                            "disease": None,
                            "file_size_human": file_size_human,
                            "file_upload_progress": 0.0,
                            "platform_bucket_url": None,
                        }
                        if with_extra_metadata:
                            entry["extra"] = image_metadata.get("extra", {})

                        if not with_gui_metadata:
                            entry.pop("reference_short", None)
                            entry.pop("source", None)
                            entry.pop("file_size_human", None)
                            entry.pop("file_upload_progress", None)

                        if mappings:
                            Service._apply_mappings_to_entry(entry, mappings)

                        metadata.append(entry)
                    except Exception as e:  # noqa: BLE001
                        message = f"Failed to process file '{file_path}': {e}"
                        logger.warning(message)
                        continue

            logger.debug("Generated metadata for %d files", len(metadata))
            return metadata

        except Exception as e:
            message = f"Failed to generate metadata from source directory '{source_directory}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def application_run_upload(  # noqa: PLR0913, PLR0917
        application_version_id: str,
        metadata: list[dict[str, Any]],
        onboard_to_aignostics_portal: bool = False,
        upload_prefix: str = str(time.time() * 1000),
        upload_progress_queue: Any | None = None,  # noqa: ANN401
        upload_progress_callable: Callable[[int, Path, str], None] | None = None,
    ) -> bool:
        """Upload files with a progress queue.

        Args:
            application_version_id (str): The ID of the application version.
                If application id is given, the latest version of that application is used.
            metadata (list[dict[str, Any]]): The metadata to upload.
            onboard_to_aignostics_portal (bool): True if the run should be onboarded to the Aignostics Portal.
            upload_prefix (str): The prefix for the upload, defaults to current milliseconds.
            upload_progress_queue (Queue | None): The queue to send progress updates to.
            upload_progress_callable (Callable[[int, Path, str], None] | None): The task to update for progress updates.

        Returns:
            bool: True if the upload was successful, False otherwise.

        Raises:
            NotFoundException: If the application version with the given ID is not found.
            RuntimeError: If fetching the application version fails unexpectedly.
            requests.HTTPError: If the upload fails with an HTTP error.
        """
        import psutil  # noqa: PLC0415

        logger.debug("Uploading files with upload ID '%s'", upload_prefix)
        application_version = Service().application_version(application_version_id, use_latest_if_no_version_given=True)
        for row in metadata:
            reference = row["reference"]
            source_file_path = Path(row["reference"])
            if not source_file_path.is_file():
                logger.warning("Source file '%s' does not exist.", row["reference"])
                return False
            username = psutil.Process().username().replace("\\", "_")
            object_key = (
                f"{username}/{upload_prefix}/{application_version.application_version_id}/{source_file_path.name}"
            )
            if onboard_to_aignostics_portal:
                object_key = f"onboard/{object_key}"
            platform_bucket_url = (
                f"{BucketService().get_bucket_protocol()}://{BucketService().get_bucket_name()}/{object_key}"
            )
            signed_upload_url = BucketService().create_signed_upload_url(object_key)
            logger.debug("Generated signed upload URL '%s' for object '%s'", signed_upload_url, platform_bucket_url)
            if upload_progress_queue:
                upload_progress_queue.put_nowait({
                    "reference": reference,
                    "platform_bucket_url": platform_bucket_url,
                })
            file_size = source_file_path.stat().st_size
            logger.debug(
                "Uploading file '%s' with size %d bytes to '%s' via '%s'",
                source_file_path,
                file_size,
                platform_bucket_url,
                signed_upload_url,
            )
            with (
                open(source_file_path, "rb") as f,
            ):

                def read_in_chunks(  # noqa: PLR0913, PLR0917
                    reference: str,
                    file_size: int,
                    upload_progress_queue: Any | None = None,  # noqa: ANN401
                    upload_progress_callable: Callable[[int, Path, str], None] | None = None,
                    file_path: Path = source_file_path,
                    platform_bucket_url: str = platform_bucket_url,
                ) -> Generator[bytes, None, None]:
                    while True:
                        chunk = f.read(APPLICATION_RUN_UPLOAD_CHUNK_SIZE)
                        if not chunk:
                            break
                        if upload_progress_queue:
                            upload_progress_queue.put_nowait({
                                "reference": reference,
                                "file_upload_progress": min(100.0, f.tell() / file_size),
                            })
                        if upload_progress_callable:
                            upload_progress_callable(len(chunk), file_path, platform_bucket_url)
                        yield chunk

                response = requests.put(
                    signed_upload_url,
                    data=read_in_chunks(reference, file_size, upload_progress_queue, upload_progress_callable),
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=60,
                )
                response.raise_for_status()
        logger.info("Upload completed successfully.")
        return True

    @staticmethod
    def application_runs_static(
        limit: int | None = None,
        completed_only: bool = False,
        note_regex: str | None = None,
        note_query_case_insensitive: bool = True,
    ) -> list[dict[str, Any]]:
        """Get a list of all application runs, static variant.

        Args:
            limit (int | None): The maximum number of runs to retrieve. If None, all runs are retrieved.
            completed_only (bool): If True, only completed runs are retrieved.
            note_regex (str | None): Optional regex to filter runs by note metadata. If None, no filtering is applied.
            note_query_case_insensitive (bool): If True, the note_regex is case insensitive. Default is True.

        Returns:
            list[ApplicationRunData]: A list of all application runs.

        Raises:
            RuntimeError: If the application run list cannot be retrieved.
        """
        return [
            {
                "application_run_id": run.application_run_id,
                "application_version_id": run.application_version_id,
                "triggered_at": run.triggered_at,
                "status": run.status,
            }
            for run in Service().application_runs(
                limit=limit,
                status=ApplicationRunStatus.COMPLETED if completed_only else None,
                note_regex=note_regex,
                note_query_case_insensitive=note_query_case_insensitive,
            )
        ]

    def application_runs(
        self,
        limit: int | None = None,
        status: ApplicationRunStatus | None = None,
        note_regex: str | None = None,
        note_query_case_insensitive: bool = True,
    ) -> list[ApplicationRunData]:
        """Get a list of all application runs.

        Args:
            limit (int | None): The maximum number of runs to retrieve. If None, all runs are retrieved.
            status (ApplicationRunStatus | None): Filter runs by status. If None, all runs are retrieved.
            note_regex (str | None): Optional regex to filter runs by note metadata. If None, no filtering is applied.
            note_query_case_insensitive (bool): If True, the note_regex is case insensitive. Default is True.

        Returns:
            list[ApplicationRunData]: A list of all application runs.

        Raises:
            RuntimeError: If the application run list cannot be retrieved.
        """
        if limit is not None and limit <= 0:
            return []
        runs = []
        page_size = LIST_APPLICATION_RUNS_MAX_PAGE_SIZE
        try:
            if note_regex:
                flag_case_insensitive = ' flag "i"' if note_query_case_insensitive else ""
                metadata = f'$.sdk.note ? (@ like_regex "{note_regex}"{flag_case_insensitive})'
            else:
                metadata = None

            run_iterator = self._get_platform_client().runs.list_data(
                sort="-triggered_at", page_size=page_size, metadata=metadata
            )
            for run in run_iterator:
                if status is not None and run.status != status:
                    continue
                runs.append(run)
                if limit is not None and len(runs) >= limit:
                    break
            return runs
        except Exception as e:
            message = f"Failed to retrieve application runs: {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_run(self, run_id: str) -> ApplicationRun:
        """Select a run by its ID.

        Args:
            run_id: The ID of the run to find

        Returns:
            ApplicationRun: The run that can be fetched using the .details() call.

        Raises:
            RuntimeError: If initializing the client fails or the run cannot be retrieved.
        """
        try:
            return self._get_platform_client().run(run_id)
        except Exception as e:
            message = f"Failed to retrieve application run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_run_submit_from_metadata(
        self,
        application_version_id: str,
        metadata: list[dict[str, Any]],
        custom_metadata: dict[str, Any] | None = None,
        onboard_to_aignostics_portal: bool = False,
    ) -> ApplicationRun:
        """Submit a run for the given application.

        Args:
            application_version_id: The ID of the application version to run.
                If application id is given, the latest version of that application is used.
            metadata: The metadata for the run.
            custom_metadata: Optional custom metadata to attach to the run.
            onboard_to_aignostics_portal: True if the run should be onboarded to the Aignostics Portal.

        Returns:
            ApplicationRun: The submitted run.

        Raises:
            NotFoundException: If the application version with the given ID is not found.
            ValueError: If platform bucket URL is missing or has unsupported protocol,
                or if the application version ID is invalid.
            RuntimeError: If submitting the run failed unexpectedly.
        """
        logger.debug("Submitting application run with metadata: %s", metadata)
        if onboard_to_aignostics_portal:
            custom_metadata = custom_metadata or {}
            custom_metadata.setdefault("sdk", {})
            custom_metadata["sdk"]["onboard_to_aignostics_portal"] = onboard_to_aignostics_portal
        application_version = self.application_version(application_version_id, use_latest_if_no_version_given=True)
        if len(application_version.input_artifacts) != 1:
            message = (
                f"Application version '{application_version_id}' has "
                f"{len(application_version.input_artifacts)} input artifacts, "
                "but only 1 is supported."
            )
            logger.warning(message)
            raise RuntimeError(message)
        input_artifact_name = application_version.input_artifacts[0].name

        items = []
        for row in metadata:
            platform_bucket_url = row["platform_bucket_url"]
            if platform_bucket_url and platform_bucket_url.startswith("gs://"):
                url_parts = platform_bucket_url[5:].split("/", 1)
                bucket_name = url_parts[0]
                object_key = url_parts[1]
                download_url = BucketService().create_signed_download_url(object_key, bucket_name)
            else:
                message = f"Invalid platform bucket URL: '{platform_bucket_url}'."
                logger.warning(message)
                raise ValueError(message)

            items.append(
                InputItem(
                    reference=row["reference"],
                    input_artifacts=[
                        InputArtifact(
                            name=input_artifact_name,
                            download_url=download_url,
                            metadata={
                                "checksum_base64_crc32c": row["checksum_base64_crc32c"],
                                "height_px": int(row["height_px"]),
                                "width_px": int(row["width_px"]),
                                "media_type": (
                                    "image/tiff"
                                    if row["reference"].lower().endswith((".tif", ".tiff"))
                                    else "application/dicom"
                                    if row["reference"].lower().endswith(".dcm")
                                    else "application/octet-stream"
                                ),
                                "resolution_mpp": float(row["resolution_mpp"]),
                                "specimen": {
                                    "disease": row["disease"],
                                    "tissue": row["tissue"],
                                },
                                "staining_method": row["staining_method"],
                            },
                        )
                    ],
                )
            )
        logger.debug("Items for application run submission: %s", items)

        try:
            run = self.application_run_submit(application_version.application_version_id, items, custom_metadata)
            logger.info(
                "Submitted application run with items: %s, application run id %s, custom metadata: %s",
                items,
                run.application_run_id,
                custom_metadata,
            )
            return run
        except ValueError as e:
            message = f"Failed to submit application run for version '{application_version_id}': {e}"
            logger.warning(message)
            raise ValueError(message) from e
        except Exception as e:
            message = f"Failed to submit application run for version '{application_version_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_run_submit(
        self, application_version_id: str, items: list[InputItem], custom_metadata: dict[str, Any] | None = None
    ) -> ApplicationRun:
        """Submit a run for the given application.

        Args:
            application_version_id: The ID of the application version to run.
            items: The input items for the run.
            custom_metadata: Optional custom metadata to attach to the run.

        Returns:
            ApplicationRun: The submitted run.

        Raises:
            NotFoundException: If the application version with the given ID is not found.
            ValueError: If the application version ID is invalid or items invalid.
            RuntimeError: If submitting the run failed unexpectedly.
        """
        try:
            return self._get_platform_client().runs.create(
                application_version=application_version_id, items=items, custom_metadata=custom_metadata
            )
        except ValueError as e:
            message = f"Failed to submit application run for version '{application_version_id}': {e}"
            logger.warning(message)
            raise ValueError(message) from e
        except Exception as e:
            message = f"Failed to submit application run for version '{application_version_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_run_cancel(self, run_id: str) -> None:
        """Cancel a run by its ID.

        Args:
            run_id: The ID of the run to cancel

        Raises:
            Exception: If the client cannot be created.

        Raises:
            NotFoundException: If the application run with the given ID is not found.
            ValueError: If the run ID is invalid or the run cannot be canceled given its current state.
            RuntimeError: If canceling the run fails unexpectedly.
        """
        try:
            self.application_run(run_id).cancel()
        except ValueError as e:
            message = f"Failed to cancel application run with ID '{run_id}': ValueError {e}"
            logger.warning(message)
            raise ValueError(message) from e
        except NotFoundException as e:
            message = f"Application run with ID '{run_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except ApiException as e:
            if e.status == HTTPStatus.UNPROCESSABLE_ENTITY:
                message = f"Run ID '{run_id}' invalid: {e!s}."
                logger.warning(message)
                raise ValueError(message) from e
            message = f"Failed to retrieve application run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e
        except Exception as e:
            message = f"Failed to cancel application run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    def application_run_delete(self, run_id: str) -> None:
        """Delete a run by its ID.

        Args:
            run_id: The ID of the run to delete

        Raises:
            Exception: If the client cannot be created.

        Raises:
            NotFoundException: If the application run with the given ID is not found.
            ValueError: If the run ID is invalid or the run cannot be deleted given its current state.
            RuntimeError: If deleting the run fails unexpectedly.
        """
        try:
            logger.debug("Deleting application run with ID '%s'", run_id)
            self.application_run(run_id).delete()
            logger.debug("Deleted application run with ID '%s'", run_id)
        except ValueError as e:
            message = f"Failed to delete application run with ID '{run_id}': ValueError {e}"
            logger.warning(message)
            raise ValueError(message) from e
        except NotFoundException as e:
            message = f"Application run with ID '{run_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except Exception as e:
            message = f"Failed to delete application run with ID '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

    @staticmethod
    def application_run_download_static(  # noqa: PLR0913, PLR0917
        run_id: str,
        destination_directory: Path,
        create_subdirectory_for_run: bool = True,
        create_subdirectory_per_item: bool = True,
        wait_for_completion: bool = True,
        qupath_project: bool = False,
        download_progress_queue: Any | None = None,  # noqa: ANN401
    ) -> Path:
        """Download application run results with progress tracking, static variant.

        Args:
            run_id (str): The ID of the application run to download.
            destination_directory (Path): Directory to save downloaded files.
            create_subdirectory_for_run (bool): Whether to create a subdirectory for the run.
            create_subdirectory_per_item (bool): Whether to create a subdirectory for each item,
                if not set, all items will be downloaded to the same directory but prefixed
                with the item reference and underscore.
            wait_for_completion (bool): Whether to wait for run completion. Defaults to True.
            qupath_project (bool): If True, create QuPath project referencing input slides and results.
                This requires QuPath to be installed. The QuPath project will be created in a subfolder
                of the destination directory.
            download_progress_queue (Queue | None): Queue for GUI progress updates.

        Returns:
            Path: The directory containing downloaded results.

        Raises:
            ValueError: If the run ID is invalid or destination directory cannot be created.
            NotFoundException: If the application run with the given ID is not found.
            RuntimeError: If run details cannot be retrieved or download fails unexpectedly.
            requests.HTTPError: If the download fails with an HTTP error.
        """
        return Service().application_run_download(
            run_id,
            destination_directory,
            create_subdirectory_for_run,
            create_subdirectory_per_item,
            wait_for_completion,
            qupath_project,
            download_progress_queue,
        )

    def application_run_download(  # noqa: C901, PLR0912, PLR0913, PLR0914, PLR0915, PLR0917
        self,
        run_id: str,
        destination_directory: Path,
        create_subdirectory_for_run: bool = True,
        create_subdirectory_per_item: bool = True,
        wait_for_completion: bool = True,
        qupath_project: bool = False,
        download_progress_queue: Any | None = None,  # noqa: ANN401
        download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
    ) -> Path:
        """Download application run results with progress tracking.

        Args:
            progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
            run_id (str): The ID of the application run to download.
            destination_directory (Path): Directory to save downloaded files.
            create_subdirectory_for_run (bool): Whether to create a subdirectory for the run.
            create_subdirectory_per_item (bool): Whether to create a subdirectory for each item,
                if not set, all items will be downloaded to the same directory but prefixed
                with the item reference and underscore.
            wait_for_completion (bool): Whether to wait for run completion. Defaults to True.
            qupath_project (bool): If True, create QuPath project referencing input slides and results.
                This requires QuPath to be installed. The QuPath project will be created in a subfolder
                of the destination directory.
            download_progress_queue (Queue | None): Queue for GUI progress updates.
            download_progress_callable (Callable | None): Callback for CLI progress updates.

        Returns:
            Path: The directory containing downloaded results.

        Raises:
            ValueError: If the run ID is invalid or destination directory cannot be created.
            NotFoundException: If the application run with the given ID is not found.
            RuntimeError: If run details cannot be retrieved or download fails unexpectedly.
            requests.HTTPError: If the download fails with an HTTP error.
        """
        if qupath_project and not has_qupath_extra:
            message = "QuPath project creation requested, but 'qupath' extra is not installed."
            message += 'Start launchpad with `uvx --with "aignostics[qupath]" ....'
            logger.warning(message)
            raise ValueError(message)
        progress = DownloadProgress()
        Service._update_progress(progress, download_progress_callable, download_progress_queue)

        application_run = self.application_run(run_id)
        final_destination_directory = destination_directory
        try:
            details = application_run.details()
        except NotFoundException as e:
            message = f"Application run with ID '{run_id}' not found: {e}"
            logger.warning(message)
            raise NotFoundException(message) from e
        except ApiException as e:
            if e.status == HTTPStatus.UNPROCESSABLE_ENTITY:
                message = f"Run ID '{run_id}' invalid: {e!s}."
                logger.warning(message)
                raise ValueError(message) from e
            message = f"Failed to retrieve details for application run '{run_id}': {e}"
            logger.exception(message)
            raise RuntimeError(message) from e

        if create_subdirectory_for_run:
            final_destination_directory = destination_directory / details.application_run_id
        try:
            final_destination_directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            message = f"Failed to create destination directory '{final_destination_directory}': {e}"
            logger.warning(message)
            raise ValueError(message) from e

        if qupath_project:

            def update_qupath_add_input_progress(qupath_add_input_progress: QuPathAddProgress) -> None:
                progress.status = DownloadProgressState.QUPATH_ADD_INPUT
                progress.qupath_add_input_progress = qupath_add_input_progress
                Service._update_progress(progress, download_progress_callable, download_progress_queue)

            logger.debug("Adding input slides to QuPath project ...")
            image_paths = []
            for item in application_run.results():
                image_path = Path(item.reference)
                if image_path.is_file():
                    image_paths.append(image_path.resolve())
            added = QuPathService.add(
                final_destination_directory / "qupath", image_paths, update_qupath_add_input_progress
            )
            message = f"Added '{added}' input slides to QuPath project."
            logger.info(message)

        logger.debug("Downloading results for run '%s' to '%s'", run_id, final_destination_directory)

        progress.status = DownloadProgressState.CHECKING
        Service._update_progress(progress, download_progress_callable, download_progress_queue)

        downloaded_items: set[str] = set()  # Track downloaded items to avoid re-downloading
        while True:
            run_details = application_run.details()  # (Re)load current run details
            progress.run = run_details
            Service._update_progress(progress, download_progress_callable, download_progress_queue)

            self._download_available_items(
                progress,
                application_run,
                final_destination_directory,
                downloaded_items,
                create_subdirectory_per_item,
                download_progress_queue,
                download_progress_callable,
            )

            if run_details.status in {
                ApplicationRunStatus.CANCELED_SYSTEM,
                ApplicationRunStatus.CANCELED_USER,
                ApplicationRunStatus.COMPLETED,
                ApplicationRunStatus.COMPLETED_WITH_ERROR,
                ApplicationRunStatus.REJECTED,
            }:
                logger.debug(
                    "Run '%s' reached final status '%s' with message '%s'.",
                    run_id,
                    run_details.status,
                    run_details.message,
                )
                break

            if not wait_for_completion:
                logger.debug(
                    "Run '%s' is in progress with status '%s' and message '%s', "
                    "but not requested to wait for completion.",
                    run_id,
                    run_details.status,
                    run_details.message,
                )
                break

            logger.debug(
                "Run '%s' is in progress with status '%s', waiting for completion ...", run_id, run_details.status
            )
            progress.status = DownloadProgressState.WAITING
            Service._update_progress(progress, download_progress_callable, download_progress_queue)
            time.sleep(APPLICATION_RUN_DOWNLOAD_SLEEP_SECONDS)

        if qupath_project:
            logger.debug("Adding result images to QuPath project ...")

            def update_qupath_add_results_progress(qupath_add_results_progress: QuPathAddProgress) -> None:
                progress.status = DownloadProgressState.QUPATH_ADD_RESULTS
                progress.qupath_add_results_progress = qupath_add_results_progress
                Service._update_progress(progress, download_progress_callable, download_progress_queue)

            added = QuPathService.add(
                final_destination_directory / "qupath",
                [final_destination_directory],
                update_qupath_add_results_progress,
            )
            message = f"Added {added} result images to QuPath project."
            logger.info(message)
            logger.debug("Annotating input slides with polygons from results ...")

            def update_qupath_annotate_input_with_results_progress(
                qupath_annotate_input_with_results_progress: QuPathAnnotateProgress,
            ) -> None:
                progress.status = DownloadProgressState.QUPATH_ANNOTATE_INPUT_WITH_RESULTS
                progress.qupath_annotate_input_with_results_progress = qupath_annotate_input_with_results_progress
                Service._update_progress(progress, download_progress_callable, download_progress_queue)

            total_annotations = 0
            results = list(application_run.results())
            progress.item_count = len(results)
            for item_index, item in enumerate(application_run.results()):
                progress.item_index = item_index
                Service._update_progress(progress, download_progress_callable, download_progress_queue)

                image_path = Path(item.reference)
                if not image_path.is_file():
                    continue
                for artifact in item.output_artifacts:
                    if (
                        get_mime_type_for_artifact(artifact) == "application/geo+json"
                        and artifact.name == "cell_classification:geojson_polygons"
                    ):
                        artifact_name = artifact.name
                        if create_subdirectory_per_item:
                            reference_path = Path(item.reference)
                            stem_name = reference_path.stem
                            artifact_path = (
                                final_destination_directory
                                / stem_name
                                / f"{sanitize_path_component(artifact_name)}.json"
                            )
                        else:
                            artifact_path = (
                                final_destination_directory / f"{sanitize_path_component(artifact_name)}.json"
                            )
                        message = f"Annotating input slide '{image_path}' with artifact '{artifact_path}' ..."
                        logger.debug(message)
                        added = QuPathService.annotate(
                            final_destination_directory / "qupath",
                            image_path,
                            artifact_path,
                            update_qupath_annotate_input_with_results_progress,
                        )
                        message = f"Added {added} annotations to input slide '{image_path}' from '{artifact_path}'."
                        logger.info(message)
                        total_annotations += added
            message = f"Added {added} annotations to input slides."
            logger.info(message)

        progress.status = DownloadProgressState.COMPLETED
        Service._update_progress(progress, download_progress_callable, download_progress_queue)

        return final_destination_directory

    @staticmethod
    def _update_progress(
        progress: DownloadProgress,
        download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
        download_progress_queue: Any | None = None,  # noqa: ANN401
    ) -> None:
        if download_progress_callable:
            download_progress_callable(progress)
        if download_progress_queue:
            download_progress_queue.put_nowait(progress)

    def _download_available_items(  # noqa: PLR0913, PLR0917
        self,
        progress: DownloadProgress,
        application_run: ApplicationRun,
        destination_directory: Path,
        downloaded_items: set[str],
        create_subdirectory_per_item: bool = False,
        download_progress_queue: Any | None = None,  # noqa: ANN401
        download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
    ) -> None:
        """Download items that are available and not yet downloaded.

        Args:
            progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
            application_run (ApplicationRun): The application run object.
            destination_directory (Path): Directory to save files.
            downloaded_items (set): Set of already downloaded item references.
            create_subdirectory_per_item (bool): Whether to create a subdirectory for each item.
            download_progress_queue (Queue | None): Queue for GUI progress updates.
            download_progress_callable (Callable | None): Callback for CLI progress updates.
        """
        items = list(application_run.results())
        progress.item_count = len(items)
        for item_index, item in enumerate(items):
            if item.reference in downloaded_items:
                continue

            if item.status == ItemStatus.SUCCEEDED:
                progress.status = DownloadProgressState.DOWNLOADING
                progress.item_index = item_index
                progress.item = item
                progress.item_reference = item.reference

                progress.artifact_count = len(item.output_artifacts)
                Service._update_progress(progress, download_progress_callable, download_progress_queue)

                if create_subdirectory_per_item:
                    reference_path = Path(item.reference)
                    stem_name = reference_path.stem
                    try:
                        # Handle case where reference might be relative to destination
                        rel_path = reference_path.relative_to(destination_directory)
                        stem_name = rel_path.stem
                    except ValueError:
                        # Not a subfolder - just use the stem
                        pass
                    item_directory = destination_directory / stem_name
                else:
                    item_directory = destination_directory
                item_directory.mkdir(exist_ok=True)

                for artifact_index, artifact in enumerate(item.output_artifacts):
                    progress.artifact_index = artifact_index
                    progress.artifact = artifact
                    Service._update_progress(progress, download_progress_callable, download_progress_queue)

                    self._download_item_artifact(
                        progress,
                        artifact,
                        item_directory,
                        item.reference if not create_subdirectory_per_item else "",
                        download_progress_queue,
                        download_progress_callable,
                    )

                downloaded_items.add(item.reference)

    def _download_item_artifact(  # noqa: PLR0913, PLR0917
        self,
        progress: DownloadProgress,
        artifact: Any,  # noqa: ANN401
        destination_directory: Path,
        prefix: str = "",
        download_progress_queue: Any | None = None,  # noqa: ANN401
        download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
    ) -> None:
        """Download a an artifact of a result item with progress tracking.

        Args:
            progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
            artifact (Any): The artifact to download.
            destination_directory (Path): Directory to save the file.
            prefix (str): Prefix for the file name, if needed.
            download_progress_queue (Queue | None): Queue for GUI progress updates.
            download_progress_callable (Callable | None): Callback for CLI progress updates.

        Raises:
            ValueError: If no checksum metadata is found for the artifact.
            requests.HTTPError: If the download fails.
        """
        metadata = artifact.metadata or {}
        metadata_checksum = metadata.get("checksum_base64_crc32c", "") or metadata.get("checksum_crc32c", "")
        if not metadata_checksum:
            message = f"No checksum metadata found for artifact {artifact.name}"
            logger.error(message)
            raise ValueError(message)

        artifact_path = (
            destination_directory
            / f"{prefix}{sanitize_path_component(artifact.name)}{get_file_extension_for_artifact(artifact)}"
        )

        if artifact_path.exists():
            checksum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]
            with open(artifact_path, "rb") as f:
                while chunk := f.read(APPLICATION_RUN_FILE_READ_CHUNK_SIZE):
                    checksum.update(chunk)  # type: ignore[no-untyped-call]
            existing_checksum = base64.b64encode(checksum.digest()).decode("ascii")  # type: ignore[no-untyped-call]
            if existing_checksum == metadata_checksum:
                logger.debug("File %s already exists with correct checksum", artifact_path)
                return

        self._download_file_with_progress(
            progress,
            artifact.download_url,
            artifact_path,
            metadata_checksum,
            download_progress_queue,
            download_progress_callable,
        )

    @staticmethod
    def _download_file_with_progress(  # noqa: PLR0913, PLR0917
        progress: DownloadProgress,
        signed_url: str,
        artifact_path: Path,
        metadata_checksum: str,
        download_progress_queue: Any | None = None,  # noqa: ANN401
        download_progress_callable: Callable | None = None,  # type: ignore[type-arg]
    ) -> None:
        """Download a file with progress tracking support.

        Args:
            progress (DownloadProgress): Progress tracking object for GUI or CLI updates.
            signed_url (str): The signed URL to download from.
            artifact_path (Path): Path to save the file.
            metadata_checksum (str): Expected CRC32C checksum in base64.
            download_progress_queue (Any | None): Queue for GUI progress updates.
            download_progress_callable (Callable | None): Callback for CLI progress updates.

        Raises:
            ValueError: If checksum verification fails.
            requests.HTTPError: If download fails.
        """
        logger.debug(
            "Downloading artifact '%s' to '%s' with expected checksum '%s' for item reference '%s'",
            progress.artifact.name if progress.artifact else "unknown",
            artifact_path,
            metadata_checksum,
            progress.item_reference or "unknown",
        )
        progress.artifact_download_url = signed_url
        progress.artifact_path = artifact_path
        progress.artifact_downloaded_size = 0
        progress.artifact_downloaded_chunk_size = 0
        progress.artifact_size = None
        Service._update_progress(progress, download_progress_callable, download_progress_queue)

        checksum = google_crc32c.Checksum()  # type: ignore[no-untyped-call]

        with requests.get(signed_url, stream=True, timeout=60) as stream:
            stream.raise_for_status()
            progress.artifact_size = int(stream.headers.get("content-length", 0))
            Service._update_progress(progress, download_progress_callable, download_progress_queue)
            with open(artifact_path, mode="wb") as file:
                for chunk in stream.iter_content(chunk_size=APPLICATION_RUN_DOWNLOAD_CHUNK_SIZE):
                    if chunk:
                        file.write(chunk)
                        checksum.update(chunk)  # type: ignore[no-untyped-call]
                        progress.artifact_downloaded_chunk_size = len(chunk)
                        progress.artifact_downloaded_size += progress.artifact_downloaded_chunk_size
                        Service._update_progress(progress, download_progress_callable, download_progress_queue)

        downloaded_checksum = base64.b64encode(checksum.digest()).decode("ascii")  # type: ignore[no-untyped-call]
        if downloaded_checksum != metadata_checksum:
            artifact_path.unlink()  # Remove corrupted file
            msg = f"Checksum mismatch for {artifact_path}: {downloaded_checksum} != {metadata_checksum}"
            logger.error(msg)
            raise ValueError(msg)
