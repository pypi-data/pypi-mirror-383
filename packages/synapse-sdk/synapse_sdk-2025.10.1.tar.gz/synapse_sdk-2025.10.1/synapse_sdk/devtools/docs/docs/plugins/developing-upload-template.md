# Developing Upload Templates with BaseUploader

This guide provides comprehensive documentation for plugin developers who want to create custom upload plugins using the BaseUploader template class. The BaseUploader follows the template method pattern to provide a structured, extensible foundation for file processing workflows.

## Quick Start

### Basic Plugin Structure

Create your upload plugin by inheriting from BaseUploader:

```python
from pathlib import Path
from typing import List, Dict, Any
from . import BaseUploader

class MyUploader(BaseUploader):
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
    
    def process_files(self, organized_files: List) -> List:
        """Implement your custom file processing logic here."""
        # Your processing logic goes here
        return organized_files
    
    def handle_upload_files(self) -> List[Dict[str, Any]]:
        """Main entry point called by the upload action."""
        return super().handle_upload_files()
```

### Minimal Working Example

```python
class SimpleUploader(BaseUploader):
    def process_files(self, organized_files: List) -> List:
        """Add metadata to each file group."""
        for file_group in organized_files:
            file_group['processed_by'] = 'SimpleUploader'
            file_group['processing_timestamp'] = datetime.now().isoformat()
        return organized_files
```

## Architecture Deep Dive

### Workflow Pipeline

The BaseUploader implements a comprehensive 6-step workflow pipeline:

```
1. setup_directories()    # Initialize directory structure
2. organize_files()       # Group and structure files
3. before_process()       # Pre-processing hooks
4. process_files()        # Main processing logic (REQUIRED)
5. after_process()        # Post-processing hooks
6. validate_files()       # Final validation and filtering
```

### Template Method Pattern

BaseUploader uses the template method pattern where:
- **Concrete methods** provide default behavior that works for most cases
- **Hook methods** allow customization at specific points
- **Abstract methods** must be implemented by subclasses

## Core Methods Reference

### Required Methods

#### `process_files(organized_files: List) -> List`

**Purpose**: Main processing method that transforms files according to your plugin's logic.

**When to use**: Always - this is the core method every plugin must implement.

**Parameters**:
- `organized_files`: List of file group dictionaries containing organized file data

**Returns**: List of processed file groups ready for upload

**Example**:
```python
def process_files(self, organized_files: List) -> List:
    """Convert TIFF images to JPEG format."""
    processed_files = []
    
    for file_group in organized_files:
        files_dict = file_group.get('files', {})
        converted_files = {}
        
        for spec_name, file_path in files_dict.items():
            if file_path.suffix.lower() in ['.tif', '.tiff']:
                # Convert TIFF to JPEG
                jpeg_path = self.convert_tiff_to_jpeg(file_path)
                converted_files[spec_name] = jpeg_path
                self.run.log_message(f"Converted {file_path} to {jpeg_path}")
            else:
                converted_files[spec_name] = file_path
        
        file_group['files'] = converted_files
        processed_files.append(file_group)
    
    return processed_files
```

### Optional Hook Methods

#### `setup_directories() -> None`

**Purpose**: Create custom directory structures before processing begins.

**When to use**: When your plugin needs specific directories for processing, temporary files, or output.

**Example**:
```python
def setup_directories(self):
    """Create processing directories."""
    (self.path / 'temp').mkdir(exist_ok=True)
    (self.path / 'processed').mkdir(exist_ok=True)
    (self.path / 'thumbnails').mkdir(exist_ok=True)
    self.run.log_message("Created processing directories")
```

#### `organize_files(files: List) -> List`

**Purpose**: Reorganize and structure files before main processing.

**When to use**: When you need to group files differently, filter by criteria, or restructure the data.

**Example**:
```python
def organize_files(self, files: List) -> List:
    """Group files by type and size."""
    large_files = []
    small_files = []
    
    for file_group in files:
        total_size = sum(f.stat().st_size for f in file_group.get('files', {}).values())
        if total_size > 100 * 1024 * 1024:  # 100MB
            large_files.append(file_group)
        else:
            small_files.append(file_group)
    
    # Process large files first
    return large_files + small_files
```

#### `before_process(organized_files: List) -> List`

**Purpose**: Pre-processing hook for setup tasks before main processing.

**When to use**: For validation, preparation, or initialization tasks.

**Example**:
```python
def before_process(self, organized_files: List) -> List:
    """Validate and prepare files for processing."""
    self.run.log_message(f"Starting processing of {len(organized_files)} file groups")
    
    # Check available disk space
    if not self.check_disk_space(organized_files):
        raise Exception("Insufficient disk space for processing")
    
    # Initialize processing resources
    self.processing_queue = Queue()
    return organized_files
```

#### `after_process(processed_files: List) -> List`

**Purpose**: Post-processing hook for cleanup and finalization.

**When to use**: For cleanup, final transformations, or resource deallocation.

