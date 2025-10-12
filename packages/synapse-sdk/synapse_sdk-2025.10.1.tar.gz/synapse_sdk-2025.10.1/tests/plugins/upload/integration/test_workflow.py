import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from synapse_sdk.plugins.categories.upload.actions.upload.context import UploadContext
from synapse_sdk.plugins.categories.upload.actions.upload.factory import StrategyFactory
from synapse_sdk.plugins.categories.upload.actions.upload.orchestrator import UploadOrchestrator
from synapse_sdk.plugins.categories.upload.actions.upload.registry import StepRegistry
from synapse_sdk.plugins.categories.upload.actions.upload.steps.cleanup import CleanupStep
from synapse_sdk.plugins.categories.upload.actions.upload.steps.collection import AnalyzeCollectionStep
from synapse_sdk.plugins.categories.upload.actions.upload.steps.generate import GenerateDataUnitsStep
from synapse_sdk.plugins.categories.upload.actions.upload.steps.initialize import InitializeStep
from synapse_sdk.plugins.categories.upload.actions.upload.steps.metadata import ProcessMetadataStep
from synapse_sdk.plugins.categories.upload.actions.upload.steps.organize import OrganizeFilesStep
from synapse_sdk.plugins.categories.upload.actions.upload.steps.upload import UploadFilesStep
from synapse_sdk.plugins.categories.upload.actions.upload.steps.validate import ValidateFilesStep


