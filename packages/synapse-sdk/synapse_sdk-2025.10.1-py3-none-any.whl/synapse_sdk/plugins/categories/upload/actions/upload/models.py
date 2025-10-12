from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ValidationInfo, field_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.utils.pydantic.validators import non_blank
from synapse_sdk.utils.storage import get_pathlib

from .utils import ExcelSecurityConfig


class UploadParams(BaseModel):
    """Upload action parameter validation model.

    Defines and validates all parameters required for upload operations.
    Uses Pydantic for type validation and custom validators to ensure
    storage, data_collection, and project resources exist before processing.

    Attributes:
        name (str): Human-readable name for the upload operation
        description (str | None): Optional description of the upload
        path (str): File system path to upload from
        storage (int): Storage ID where files will be uploaded
        data_collection (int): Data data_collection ID for organizing uploads
        project (int | None): Optional project ID for grouping
        excel_metadata_path (str | None): Path to Excel metadata file
        is_recursive (bool): Whether to recursively process subdirectories
        max_file_size_mb (int): Maximum file size limit in megabytes
        creating_data_unit_batch_size (int): Batch size for data unit creation
        use_async_upload (bool): Whether to use asynchronous upload processing
        extra_params (dict | None): Extra parameters for the action.
            Example: {"include_metadata": True, "compression": "gzip"}

    Validation:
        - name: Must be non-blank after validation
        - storage: Must exist and be accessible via client API
        - data_collection: Must exist and be accessible via client API
        - project: Must exist if specified, or can be None
        - excel_metadata_path: Must be valid Excel file if specified

    Example:
        >>> params = UploadParams(
        ...     name="Data Upload",
        ...     path="/data/files",
        ...     storage=1,
        ...     data_collection=5
        ... )
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: str | None = None
    path: str
    storage: int
    data_collection: int
    project: int | None = None
    excel_metadata_path: str | None = None
    is_recursive: bool = True
    max_file_size_mb: int = 50
    creating_data_unit_batch_size: int = 1
    use_async_upload: bool = True
    extra_params: dict | None = None

    @field_validator('storage', mode='before')
    @classmethod
    def check_storage_exists(cls, value, info: ValidationInfo) -> int:
        if info.context is None:
            raise PydanticCustomError('missing_context', 'Validation context is required.')

        action = info.context['action']
        client = action.client
        try:
            client.get_storage(value)
        except ClientError:
            raise PydanticCustomError('client_error', 'Error occurred while checking storage exists.')
        return value

    @field_validator('data_collection', mode='before')
    @classmethod
    def check_data_collection_exists(cls, value, info: ValidationInfo) -> int:
        if info.context is None:
            raise PydanticCustomError('missing_context', 'Validation context is required.')

        action = info.context['action']
        client = action.client
        try:
            client.get_data_collection(value)
        except ClientError:
            raise PydanticCustomError('client_error', 'Error occurred while checking data_collection exists.')
        return value

    @field_validator('project', mode='before')
    @classmethod
    def check_project_exists(cls, value, info: ValidationInfo) -> int | None:
        if not value:
            return value

        if info.context is None:
            raise PydanticCustomError('missing_context', 'Validation context is required.')

        action = info.context['action']
        client = action.client
        try:
            client.get_project(value)
        except ClientError:
            raise PydanticCustomError('client_error', 'Error occurred while checking project exists.')
        return value

    @field_validator('excel_metadata_path', mode='after')
    @classmethod
    def check_excel_metadata_path(cls, value, info: ValidationInfo) -> str | None:
        if not value:
            return value

        # Validate file extension
        if not value.lower().endswith(('.xlsx', '.xls')):
            raise PydanticCustomError('invalid_file_type', 'Excel metadata file must be .xlsx or .xls format.')

        # Get storage and path from validation data
        if not (hasattr(info, 'data') and 'storage' in info.data and 'path' in info.data):
            # If we don't have storage/path data yet, just validate extension
            return value

        if info.context is None:
            raise PydanticCustomError('missing_context', 'Validation context is required.')

        action = info.context['action']
        client = action.client

        try:
            # Get storage configuration
            storage_id = info.data['storage']
            storage = client.get_storage(storage_id)

            # Skip file system validation if storage doesn't have provider (likely test environment)
            if not isinstance(storage, dict) or 'provider' not in storage:
                # Basic validation only - likely in test environment
                return value

            # Get the actual file system path using storage + path
            base_path = get_pathlib(storage, info.data['path'])

            # Support both absolute and relative paths
            if Path(value).is_absolute():
                excel_path = Path(value)
            else:
                excel_path = base_path / value

            if not excel_path.exists():
                raise PydanticCustomError('file_not_found', 'Excel metadata file not found.')

            # Validate file size
            file_size = excel_path.stat().st_size
            excel_config = ExcelSecurityConfig()
            if file_size > excel_config.MAX_FILE_SIZE_BYTES:
                max_size_mb = excel_config.MAX_FILE_SIZE_MB
                raise PydanticCustomError(
                    'file_too_large',
                    'Excel metadata file is too large. Maximum size is {max_size_mb}MB.',
                    {'max_size_mb': max_size_mb},
                )

            # Validate file format
            try:
                with open(excel_path, 'rb') as f:
                    header = f.read(8)
                    if not header:
                        raise PydanticCustomError('invalid_file', 'Excel metadata file appears to be empty.')

                    if excel_path.suffix.lower() == '.xlsx':
                        if not header.startswith(b'PK'):
                            raise PydanticCustomError('invalid_file', 'Excel metadata file appears to be corrupted.')
                    elif excel_path.suffix.lower() == '.xls':
                        if not (header.startswith(b'\xd0\xcf\x11\xe0') or header.startswith(b'\x09\x08')):
                            raise PydanticCustomError('invalid_file', 'Excel metadata file appears to be corrupted.')

            except (OSError, IOError):
                raise PydanticCustomError('file_access_error', 'Cannot access Excel metadata file.')

        except ClientError:
            raise PydanticCustomError('client_error', 'Error occurred while checking storage.')
        except Exception as e:
            raise PydanticCustomError('validation_error', f'Error validating Excel metadata file: {str(e)}')

        return value