**Example**:
```python
def after_process(self, processed_files: List) -> List:
    """Clean up temporary files and generate summary."""
    # Remove temporary files
    temp_dir = self.path / 'temp'
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # Generate processing summary
    summary = {
        'total_processed': len(processed_files),
        'processing_time': time.time() - self.start_time,
        'plugin_version': '1.0.0'
    }
    
    self.run.log_message(f"Processing complete: {summary}")
    return processed_files
```

#### `validate_files(files: List) -> List`

**Purpose**: Custom validation logic beyond type checking.

**When to use**: When you need additional validation rules beyond the built-in file type validation.

**Example**:
```python
def validate_files(self, files: List) -> List:
    """Custom validation with size and format checks."""
    # First apply built-in type validation
    validated_files = self.validate_file_types(files)
    
    # Then apply custom validation
    final_files = []
    for file_group in validated_files:
        if self.validate_file_group(file_group):
            final_files.append(file_group)
        else:
            self.run.log_message(f"File group failed custom validation: {file_group}")
    
    return final_files

def validate_file_group(self, file_group: Dict) -> bool:
    """Custom validation for individual file groups."""
    files_dict = file_group.get('files', {})
    
    for spec_name, file_path in files_dict.items():
        # Check file size limits
        if file_path.stat().st_size > 500 * 1024 * 1024:  # 500MB limit
            return False
        
        # Check file accessibility
        if not os.access(file_path, os.R_OK):
            return False
    
    return True
```

## Advanced Features

### File Type Validation System

The BaseUploader includes a sophisticated validation system that you can customize:

#### Default File Extensions

```python
def get_file_extensions_config(self) -> Dict[str, List[str]]:
    """Override to customize allowed file extensions."""
    return {
        'pcd': ['.pcd'],
        'text': ['.txt', '.html'],
        'audio': ['.wav', '.mp3'],
        'data': ['.bin', '.json', '.fbx'],
        'image': ['.jpg', '.jpeg', '.png'],
        'video': ['.mp4'],
    }
```

#### Custom Extension Configuration

```python
class CustomUploader(BaseUploader):
    def get_file_extensions_config(self) -> Dict[str, List[str]]:
        """Add support for additional formats."""
        config = super().get_file_extensions_config()
        config.update({
            'cad': ['.dwg', '.dxf', '.step'],
            'archive': ['.zip', '.rar', '.7z'],
            'document': ['.pdf', '.docx', '.xlsx']
        })
        return config
```

#### Conversion Warnings

```python
def get_conversion_warnings_config(self) -> Dict[str, str]:
    """Override to customize conversion warnings."""
    return {
        '.tif': ' .jpg, .png',
        '.tiff': ' .jpg, .png',
        '.avi': ' .mp4',
        '.mov': ' .mp4',
        '.raw': ' .jpg, .png',
        '.bmp': ' .jpg, .png',
    }
```

### Custom Filtering

Implement the `filter_files` method for fine-grained control:

```python
def filter_files(self, organized_file: Dict[str, Any]) -> bool:
    """Custom filtering logic."""
    # Filter by file size
    files_dict = organized_file.get('files', {})
    total_size = sum(f.stat().st_size for f in files_dict.values())
    
    if total_size < 1024:  # Skip files smaller than 1KB
        self.run.log_message(f"Skipping small file group: {total_size} bytes")
        return False
    
    # Filter by file age
    oldest_file = min(files_dict.values(), key=lambda f: f.stat().st_mtime)
    age_days = (time.time() - oldest_file.stat().st_mtime) / 86400
    
    if age_days > 365:  # Skip files older than 1 year
        self.run.log_message(f"Skipping old file group: {age_days} days old")
        return False
    
    return True
```

## Real-World Examples

### Example 1: Image Processing Plugin

