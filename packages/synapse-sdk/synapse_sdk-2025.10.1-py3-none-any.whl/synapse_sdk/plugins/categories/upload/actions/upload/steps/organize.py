from ..context import StepResult, UploadContext
from ..enums import LogCode
from .base import BaseStep


class OrganizeFilesStep(BaseStep):
    """Organize files according to specifications using file discovery strategy."""

    @property
    def name(self) -> str:
        return 'organize_files'

    @property
    def progress_weight(self) -> float:
        return 0.15

    def execute(self, context: UploadContext) -> StepResult:
        """Execute file organization step."""
        file_discovery_strategy = context.strategies.get('file_discovery')
        if not file_discovery_strategy:
            return self.create_error_result('File discovery strategy not found')

        if not context.file_specifications:
            return self.create_error_result('File specifications not available')

        try:
            # Create type directories mapping
            type_dirs = {}
            for spec in context.file_specifications:
                spec_name = spec['name']
                spec_dir = context.pathlib_cwd / spec_name
                if spec_dir.exists() and spec_dir.is_dir():
                    type_dirs[spec_name] = spec_dir

            if type_dirs:
                context.run.log_message_with_code(LogCode.TYPE_DIRECTORIES_FOUND, list(type_dirs.keys()))
            else:
                context.run.log_message_with_code(LogCode.NO_TYPE_DIRECTORIES)
                return self.create_success_result(data={'organized_files': []})

            context.run.log_message_with_code(LogCode.TYPE_STRUCTURE_DETECTED)
            context.run.log_message_with_code(LogCode.FILE_ORGANIZATION_STARTED)

            # Discover files in type directories
            all_files = []
            is_recursive = context.get_param('is_recursive', True)

            for spec_name, dir_path in type_dirs.items():
                files_in_dir = file_discovery_strategy.discover(dir_path, is_recursive)
                all_files.extend(files_in_dir)

            if not all_files:
                context.run.log_message_with_code(LogCode.NO_FILES_FOUND_WARNING)
                return self.create_success_result(data={'organized_files': []})

            # Organize files using strategy
            organized_files = file_discovery_strategy.organize(
                all_files, context.file_specifications, context.metadata or {}, type_dirs
            )

            if organized_files:
                context.run.log_message_with_code(LogCode.FILES_DISCOVERED, len(organized_files))
                context.add_organized_files(organized_files)

            return self.create_success_result(
                data={'organized_files': organized_files},
                rollback_data={'files_count': len(organized_files), 'type_dirs': list(type_dirs.keys())},
            )

        except Exception as e:
            return self.create_error_result(f'File organization failed: {str(e)}')

    def can_skip(self, context: UploadContext) -> bool:
        """File organization cannot be skipped."""
        return False

    def rollback(self, context: UploadContext) -> None:
        """Rollback file organization."""
        # Clear organized files
        context.organized_files.clear()
        context.run.log_message('Rolled back file organization')

    def validate_prerequisites(self, context: UploadContext) -> None:
        """Validate prerequisites for file organization."""
        if not context.pathlib_cwd:
            raise ValueError('Working directory path not set')

        if not context.file_specifications:
            raise ValueError('File specifications not available')