class TestUploadWorkflowIntegration:
    """Integration tests for complete upload workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_run = Mock()
        self.mock_client = Mock()

        # Setup mock client responses
        self.mock_client.get_storage.return_value = {
            'id': 1,
            'name': 'test-storage',
            'provider': 'file_system',
            'configuration': {'location': '/test'},
        }
        self.mock_client.get_data_collection.return_value = {
            'id': 1,
            'file_specifications': [{'name': 'type1', 'is_required': True}, {'name': 'type2', 'is_required': False}],
        }

        self.params = {
            'name': 'Test Upload',
            'path': '/test/path',
            'storage': 1,
            'data_collection': 1,
            'is_recursive': True,
            'use_async_upload': False,  # Use sync for simpler testing
            'creating_data_unit_batch_size': 2,
        }

    def create_test_directory_structure(self):
        """Create test directory structure with files."""
        temp_dir = tempfile.mkdtemp()
        base_path = Path(temp_dir)

        # Create type directories
        type1_dir = base_path / 'type1'
        type2_dir = base_path / 'type2'
        type1_dir.mkdir()
        type2_dir.mkdir()

        # Create test files
        (type1_dir / 'file1.txt').write_text('content1')
        (type1_dir / 'file2.txt').write_text('content2')
        (type2_dir / 'file1.json').write_text('{"data": "test1"}')
        (type2_dir / 'file2.json').write_text('{"data": "test2"}')

        return base_path

    @patch('synapse_sdk.plugins.categories.upload.actions.upload.steps.initialize.get_pathlib')
    def test_complete_workflow_success(self, mock_get_pathlib):
        """Test successful execution of complete workflow."""
        # Setup
        test_dir = self.create_test_directory_structure()
        mock_get_pathlib.return_value = test_dir

        context = UploadContext(self.params, self.mock_run, self.mock_client)
        step_registry = StepRegistry()

        # Register all steps
        step_registry.register(InitializeStep())
        step_registry.register(ProcessMetadataStep())
        step_registry.register(AnalyzeCollectionStep())
        step_registry.register(OrganizeFilesStep())
        step_registry.register(ValidateFilesStep())
        step_registry.register(UploadFilesStep())
        step_registry.register(GenerateDataUnitsStep())
        step_registry.register(CleanupStep())

        # Create strategies
        strategy_factory = StrategyFactory()
        strategies = {
            'validation': strategy_factory.create_validation_strategy(self.params),
            'file_discovery': strategy_factory.create_file_discovery_strategy(self.params),
            'metadata': strategy_factory.create_metadata_strategy(self.params),
            'upload': strategy_factory.create_upload_strategy(self.params, context),
            'data_unit': strategy_factory.create_data_unit_strategy(self.params, context),
        }

        # Execute workflow
        orchestrator = UploadOrchestrator(context, step_registry, strategies)
        result = orchestrator.execute()

        # Verify result
        assert result['success'] is True
        assert len(result['errors']) == 0
        assert 'uploaded_files_count' in result
        assert 'generated_data_units_count' in result

        # Verify all steps were executed
        assert len(orchestrator.get_executed_steps()) == 8

        # Verify context state
        assert context.storage is not None
        assert context.pathlib_cwd is not None
        assert context.file_specifications is not None

    @patch('synapse_sdk.plugins.categories.upload.actions.upload.steps.initialize.get_pathlib')
    def test_workflow_with_missing_storage(self, mock_get_pathlib):
        """Test workflow failure when storage is missing."""
        # Setup client to fail on storage retrieval
        self.mock_client.get_storage.side_effect = Exception('Storage not found')

        context = UploadContext(self.params, self.mock_run, self.mock_client)
        step_registry = StepRegistry()
        step_registry.register(InitializeStep())

        strategy_factory = StrategyFactory()
        strategies = {
            'validation': strategy_factory.create_validation_strategy(self.params),
        }

        # Execute workflow - should fail
        orchestrator = UploadOrchestrator(context, step_registry, strategies)

        with pytest.raises(Exception, match='Failed to get storage'):
            orchestrator.execute()

        # Verify rollback was executed
        assert orchestrator.is_rollback_executed() is True

    @patch('synapse_sdk.utils.storage.get_pathlib')
    def test_workflow_with_no_files(self, mock_get_pathlib):
        """Test workflow with empty directories."""
        # Setup empty directory
        temp_dir = tempfile.mkdtemp()
        base_path = Path(temp_dir)
        mock_get_pathlib.return_value = base_path

        context = UploadContext(self.params, self.mock_run, self.mock_client)
        step_registry = StepRegistry()

        # Register steps up to organize (where it should stop)
        step_registry.register(InitializeStep())
        step_registry.register(ProcessMetadataStep())
        step_registry.register(AnalyzeCollectionStep())
        step_registry.register(OrganizeFilesStep())

        strategy_factory = StrategyFactory()
        strategies = {
            'validation': strategy_factory.create_validation_strategy(self.params),
            'file_discovery': strategy_factory.create_file_discovery_strategy(self.params),
            'metadata': strategy_factory.create_metadata_strategy(self.params),
        }

        # Execute workflow
        orchestrator = UploadOrchestrator(context, step_registry, strategies)
        result = orchestrator.execute()

        # Should succeed but with no files
        assert result['success'] is True
        assert len(context.organized_files) == 0

    def test_workflow_summary(self):
        """Test getting workflow summary."""
        context = UploadContext(self.params, self.mock_run, self.mock_client)
        step_registry = StepRegistry()

        # Register a few steps
        step_registry.register(InitializeStep())
        step_registry.register(ProcessMetadataStep())

        strategies = {'validation': Mock()}

        orchestrator = UploadOrchestrator(context, step_registry, strategies)

        summary = orchestrator.get_workflow_summary()

        assert summary['total_steps'] == 2
        assert summary['executed_steps'] == 0
        assert summary['current_step_index'] == 0
        assert len(summary['step_names']) == 2
        assert summary['rollback_executed'] is False

    @patch('synapse_sdk.utils.storage.get_pathlib')
    def test_workflow_step_skipping(self, mock_get_pathlib):
        """Test workflow with skippable steps."""
        test_dir = self.create_test_directory_structure()
        mock_get_pathlib.return_value = test_dir

        # Create a step that can be skipped
        class SkippableStep(InitializeStep):
            @property
            def name(self) -> str:
                return 'skippable_test'

            def can_skip(self, context):
                return True  # Always skip

        context = UploadContext(self.params, self.mock_run, self.mock_client)
        step_registry = StepRegistry()

        step_registry.register(InitializeStep())
        step_registry.register(SkippableStep())

        strategy_factory = StrategyFactory()
        strategies = {
            'validation': strategy_factory.create_validation_strategy(self.params),
        }

        orchestrator = UploadOrchestrator(context, step_registry, strategies)
        result = orchestrator.execute()

        # Should succeed with one step skipped
        assert result['success'] is True
        executed_step_names = [step.name for step in orchestrator.get_executed_steps()]
        assert 'initialize' in executed_step_names
        assert 'skippable_test' not in executed_step_names

    def test_strategy_injection(self):
        """Test that strategies are properly injected into context."""
        context = UploadContext(self.params, self.mock_run, self.mock_client)
        step_registry = StepRegistry()

        strategies = {
            'validation': Mock(),
            'upload': Mock(),
        }

        orchestrator = UploadOrchestrator(context, step_registry, strategies)

        # Execute empty workflow to test injection
        orchestrator.execute()

        # Verify strategies were injected
        assert hasattr(context, 'strategies')
        assert context.strategies == strategies