```python
class ImageProcessingUploader(BaseUploader):
    """Converts TIFF images to JPEG and generates thumbnails."""
    
    def setup_directories(self):
        """Create directories for processed images and thumbnails."""
        (self.path / 'processed').mkdir(exist_ok=True)
        (self.path / 'thumbnails').mkdir(exist_ok=True)
    
    def organize_files(self, files: List) -> List:
        """Separate raw and processed images."""
        raw_images = []
        processed_images = []
        
        for file_group in files:
            has_raw = any(
                f.suffix.lower() in ['.tif', '.tiff', '.raw'] 
                for f in file_group.get('files', {}).values()
            )
            
            if has_raw:
                raw_images.append(file_group)
            else:
                processed_images.append(file_group)
        
        # Process raw images first
        return raw_images + processed_images
    
    def process_files(self, organized_files: List) -> List:
        """Convert images and generate thumbnails."""
        processed_files = []
        
        for file_group in organized_files:
            files_dict = file_group.get('files', {})
            converted_files = {}
            
            for spec_name, file_path in files_dict.items():
                if file_path.suffix.lower() in ['.tif', '.tiff']:
                    # Convert to JPEG
                    jpeg_path = self.convert_to_jpeg(file_path)
                    converted_files[spec_name] = jpeg_path
                    
                    # Generate thumbnail
                    thumbnail_path = self.generate_thumbnail(jpeg_path)
                    converted_files[f"{spec_name}_thumbnail"] = thumbnail_path
                    
                    self.run.log_message(f"Processed {file_path.name} -> {jpeg_path.name}")
                else:
                    converted_files[spec_name] = file_path
            
            file_group['files'] = converted_files
            processed_files.append(file_group)
        
        return processed_files
    
    def convert_to_jpeg(self, tiff_path: Path) -> Path:
        """Convert TIFF to JPEG using PIL."""
        from PIL import Image
        
        output_path = self.path / 'processed' / f"{tiff_path.stem}.jpg"
        
        with Image.open(tiff_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            img.save(output_path, 'JPEG', quality=95)
        
        return output_path
    
    def generate_thumbnail(self, image_path: Path) -> Path:
        """Generate thumbnail for processed image."""
        from PIL import Image
        
        thumbnail_path = self.path / 'thumbnails' / f"{image_path.stem}_thumb.jpg"
        
        with Image.open(image_path) as img:
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=85)
        
        return thumbnail_path
```

### Example 2: Data Validation Plugin

```python
class DataValidationUploader(BaseUploader):
    """Validates data files and generates quality reports."""
    
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
        
        # Initialize validation config from extra_params
        self.validation_config = extra_params.get('validation_config', {})
        self.strict_mode = extra_params.get('strict_validation', False)
    
    def before_process(self, organized_files: List) -> List:
        """Initialize validation engine."""
        self.validation_results = []
        self.run.log_message(f"Starting validation of {len(organized_files)} file groups")
        return organized_files
    
    def process_files(self, organized_files: List) -> List:
        """Validate files and generate quality reports."""
        processed_files = []
        
        for file_group in organized_files:
            validation_result = self.validate_file_group(file_group)
            
            # Add validation metadata
            file_group['validation'] = validation_result
            file_group['quality_score'] = validation_result['score']
            
            # Include file group based on validation results
            if self.should_include_file_group(validation_result):
                processed_files.append(file_group)
                self.run.log_message(f"File group passed validation: {validation_result['score']}")
            else:
                self.run.log_message(f"File group failed validation: {validation_result['errors']}")
        
        return processed_files
    
    def validate_file_group(self, file_group: Dict) -> Dict:
        """Comprehensive validation of file group."""
        files_dict = file_group.get('files', {})
        errors = []
        warnings = []
        score = 100
        
        for spec_name, file_path in files_dict.items():
            # File existence and accessibility
            if not file_path.exists():
                errors.append(f"File not found: {file_path}")
                score -= 50
                continue
            
            if not os.access(file_path, os.R_OK):
                errors.append(f"File not readable: {file_path}")
                score -= 30
                continue
            
            # File size validation
            file_size = file_path.stat().st_size
            if file_size == 0:
                errors.append(f"Empty file: {file_path}")
                score -= 40
            elif file_size > 1024 * 1024 * 1024:  # 1GB
                warnings.append(f"Large file: {file_path} ({file_size} bytes)")
                score -= 10
            
            # Content validation based on extension
            try:
                if file_path.suffix.lower() == '.json':
                    self.validate_json_file(file_path)
                elif file_path.suffix.lower() in ['.jpg', '.png']:
                    self.validate_image_file(file_path)
                # Add more content validations as needed
            except Exception as e:
                errors.append(f"Content validation failed for {file_path}: {str(e)}")
                score -= 25
        
        return {
            'score': max(0, score),
            'errors': errors,
            'warnings': warnings,
            'validated_at': datetime.now().isoformat()
        }
    
    def should_include_file_group(self, validation_result: Dict) -> bool:
        """Determine if file group should be included based on validation."""
        if validation_result['errors'] and self.strict_mode:
            return False
        
        min_score = self.validation_config.get('min_score', 50)
        return validation_result['score'] >= min_score
    
    def validate_json_file(self, file_path: Path):
        """Validate JSON file structure."""
        import json
        with open(file_path, 'r') as f:
            json.load(f)  # Will raise exception if invalid JSON
    
    def validate_image_file(self, file_path: Path):
        """Validate image file integrity."""
        from PIL import Image
        with Image.open(file_path) as img:
            img.verify()  # Will raise exception if corrupted
```

### Example 3: Batch Processing Plugin

