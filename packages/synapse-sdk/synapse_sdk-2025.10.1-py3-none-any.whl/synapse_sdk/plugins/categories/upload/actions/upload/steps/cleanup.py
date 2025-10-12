import os
import shutil
from pathlib import Path

from ..context import StepResult, UploadContext
from ..enums import LogCode
from .base import BaseStep


class CleanupStep(BaseStep):
    """Cleanup temporary resources and finalize workflow."""

    @property
    def name(self) -> str:
        return 'cleanup'

    @property
    def progress_weight(self) -> float:
        return 0.05

    def execute(self, context: UploadContext) -> StepResult:
        """Execute cleanup step."""
        try:
            # Cleanup temporary directory
            self._cleanup_temp_directory(context)

            # Log completion
            context.run.log_message_with_code(LogCode.IMPORT_COMPLETED)

            return self.create_success_result(data={'cleanup_completed': True}, rollback_data={'temp_cleaned': True})

        except Exception as e:
            # Cleanup failures shouldn't stop the workflow
            context.run.log_message(f'Cleanup warning: {str(e)}')
            return self.create_success_result(
                data={'cleanup_completed': False}, rollback_data={'cleanup_error': str(e)}
            )

    def can_skip(self, context: UploadContext) -> bool:
        """Cleanup step can be skipped if disabled."""
        return context.get_param('skip_cleanup', False)

    def rollback(self, context: UploadContext) -> None:
        """Rollback cleanup (nothing to rollback for cleanup)."""
        context.run.log_message('Cleanup step rollback - no action needed')

    def _cleanup_temp_directory(self, context: UploadContext, temp_path: Path = None) -> None:
        """Clean up temporary directory."""
        if temp_path is None:
            try:
                temp_path = Path(os.getcwd()) / 'temp'
            except (FileNotFoundError, OSError):
                return

        if not temp_path.exists():
            return

        try:
            shutil.rmtree(temp_path, ignore_errors=True)
            context.run.log_message(f'Cleaned up temporary directory: {temp_path}')
        except Exception as e:
            context.run.log_message(f'Failed to cleanup temporary directory: {str(e)}')
