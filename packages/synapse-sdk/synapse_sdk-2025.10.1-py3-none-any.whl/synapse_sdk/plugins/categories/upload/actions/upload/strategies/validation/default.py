from typing import Dict, List

from synapse_sdk.clients.validators.collections import FileSpecificationValidator

from ..base import ValidationResult, ValidationStrategy


class DefaultValidationStrategy(ValidationStrategy):
    """Default validation strategy for upload operations."""

    def validate_params(self, params: Dict) -> ValidationResult:
        """Validate action parameters."""
        errors = []

        # Check required parameters
        required_params = ['storage', 'data_collection', 'path', 'name']
        for param in required_params:
            if param not in params:
                errors.append(f'Missing required parameter: {param}')

        # Check parameter types
        if 'storage' in params and not isinstance(params['storage'], int):
            errors.append("Parameter 'storage' must be an integer")

        if 'data_collection' in params and not isinstance(params['data_collection'], int):
            errors.append("Parameter 'data_collection' must be an integer")

        if 'is_recursive' in params and not isinstance(params['is_recursive'], bool):
            errors.append("Parameter 'is_recursive' must be a boolean")

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def validate_files(self, files: List[Dict], specs: Dict) -> ValidationResult:
        """Validate organized files against specifications."""
        try:
            validator = FileSpecificationValidator(specs, files)
            is_valid = validator.validate()

            if is_valid:
                return ValidationResult(valid=True)
            else:
                return ValidationResult(valid=False, errors=['File specification validation failed'])

        except Exception as e:
            return ValidationResult(valid=False, errors=[f'Validation error: {str(e)}'])