```python
class BatchProcessingUploader(BaseUploader):
    """Processes files in configurable batches with progress tracking."""
    
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
        
        self.batch_size = extra_params.get('batch_size', 10)
        self.parallel_processing = extra_params.get('use_parallel', True)
        self.max_workers = extra_params.get('max_workers', 4)
    
    def organize_files(self, files: List) -> List:
        """Organize files into processing batches."""
        batches = []
        current_batch = []
        
        for file_group in files:
            current_batch.append(file_group)
            
            if len(current_batch) >= self.batch_size:
                batches.append({
                    'batch_id': len(batches) + 1,
                    'files': current_batch,
                    'batch_size': len(current_batch)
                })
                current_batch = []
        
        # Add remaining files as final batch
        if current_batch:
            batches.append({
                'batch_id': len(batches) + 1,
                'files': current_batch,
                'batch_size': len(current_batch)
            })
        
        self.run.log_message(f"Organized {len(files)} files into {len(batches)} batches")
        return batches
    
    def process_files(self, organized_files: List) -> List:
        """Process files in batches with progress tracking."""
        all_processed_files = []
        total_batches = len(organized_files)
        
        if self.parallel_processing:
            all_processed_files = self.process_batches_parallel(organized_files)
        else:
            all_processed_files = self.process_batches_sequential(organized_files)
        
        self.run.log_message(f"Completed processing {total_batches} batches")
        return all_processed_files
    
    def process_batches_sequential(self, batches: List) -> List:
        """Process batches sequentially."""
        all_files = []
        
        for i, batch in enumerate(batches, 1):
            self.run.log_message(f"Processing batch {i}/{len(batches)}")
            
            processed_batch = self.process_single_batch(batch)
            all_files.extend(processed_batch)
            
            # Update progress
            progress = (i / len(batches)) * 100
            self.run.log_message(f"Progress: {progress:.1f}% complete")
        
        return all_files
    
    def process_batches_parallel(self, batches: List) -> List:
        """Process batches in parallel using ThreadPoolExecutor."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        all_files = []
        completed_batches = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batches
            future_to_batch = {
                executor.submit(self.process_single_batch, batch): batch 
                for batch in batches
            }
            
            # Process completed batches
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    processed_files = future.result()
                    all_files.extend(processed_files)
                    completed_batches += 1
                    
                    progress = (completed_batches / len(batches)) * 100
                    self.run.log_message(f"Batch {batch['batch_id']} complete. Progress: {progress:.1f}%")
                    
                except Exception as e:
                    self.run.log_message(f"Batch {batch['batch_id']} failed: {str(e)}")
        
        return all_files
    
    def process_single_batch(self, batch: Dict) -> List:
        """Process a single batch of files."""
        batch_files = batch['files']
        processed_files = []
        
        for file_group in batch_files:
            # Apply your specific processing logic here
            processed_file = self.process_file_group(file_group)
            processed_files.append(processed_file)
        
        return processed_files
    
    def process_file_group(self, file_group: Dict) -> Dict:
        """Process individual file group - implement your logic here."""
        # Example: Add batch processing metadata
        file_group['batch_processed'] = True
        file_group['processed_timestamp'] = datetime.now().isoformat()
        return file_group
```

## Error Handling and Logging

### Comprehensive Error Handling

```python
class RobustUploader(BaseUploader):
    def process_files(self, organized_files: List) -> List:
        """Process files with comprehensive error handling."""
        processed_files = []
        failed_files = []
        
        for i, file_group in enumerate(organized_files):
            try:
                self.run.log_message(f"Processing file group {i+1}/{len(organized_files)}")
                
                # Process with validation
                processed_file = self.process_file_group_safely(file_group)
                processed_files.append(processed_file)
                
            except Exception as e:
                error_info = {
                    'file_group': file_group,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'timestamp': datetime.now().isoformat()
                }
                failed_files.append(error_info)
                
                self.run.log_message(f"Failed to process file group: {str(e)}")
                
                # Continue processing other files
                continue
        
        # Log summary
        self.run.log_message(
            f"Processing complete: {len(processed_files)} successful, {len(failed_files)} failed"
        )
        
        if failed_files:
            # Save error report
            self.save_error_report(failed_files)
        
        return processed_files
    
    def process_file_group_safely(self, file_group: Dict) -> Dict:
        """Process file group with validation and error checking."""
        # Validate file group structure
        if 'files' not in file_group:
            raise ValueError("File group missing 'files' key")
        
        files_dict = file_group['files']
        if not files_dict:
            raise ValueError("File group has no files")
        
        # Validate file accessibility
        for spec_name, file_path in files_dict.items():
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"Cannot read file: {file_path}")
        
        # Perform actual processing
        return self.apply_processing_logic(file_group)
    
    def save_error_report(self, failed_files: List):
        """Save detailed error report for debugging."""
        error_report_path = self.path / 'error_report.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'plugin_name': self.__class__.__name__,
            'total_errors': len(failed_files),
            'errors': failed_files
        }
        
        with open(error_report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.run.log_message(f"Error report saved to: {error_report_path}")
```

### Structured Logging

