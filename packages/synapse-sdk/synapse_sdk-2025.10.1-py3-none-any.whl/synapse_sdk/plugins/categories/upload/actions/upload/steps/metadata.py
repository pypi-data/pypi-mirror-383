from pathlib import Path

from ..context import StepResult, UploadContext
from ..enums import LogCode
from ..exceptions import ExcelParsingError, ExcelSecurityError
from .base import BaseStep


class ProcessMetadataStep(BaseStep):
    """Process metadata from Excel files or other sources."""

    @property
    def name(self) -> str:
        return 'process_metadata'

    @property
    def progress_weight(self) -> float:
        return 0.10

    def execute(self, context: UploadContext) -> StepResult:
        """Execute metadata processing step."""
        metadata_strategy = context.strategies.get('metadata')
        if not metadata_strategy:
            context.run.log_message('No metadata strategy configured - skipping metadata processing')
            return self.create_success_result(data={'metadata': {}})

        excel_metadata = {}

        try:
            # Check if Excel metadata path is specified
            excel_metadata_path = context.get_param('excel_metadata_path')
            if excel_metadata_path:
                # Convert string to Path object
                if isinstance(excel_metadata_path, str):
                    excel_metadata_path = Path(excel_metadata_path)

                if excel_metadata_path.exists() and excel_metadata_path.is_file():
                    excel_path = excel_metadata_path
                else:
                    excel_path = context.pathlib_cwd / excel_metadata_path
                if not excel_path.exists():
                    context.run.log_message_with_code(LogCode.EXCEL_FILE_NOT_FOUND_PATH)
                    return self.create_success_result(data={'metadata': {}})
                excel_metadata = metadata_strategy.extract(excel_path)
            else:
                # Look for default metadata files (meta.xlsx, meta.xls)
                excel_path = self._find_excel_metadata_file(context.pathlib_cwd)
                if excel_path:
                    excel_metadata = metadata_strategy.extract(excel_path)

            # Validate extracted metadata
            if excel_metadata:
                validation_result = metadata_strategy.validate(excel_metadata)
                if not validation_result.valid:
                    error_msg = f'Metadata validation failed: {", ".join(validation_result.errors)}'
                    return self.create_error_result(error_msg)
                context.run.log_message_with_code(LogCode.EXCEL_METADATA_LOADED, len(excel_metadata))

            return self.create_success_result(
                data={'metadata': excel_metadata}, rollback_data={'metadata_processed': len(excel_metadata) > 0}
            )

        except ExcelSecurityError as e:
            context.run.log_message_with_code(LogCode.EXCEL_SECURITY_VIOLATION, str(e))
            return self.create_error_result(f'Excel security violation: {str(e)}')

        except ExcelParsingError as e:
            # If excel_metadata_path was specified, this is an error
            # If we were just looking for default files, it's not an error
            if context.get_param('excel_metadata_path'):
                context.run.log_message_with_code(LogCode.EXCEL_PARSING_ERROR, str(e))
                return self.create_error_result(f'Excel parsing error: {str(e)}')
            else:
                context.run.log_message_with_code(LogCode.EXCEL_PARSING_ERROR, str(e))
                return self.create_success_result(data={'metadata': {}})

        except Exception as e:
            return self.create_error_result(f'Unexpected error processing metadata: {str(e)}')

    def can_skip(self, context: UploadContext) -> bool:
        """Metadata step can be skipped if no metadata strategy is configured."""
        return 'metadata' not in context.strategies

    def rollback(self, context: UploadContext) -> None:
        """Rollback metadata processing."""
        # Clear any loaded metadata
        context.metadata.clear()

    def _find_excel_metadata_file(self, pathlib_cwd: Path) -> Path:
        """Find default Excel metadata file."""
        # Check .xlsx first as it's more common
        excel_path = pathlib_cwd / 'meta.xlsx'
        if excel_path.exists():
            return excel_path

        # Fallback to .xls
        excel_path = pathlib_cwd / 'meta.xls'
        if excel_path.exists():
            return excel_path

        return None