```python
class LoggingUploader(BaseUploader):
    def setup_directories(self):
        """Setup logging directory."""
        log_dir = self.path / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Initialize structured logging
        self.setup_structured_logging(log_dir)
    
    def setup_structured_logging(self, log_dir: Path):
        """Setup structured logging with different levels."""
        import logging
        import json
        
        # Create custom formatter for structured logs
        class StructuredFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'plugin': 'LoggingUploader'
                }
                
                # Add extra fields if present
                if hasattr(record, 'file_path'):
                    log_entry['file_path'] = str(record.file_path)
                if hasattr(record, 'operation'):
                    log_entry['operation'] = record.operation
                if hasattr(record, 'duration'):
                    log_entry['duration'] = record.duration
                
                return json.dumps(log_entry)
        
        # Setup logger
        self.logger = logging.getLogger('upload_plugin')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        handler = logging.FileHandler(log_dir / 'plugin.log')
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
    
    def process_files(self, organized_files: List) -> List:
        """Process files with detailed logging."""
        start_time = time.time()
        
        self.logger.info(
            f"Starting file processing",
            extra={'operation': 'process_files', 'file_count': len(organized_files)}
        )
        
        processed_files = []
        
        for i, file_group in enumerate(organized_files):
            file_start_time = time.time()
            
            try:
                # Process file group
                processed_file = self.process_file_group(file_group)
                processed_files.append(processed_file)
                
                # Log success
                duration = time.time() - file_start_time
                self.logger.info(
                    f"Successfully processed file group {i+1}",
                    extra={
                        'operation': 'process_file_group',
                        'file_group_index': i,
                        'duration': duration
                    }
                )
                
            except Exception as e:
                # Log error
                duration = time.time() - file_start_time
                self.logger.error(
                    f"Failed to process file group {i+1}: {str(e)}",
                    extra={
                        'operation': 'process_file_group',
                        'file_group_index': i,
                        'duration': duration,
                        'error': str(e)
                    }
                )
                raise
        
        # Log overall completion
        total_duration = time.time() - start_time
        self.logger.info(
            f"Completed file processing",
            extra={
                'operation': 'process_files',
                'total_duration': total_duration,
                'processed_count': len(processed_files)
            }
        )
        
        return processed_files
```

## Performance Optimization

### Memory Management

```python
class MemoryEfficientUploader(BaseUploader):
    """Uploader optimized for large file processing."""
    
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
        
        self.chunk_size = extra_params.get('chunk_size', 8192)  # 8KB chunks
        self.memory_limit = extra_params.get('memory_limit_mb', 100) * 1024 * 1024
    
    def process_files(self, organized_files: List) -> List:
        """Process files with memory management."""
        import psutil
        import gc
        
        processed_files = []
        
        for file_group in organized_files:
            # Check memory usage before processing
            memory_usage = psutil.Process().memory_info().rss
            
            if memory_usage > self.memory_limit:
                self.run.log_message(f"High memory usage: {memory_usage / 1024 / 1024:.1f}MB")
                
                # Force garbage collection
                gc.collect()
                
                # Check again after cleanup
                memory_usage = psutil.Process().memory_info().rss
                if memory_usage > self.memory_limit:
                    self.run.log_message("Memory limit exceeded, processing in smaller chunks")
                    processed_file = self.process_file_group_chunked(file_group)
                else:
                    processed_file = self.process_file_group_normal(file_group)
            else:
                processed_file = self.process_file_group_normal(file_group)
            
            processed_files.append(processed_file)
        
        return processed_files
    
    def process_file_group_chunked(self, file_group: Dict) -> Dict:
        """Process large files in chunks to manage memory."""
        files_dict = file_group.get('files', {})
        processed_files = {}
        
        for spec_name, file_path in files_dict.items():
            if file_path.stat().st_size > 50 * 1024 * 1024:  # 50MB
                # Process large files in chunks
                processed_path = self.process_large_file_chunked(file_path)
                processed_files[spec_name] = processed_path
            else:
                # Process smaller files normally
                processed_files[spec_name] = file_path
        
        file_group['files'] = processed_files
        return file_group
    
    def process_large_file_chunked(self, file_path: Path) -> Path:
        """Process large file in chunks."""
        output_path = self.path / 'processed' / file_path.name
        
        with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            while True:
                chunk = infile.read(self.chunk_size)
                if not chunk:
                    break
                
                # Apply processing to chunk
                processed_chunk = self.process_chunk(chunk)
                outfile.write(processed_chunk)
        
        return output_path
    
    def process_chunk(self, chunk: bytes) -> bytes:
        """Process individual chunk - override with your logic."""
        # Example: Simple pass-through
        return chunk
```

### Async Processing

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

class AsyncUploader(BaseUploader):
    """Uploader with asynchronous processing capabilities."""
    
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
        
        self.max_concurrent = extra_params.get('max_concurrent', 5)
        self.use_process_pool = extra_params.get('use_process_pool', False)
    
    def process_files(self, organized_files: List) -> List:
        """Process files asynchronously."""
        # Run async processing in sync context
        return asyncio.run(self._process_files_async(organized_files))
    
    async def _process_files_async(self, organized_files: List) -> List:
        """Main async processing method."""
        if self.use_process_pool:
            return await self._process_with_process_pool(organized_files)
        else:
            return await self._process_with_async_tasks(organized_files)
    
    async def _process_with_async_tasks(self, organized_files: List) -> List:
        """Process using async tasks with concurrency limit."""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_with_semaphore(file_group):
            async with semaphore:
                return await self._process_file_group_async(file_group)
        
        # Create tasks for all file groups
        tasks = [
            process_with_semaphore(file_group) 
            for file_group in organized_files
        ]
        
        # Wait for all tasks to complete
        processed_files = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        valid_files = []
        for i, result in enumerate(processed_files):
            if isinstance(result, Exception):
                self.run.log_message(f"Error processing file group {i}: {str(result)}")
            else:
                valid_files.append(result)
        
        return valid_files
    
    async def _process_with_process_pool(self, organized_files: List) -> List:
        """Process using process pool for CPU-intensive tasks."""
        loop = asyncio.get_event_loop()
        
        with ProcessPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit all tasks to process pool
            futures = [
                loop.run_in_executor(executor, self._process_file_group_sync, file_group)
                for file_group in organized_files
            ]
            
            # Wait for completion
            processed_files = await asyncio.gather(*futures, return_exceptions=True)
            
            # Filter exceptions
            valid_files = []
            for i, result in enumerate(processed_files):
                if isinstance(result, Exception):
                    self.run.log_message(f"Error in process pool for file group {i}: {str(result)}")
                else:
                    valid_files.append(result)
            
            return valid_files
    
    async def _process_file_group_async(self, file_group: Dict) -> Dict:
        """Async processing of individual file group."""
        # Simulate async I/O operation
        await asyncio.sleep(0.1)
        
        # Apply your processing logic here
        file_group['async_processed'] = True
        file_group['processed_timestamp'] = datetime.now().isoformat()
        
        return file_group
    
    def _process_file_group_sync(self, file_group: Dict) -> Dict:
        """Synchronous processing for process pool."""
        # This runs in a separate process
        import time
        time.sleep(0.1)  # Simulate CPU work
        
        file_group['process_pool_processed'] = True
        file_group['processed_timestamp'] = datetime.now().isoformat()
        
        return file_group
```

## Testing and Debugging

### Unit Testing Framework

```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

class TestMyUploader(unittest.TestCase):
    """Test suite for custom uploader."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Mock run object
        self.mock_run = Mock()
        self.mock_run.log_message = Mock()
        
        # Sample file specification
        self.file_specification = [
            {'name': 'image_data', 'file_type': 'image'},
            {'name': 'text_data', 'file_type': 'text'}
        ]
        
        # Create test files
        self.test_files = self.create_test_files()
        
        # Sample organized files
        self.organized_files = [
            {
                'files': {
                    'image_data': self.test_files['image'],
                    'text_data': self.test_files['text']
                },
                'metadata': {'group_id': 1}
            }
        ]
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_files(self) -> Dict[str, Path]:
        """Create test files for testing."""
        files = {}
        
        # Create test image file
        image_file = self.temp_dir / 'test_image.jpg'
        with open(image_file, 'wb') as f:
            f.write(b'fake_image_data')
        files['image'] = image_file
        
        # Create test text file
        text_file = self.temp_dir / 'test_text.txt'
        with open(text_file, 'w') as f:
            f.write('test content')
        files['text'] = text_file
        
        return files
    
    def test_initialization(self):
        """Test uploader initialization."""
        uploader = MyUploader(
            run=self.mock_run,
            path=self.temp_dir,
            file_specification=self.file_specification,
            organized_files=self.organized_files
        )
        
        self.assertEqual(uploader.path, self.temp_dir)
        self.assertEqual(uploader.file_specification, self.file_specification)
        self.assertEqual(uploader.organized_files, self.organized_files)
    
    def test_process_files(self):
        """Test process_files method."""
        uploader = MyUploader(
            run=self.mock_run,
            path=self.temp_dir,
            file_specification=self.file_specification,
            organized_files=self.organized_files
        )
        
        result = uploader.process_files(self.organized_files)
        
        # Verify result structure
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        
        # Verify processing occurred
        processed_file = result[0]
        self.assertIn('processed_by', processed_file)
        self.assertEqual(processed_file['processed_by'], 'MyUploader')
    
    def test_handle_upload_files_workflow(self):
        """Test complete workflow."""
        uploader = MyUploader(
            run=self.mock_run,
            path=self.temp_dir,
            file_specification=self.file_specification,
            organized_files=self.organized_files
        )
        
        # Mock workflow methods
        with patch.object(uploader, 'setup_directories') as mock_setup, \
             patch.object(uploader, 'organize_files', return_value=self.organized_files) as mock_organize, \
             patch.object(uploader, 'before_process', return_value=self.organized_files) as mock_before, \
             patch.object(uploader, 'process_files', return_value=self.organized_files) as mock_process, \
             patch.object(uploader, 'after_process', return_value=self.organized_files) as mock_after, \
             patch.object(uploader, 'validate_files', return_value=self.organized_files) as mock_validate:
            
            result = uploader.handle_upload_files()
            
            # Verify all methods were called in correct order
            mock_setup.assert_called_once()
            mock_organize.assert_called_once()
            mock_before.assert_called_once()
            mock_process.assert_called_once()
            mock_after.assert_called_once()
            mock_validate.assert_called_once()
            
            self.assertEqual(result, self.organized_files)
    
    def test_error_handling(self):
        """Test error handling in process_files."""
        uploader = MyUploader(
            run=self.mock_run,
            path=self.temp_dir,
            file_specification=self.file_specification,
            organized_files=self.organized_files
        )
        
        # Test with invalid file group
        invalid_files = [{'invalid': 'structure'}]
        
        with self.assertRaises(Exception):
            uploader.process_files(invalid_files)
    
    @patch('your_module.some_external_dependency')
    def test_external_dependencies(self, mock_dependency):
        """Test integration with external dependencies."""
        mock_dependency.return_value = 'mocked_result'
        
        uploader = MyUploader(
            run=self.mock_run,
            path=self.temp_dir,
            file_specification=self.file_specification,
            organized_files=self.organized_files
        )
        
        # Test method that uses external dependency
        result = uploader.some_method_using_dependency()
        
        mock_dependency.assert_called_once()
        self.assertEqual(result, 'expected_result_based_on_mock')

if __name__ == '__main__':
    # Run specific test
    unittest.main()
```

### Integration Testing

```python
class TestUploaderIntegration(unittest.TestCase):
    """Integration tests for uploader with real file operations."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_run = Mock()
        
        # Create realistic test files
        self.create_realistic_test_files()
    
    def create_realistic_test_files(self):
        """Create realistic test files for integration testing."""
        # Create various file types
        (self.temp_dir / 'images').mkdir()
        (self.temp_dir / 'data').mkdir()
        
        # TIFF image that can be actually processed
        tiff_path = self.temp_dir / 'images' / 'test.tif'
        # Create a minimal valid TIFF file
        self.create_minimal_tiff(tiff_path)
        
        # JSON data file
        json_path = self.temp_dir / 'data' / 'test.json'
        with open(json_path, 'w') as f:
            json.dump({'test': 'data', 'values': [1, 2, 3]}, f)
        
        self.test_files = {
            'image_file': tiff_path,
            'data_file': json_path
        }
    
    def create_minimal_tiff(self, path: Path):
        """Create a minimal valid TIFF file for testing."""
        try:
            from PIL import Image
            import numpy as np
            
            # Create a small test image
            array = np.zeros((50, 50, 3), dtype=np.uint8)
            array[10:40, 10:40] = [255, 0, 0]  # Red square
            
            image = Image.fromarray(array)
            image.save(path, 'TIFF')
        except ImportError:
            # Fallback: create empty file if PIL not available
            path.touch()
    
    def test_full_workflow_with_real_files(self):
        """Test complete workflow with real file operations."""
        file_specification = [
            {'name': 'test_image', 'file_type': 'image'},
            {'name': 'test_data', 'file_type': 'data'}
        ]
        
        organized_files = [
            {
                'files': {
                    'test_image': self.test_files['image_file'],
                    'test_data': self.test_files['data_file']
                }
            }
        ]
        
        uploader = ImageProcessingUploader(
            run=self.mock_run,
            path=self.temp_dir,
            file_specification=file_specification,
            organized_files=organized_files
        )
        
        # Run complete workflow
        result = uploader.handle_upload_files()
        
        # Verify results
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        
        # Check if processing directories were created
        self.assertTrue((self.temp_dir / 'processed').exists())
        self.assertTrue((self.temp_dir / 'thumbnails').exists())
        
        # Verify logging calls
        self.assertTrue(self.mock_run.log_message.called)
```

### Debugging Utilities

```python
class DebuggingUploader(BaseUploader):
    """Uploader with enhanced debugging capabilities."""
    
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
        
        self.debug_mode = extra_params.get('debug_mode', False)
        self.debug_dir = self.path / 'debug'
        
        if self.debug_mode:
            self.debug_dir.mkdir(exist_ok=True)
            self.setup_debugging()
    
    def setup_debugging(self):
        """Initialize debugging infrastructure."""
        import json
        
        # Save initialization state
        init_state = {
            'path': str(self.path),
            'file_specification': self.file_specification,
            'organized_files_count': len(self.organized_files),
            'extra_params': self.extra_params,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.debug_dir / 'init_state.json', 'w') as f:
            json.dump(init_state, f, indent=2, default=str)
    
    def debug_log(self, message: str, data: Any = None):
        """Enhanced debug logging."""
        if not self.debug_mode:
            return
        
        debug_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'data': data
        }
        
        # Write to debug log
        debug_log_path = self.debug_dir / 'debug.log'
        with open(debug_log_path, 'a') as f:
            f.write(json.dumps(debug_entry, default=str) + '\n')
        
        # Also log to main run
        self.run.log_message(f"DEBUG: {message}")
    
    def setup_directories(self):
        """Setup directories with debugging."""
        self.debug_log("Setting up directories")
        super().setup_directories()
        
        if self.debug_mode:
            # Save directory state
            dirs_state = {
                'existing_dirs': [str(p) for p in self.path.iterdir() if p.is_dir()],
                'path_exists': self.path.exists(),
                'path_writable': os.access(self.path, os.W_OK)
            }
            self.debug_log("Directory setup complete", dirs_state)
    
    def process_files(self, organized_files: List) -> List:
        """Process files with debugging instrumentation."""
        self.debug_log(f"Starting process_files with {len(organized_files)} file groups")
        
        # Save input state
        if self.debug_mode:
            with open(self.debug_dir / 'input_files.json', 'w') as f:
                json.dump(organized_files, f, indent=2, default=str)
        
        processed_files = []
        
        for i, file_group in enumerate(organized_files):
            self.debug_log(f"Processing file group {i+1}")
            
            try:
                # Process with timing
                start_time = time.time()
                processed_file = self.process_file_group_with_debug(file_group, i)
                duration = time.time() - start_time
                
                processed_files.append(processed_file)
                self.debug_log(f"File group {i+1} processed successfully", {'duration': duration})
                
            except Exception as e:
                error_data = {
                    'file_group_index': i,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'file_group': file_group
                }
                self.debug_log(f"Error processing file group {i+1}", error_data)
                
                # Save error state
                if self.debug_mode:
                    with open(self.debug_dir / f'error_group_{i}.json', 'w') as f:
                        json.dump(error_data, f, indent=2, default=str)
                
                raise
        
        # Save output state
        if self.debug_mode:
            with open(self.debug_dir / 'output_files.json', 'w') as f:
                json.dump(processed_files, f, indent=2, default=str)
        
        self.debug_log(f"process_files completed with {len(processed_files)} processed files")
        return processed_files
    
    def process_file_group_with_debug(self, file_group: Dict, index: int) -> Dict:
        """Process individual file group with debugging."""
        if self.debug_mode:
            # Save intermediate state
            with open(self.debug_dir / f'group_{index}_input.json', 'w') as f:
                json.dump(file_group, f, indent=2, default=str)
        
        # Apply your processing logic
        processed_group = self.apply_custom_processing(file_group)
        
        if self.debug_mode:
            # Save result state
            with open(self.debug_dir / f'group_{index}_output.json', 'w') as f:
                json.dump(processed_group, f, indent=2, default=str)
        
        return processed_group
    
    def apply_custom_processing(self, file_group: Dict) -> Dict:
        """Your custom processing logic - implement as needed."""
        # Example implementation
        file_group['debug_processed'] = True
        file_group['processing_timestamp'] = datetime.now().isoformat()
        return file_group
    
    def generate_debug_report(self):
        """Generate comprehensive debug report."""
        if not self.debug_mode:
            return
        
        report = {
            'plugin_name': self.__class__.__name__,
            'debug_session': datetime.now().isoformat(),
            'files_processed': 0,
            'errors': [],
            'performance': {}
        }
        
        # Analyze debug files
        for debug_file in self.debug_dir.glob('*.json'):
            if debug_file.name.startswith('error_'):
                with open(debug_file) as f:
                    error_data = json.load(f)
                    report['errors'].append(error_data)
            elif debug_file.name == 'output_files.json':
                with open(debug_file) as f:
                    output_data = json.load(f)
                    report['files_processed'] = len(output_data)
        
        # Save final report
        with open(self.debug_dir / 'debug_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.run.log_message(f"Debug report generated at: {self.debug_dir / 'debug_report.json'}")
```

## Best Practices Summary

### 1. Code Organization
- Keep `process_files()` focused on core logic
- Use hook methods for setup, cleanup, and validation
- Separate concerns using helper methods
- Follow single responsibility principle

### 2. Error Handling
- Implement comprehensive error handling
- Log errors with context information
- Fail gracefully when possible
- Provide meaningful error messages

### 3. Performance
- Profile your processing logic
- Use appropriate data structures
- Consider memory usage for large files
- Implement async processing for I/O-heavy operations

### 4. Testing
- Write unit tests for all methods
- Include integration tests with real files
- Test error conditions and edge cases
- Use mocking for external dependencies

### 5. Logging
- Log important operations and milestones
- Include timing information for performance analysis
- Use structured logging for better analysis
- Provide different log levels (info, warning, error)

### 6. Configuration
- Use `extra_params` for plugin configuration
- Provide sensible defaults
- Validate configuration parameters
- Document all configuration options

### 7. Documentation
- Document all methods with clear docstrings
- Provide usage examples
- Document configuration options
- Include troubleshooting information

This comprehensive guide should help you develop robust, efficient, and maintainable upload plugins using the BaseUploader template. Remember to adapt the examples to your specific use case and requirements.