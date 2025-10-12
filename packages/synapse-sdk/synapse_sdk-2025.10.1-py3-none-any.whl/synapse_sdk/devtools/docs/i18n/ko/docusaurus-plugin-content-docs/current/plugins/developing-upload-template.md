# BaseUploader로 업로드 템플릿 개발하기

이 가이드는 BaseUploader 템플릿 클래스를 사용하여 커스텀 업로드 플러그인을 만들고자 하는 플러그인 개발자를 위한 포괄적인 문서를 제공합니다. BaseUploader는 템플릿 메소드 패턴을 따라 파일 처리 워크플로우를 위한 구조화되고 확장 가능한 기반을 제공합니다.

## 빠른 시작

### 기본 플러그인 구조

BaseUploader를 상속하여 업로드 플러그인을 생성하세요:

```python
from pathlib import Path
from typing import List, Dict, Any
from . import BaseUploader

class MyUploader(BaseUploader):
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
    
    def process_files(self, organized_files: List) -> List:
        """여기에 커스텀 파일 처리 로직을 구현하세요."""
        # 처리 로직이 여기에 들어갑니다
        return organized_files
    
    def handle_upload_files(self) -> List[Dict[str, Any]]:
        """업로드 액션에서 호출되는 주요 진입점."""
        return super().handle_upload_files()
```

### 최소 동작 예제

```python
class SimpleUploader(BaseUploader):
    def process_files(self, organized_files: List) -> List:
        """각 파일 그룹에 메타데이터 추가."""
        for file_group in organized_files:
            file_group['processed_by'] = 'SimpleUploader'
            file_group['processing_timestamp'] = datetime.now().isoformat()
        return organized_files
```

## 아키텍처 심층 분석

### 워크플로우 파이프라인

BaseUploader는 포괄적인 6단계 워크플로우 파이프라인을 구현합니다:

```
1. setup_directories()    # 디렉토리 구조 초기화
2. organize_files()       # 파일 그룹화 및 구조화
3. before_process()       # 전처리 훅
4. process_files()        # 주요 처리 로직 (필수)
5. after_process()        # 후처리 훅
6. validate_files()       # 최종 검증 및 필터링
```

### 템플릿 메소드 패턴

BaseUploader는 다음과 같은 템플릿 메소드 패턴을 사용합니다:
- **구체적 메소드**: 대부분의 경우에 작동하는 기본 동작 제공
- **훅 메소드**: 특정 지점에서 커스터마이제이션 허용
- **추상 메소드**: 서브클래스에서 반드시 구현해야 함

## 핵심 메소드 참조

### 필수 메소드

#### `process_files(organized_files: List) -> List`

**목적**: 플러그인의 로직에 따라 파일을 변환하는 주요 처리 메소드.

**사용 시기**: 항상 - 모든 플러그인이 반드시 구현해야 하는 핵심 메소드입니다.

**매개변수**:
- `organized_files`: 구성된 파일 데이터를 포함하는 파일 그룹 딕셔너리 목록

**반환값**: 업로드 준비가 완료된 처리된 파일 그룹 목록

**예제**:
```python
def process_files(self, organized_files: List) -> List:
    """TIFF 이미지를 JPEG 형식으로 변환."""
    processed_files = []
    
    for file_group in organized_files:
        files_dict = file_group.get('files', {})
        converted_files = {}
        
        for spec_name, file_path in files_dict.items():
            if file_path.suffix.lower() in ['.tif', '.tiff']:
                # TIFF를 JPEG로 변환
                jpeg_path = self.convert_tiff_to_jpeg(file_path)
                converted_files[spec_name] = jpeg_path
                self.run.log_message(f"{file_path}를 {jpeg_path}로 변환했습니다")
            else:
                converted_files[spec_name] = file_path
        
        file_group['files'] = converted_files
        processed_files.append(file_group)
    
    return processed_files
```

### 선택적 훅 메소드

#### `setup_directories() -> None`

**목적**: 처리 시작 전에 커스텀 디렉토리 구조를 생성.

**사용 시기**: 플러그인이 처리, 임시 파일 또는 출력을 위한 특정 디렉토리가 필요할 때.

**예제**:
```python
def setup_directories(self):
    """처리 디렉토리 생성."""
    (self.path / 'temp').mkdir(exist_ok=True)
    (self.path / 'processed').mkdir(exist_ok=True)
    (self.path / 'thumbnails').mkdir(exist_ok=True)
    self.run.log_message("처리 디렉토리를 생성했습니다")
```

#### `organize_files(files: List) -> List`

**목적**: 주요 처리 전에 파일을 재구성하고 구조화.

**사용 시기**: 파일을 다르게 그룹화하거나, 기준에 따라 필터링하거나, 데이터를 재구조화해야 할 때.

**예제**:
```python
def organize_files(self, files: List) -> List:
    """타입과 크기별로 파일 그룹화."""
    large_files = []
    small_files = []
    
    for file_group in files:
        total_size = sum(f.stat().st_size for f in file_group.get('files', {}).values())
        if total_size > 100 * 1024 * 1024:  # 100MB
            large_files.append(file_group)
        else:
            small_files.append(file_group)
    
    # 큰 파일을 먼저 처리
    return large_files + small_files
```

#### `before_process(organized_files: List) -> List`

**목적**: 주요 처리 전 설정 작업을 위한 전처리 훅.

**사용 시기**: 검증, 준비 또는 초기화 작업에 사용.

**예제**:
```python
def before_process(self, organized_files: List) -> List:
    """처리를 위한 파일 검증 및 준비."""
    self.run.log_message(f"{len(organized_files)}개 파일 그룹 처리 시작")
    
    # 사용 가능한 디스크 공간 확인
    if not self.check_disk_space(organized_files):
        raise Exception("처리를 위한 디스크 공간이 부족합니다")
    
    # 처리 리소스 초기화
    self.processing_queue = Queue()
    return organized_files
```

#### `after_process(processed_files: List) -> List`

**목적**: 정리 및 완료를 위한 후처리 훅.

**사용 시기**: 정리, 최종 변환 또는 리소스 해제에 사용.

**예제**:
```python
def after_process(self, processed_files: List) -> List:
    """임시 파일 정리 및 요약 생성."""
    # 임시 파일 제거
    temp_dir = self.path / 'temp'
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    # 처리 요약 생성
    summary = {
        'total_processed': len(processed_files),
        'processing_time': time.time() - self.start_time,
        'plugin_version': '1.0.0'
    }
    
    self.run.log_message(f"처리 완료: {summary}")
    return processed_files
```

#### `validate_files(files: List) -> List`

**목적**: 타입 검사를 넘어선 커스텀 검증 로직.

**사용 시기**: 내장된 파일 타입 검증 외에 추가적인 검증 규칙이 필요할 때.

**예제**:
```python
def validate_files(self, files: List) -> List:
    """크기 및 형식 검사를 포함한 커스텀 검증."""
    # 먼저 내장 타입 검증 적용
    validated_files = self.validate_file_types(files)
    
    # 그 다음 커스텀 검증 적용
    final_files = []
    for file_group in validated_files:
        if self.validate_file_group(file_group):
            final_files.append(file_group)
        else:
            self.run.log_message(f"커스텀 검증 실패한 파일 그룹: {file_group}")
    
    return final_files

def validate_file_group(self, file_group: Dict) -> bool:
    """개별 파일 그룹에 대한 커스텀 검증."""
    files_dict = file_group.get('files', {})
    
    for spec_name, file_path in files_dict.items():
        # 파일 크기 제한 확인
        if file_path.stat().st_size > 500 * 1024 * 1024:  # 500MB 제한
            return False
        
        # 파일 접근 가능성 확인
        if not os.access(file_path, os.R_OK):
            return False
    
    return True
```

## 고급 기능

### 파일 타입 검증 시스템

BaseUploader는 커스터마이즈할 수 있는 정교한 검증 시스템을 포함합니다:

#### 기본 파일 확장자

```python
def get_file_extensions_config(self) -> Dict[str, List[str]]:
    """허용된 파일 확장자를 커스터마이즈하려면 오버라이드하세요."""
    return {
        'pcd': ['.pcd'],
        'text': ['.txt', '.html'],
        'audio': ['.wav', '.mp3'],
        'data': ['.bin', '.json', '.fbx'],
        'image': ['.jpg', '.jpeg', '.png'],
        'video': ['.mp4'],
    }
```

#### 커스텀 확장자 구성

```python
class CustomUploader(BaseUploader):
    def get_file_extensions_config(self) -> Dict[str, List[str]]:
        """추가 형식 지원 추가."""
        config = super().get_file_extensions_config()
        config.update({
            'cad': ['.dwg', '.dxf', '.step'],
            'archive': ['.zip', '.rar', '.7z'],
            'document': ['.pdf', '.docx', '.xlsx']
        })
        return config
```

#### 변환 경고

```python
def get_conversion_warnings_config(self) -> Dict[str, str]:
    """변환 경고를 커스터마이즈하려면 오버라이드하세요."""
    return {
        '.tif': ' .jpg, .png',
        '.tiff': ' .jpg, .png',
        '.avi': ' .mp4',
        '.mov': ' .mp4',
        '.raw': ' .jpg, .png',
        '.bmp': ' .jpg, .png',
    }
```

### 커스텀 필터링

세밀한 제어를 위해 `filter_files` 메소드를 구현하세요:

```python
def filter_files(self, organized_file: Dict[str, Any]) -> bool:
    """커스텀 필터링 로직."""
    # 파일 크기별 필터링
    files_dict = organized_file.get('files', {})
    total_size = sum(f.stat().st_size for f in files_dict.values())
    
    if total_size < 1024:  # 1KB보다 작은 파일 건너뛰기
        self.run.log_message(f"작은 파일 그룹 건너뛰기: {total_size} bytes")
        return False
    
    # 파일 나이별 필터링
    oldest_file = min(files_dict.values(), key=lambda f: f.stat().st_mtime)
    age_days = (time.time() - oldest_file.stat().st_mtime) / 86400
    
    if age_days > 365:  # 1년보다 오래된 파일 건너뛰기
        self.run.log_message(f"오래된 파일 그룹 건너뛰기: {age_days}일 전")
        return False
    
    return True
```

## 실제 사용 예제

### 예제 1: 이미지 처리 플러그인

```python
class ImageProcessingUploader(BaseUploader):
    """TIFF 이미지를 JPEG로 변환하고 썸네일을 생성."""
    
    def setup_directories(self):
        """처리된 이미지와 썸네일을 위한 디렉토리 생성."""
        (self.path / 'processed').mkdir(exist_ok=True)
        (self.path / 'thumbnails').mkdir(exist_ok=True)
    
    def organize_files(self, files: List) -> List:
        """원본과 처리된 이미지 분리."""
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
        
        # 원본 이미지를 먼저 처리
        return raw_images + processed_images
    
    def process_files(self, organized_files: List) -> List:
        """이미지 변환 및 썸네일 생성."""
        processed_files = []
        
        for file_group in organized_files:
            files_dict = file_group.get('files', {})
            converted_files = {}
            
            for spec_name, file_path in files_dict.items():
                if file_path.suffix.lower() in ['.tif', '.tiff']:
                    # JPEG로 변환
                    jpeg_path = self.convert_to_jpeg(file_path)
                    converted_files[spec_name] = jpeg_path
                    
                    # 썸네일 생성
                    thumbnail_path = self.generate_thumbnail(jpeg_path)
                    converted_files[f"{spec_name}_thumbnail"] = thumbnail_path
                    
                    self.run.log_message(f"{file_path.name} -> {jpeg_path.name}로 처리했습니다")
                else:
                    converted_files[spec_name] = file_path
            
            file_group['files'] = converted_files
            processed_files.append(file_group)
        
        return processed_files
    
    def convert_to_jpeg(self, tiff_path: Path) -> Path:
        """PIL을 사용하여 TIFF를 JPEG로 변환."""
        from PIL import Image
        
        output_path = self.path / 'processed' / f"{tiff_path.stem}.jpg"
        
        with Image.open(tiff_path) as img:
            # 필요시 RGB로 변환
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            img.save(output_path, 'JPEG', quality=95)
        
        return output_path
    
    def generate_thumbnail(self, image_path: Path) -> Path:
        """처리된 이미지의 썸네일 생성."""
        from PIL import Image
        
        thumbnail_path = self.path / 'thumbnails' / f"{image_path.stem}_thumb.jpg"
        
        with Image.open(image_path) as img:
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=85)
        
        return thumbnail_path
```

### 예제 2: 데이터 검증 플러그인

```python
class DataValidationUploader(BaseUploader):
    """데이터 파일을 검증하고 품질 보고서를 생성."""
    
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
        
        # extra_params에서 검증 구성 초기화
        self.validation_config = extra_params.get('validation_config', {})
        self.strict_mode = extra_params.get('strict_validation', False)
    
    def before_process(self, organized_files: List) -> List:
        """검증 엔진 초기화."""
        self.validation_results = []
        self.run.log_message(f"{len(organized_files)}개 파일 그룹 검증 시작")
        return organized_files
    
    def process_files(self, organized_files: List) -> List:
        """파일 검증 및 품질 보고서 생성."""
        processed_files = []
        
        for file_group in organized_files:
            validation_result = self.validate_file_group(file_group)
            
            # 검증 메타데이터 추가
            file_group['validation'] = validation_result
            file_group['quality_score'] = validation_result['score']
            
            # 검증 결과에 따라 파일 그룹 포함
            if self.should_include_file_group(validation_result):
                processed_files.append(file_group)
                self.run.log_message(f"파일 그룹 검증 통과: {validation_result['score']}")
            else:
                self.run.log_message(f"파일 그룹 검증 실패: {validation_result['errors']}")
        
        return processed_files
    
    def validate_file_group(self, file_group: Dict) -> Dict:
        """파일 그룹의 포괄적인 검증."""
        files_dict = file_group.get('files', {})
        errors = []
        warnings = []
        score = 100
        
        for spec_name, file_path in files_dict.items():
            # 파일 존재 및 접근 가능성
            if not file_path.exists():
                errors.append(f"파일을 찾을 수 없음: {file_path}")
                score -= 50
                continue
            
            if not os.access(file_path, os.R_OK):
                errors.append(f"파일을 읽을 수 없음: {file_path}")
                score -= 30
                continue
            
            # 파일 크기 검증
            file_size = file_path.stat().st_size
            if file_size == 0:
                errors.append(f"빈 파일: {file_path}")
                score -= 40
            elif file_size > 1024 * 1024 * 1024:  # 1GB
                warnings.append(f"큰 파일: {file_path} ({file_size} bytes)")
                score -= 10
            
            # 확장자에 따른 내용 검증
            try:
                if file_path.suffix.lower() == '.json':
                    self.validate_json_file(file_path)
                elif file_path.suffix.lower() in ['.jpg', '.png']:
                    self.validate_image_file(file_path)
                # 필요에 따라 더 많은 내용 검증 추가
            except Exception as e:
                errors.append(f"{file_path}의 내용 검증 실패: {str(e)}")
                score -= 25
        
        return {
            'score': max(0, score),
            'errors': errors,
            'warnings': warnings,
            'validated_at': datetime.now().isoformat()
        }
    
    def should_include_file_group(self, validation_result: Dict) -> bool:
        """검증 결과를 기반으로 파일 그룹 포함 여부 결정."""
        if validation_result['errors'] and self.strict_mode:
            return False
        
        min_score = self.validation_config.get('min_score', 50)
        return validation_result['score'] >= min_score
    
    def validate_json_file(self, file_path: Path):
        """JSON 파일 구조 검증."""
        import json
        with open(file_path, 'r') as f:
            json.load(f)  # 유효하지 않은 JSON이면 예외 발생
    
    def validate_image_file(self, file_path: Path):
        """이미지 파일 무결성 검증."""
        from PIL import Image
        with Image.open(file_path) as img:
            img.verify()  # 손상된 경우 예외 발생
```

### 예제 3: 배치 처리 플러그인

```python
class BatchProcessingUploader(BaseUploader):
    """진행 상황 추적과 함께 구성 가능한 배치로 파일을 처리."""
    
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
        
        self.batch_size = extra_params.get('batch_size', 10)
        self.parallel_processing = extra_params.get('use_parallel', True)
        self.max_workers = extra_params.get('max_workers', 4)
    
    def organize_files(self, files: List) -> List:
        """파일을 처리 배치로 구성."""
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
        
        # 남은 파일을 최종 배치로 추가
        if current_batch:
            batches.append({
                'batch_id': len(batches) + 1,
                'files': current_batch,
                'batch_size': len(current_batch)
            })
        
        self.run.log_message(f"{len(files)}개 파일을 {len(batches)}개 배치로 구성했습니다")
        return batches
    
    def process_files(self, organized_files: List) -> List:
        """진행 상황 추적과 함께 배치로 파일 처리."""
        all_processed_files = []
        total_batches = len(organized_files)
        
        if self.parallel_processing:
            all_processed_files = self.process_batches_parallel(organized_files)
        else:
            all_processed_files = self.process_batches_sequential(organized_files)
        
        self.run.log_message(f"{total_batches}개 배치 처리 완료")
        return all_processed_files
    
    def process_batches_sequential(self, batches: List) -> List:
        """배치를 순차적으로 처리."""
        all_files = []
        
        for i, batch in enumerate(batches, 1):
            self.run.log_message(f"배치 {i}/{len(batches)} 처리 중")
            
            processed_batch = self.process_single_batch(batch)
            all_files.extend(processed_batch)
            
            # 진행 상황 업데이트
            progress = (i / len(batches)) * 100
            self.run.log_message(f"진행 상황: {progress:.1f}% 완료")
        
        return all_files
    
    def process_batches_parallel(self, batches: List) -> List:
        """ThreadPoolExecutor를 사용하여 배치를 병렬로 처리."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        all_files = []
        completed_batches = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 모든 배치 제출
            future_to_batch = {
                executor.submit(self.process_single_batch, batch): batch 
                for batch in batches
            }
            
            # 완료된 배치 처리
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    processed_files = future.result()
                    all_files.extend(processed_files)
                    completed_batches += 1
                    
                    progress = (completed_batches / len(batches)) * 100
                    self.run.log_message(f"배치 {batch['batch_id']} 완료. 진행 상황: {progress:.1f}%")
                    
                except Exception as e:
                    self.run.log_message(f"배치 {batch['batch_id']} 실패: {str(e)}")
        
        return all_files
    
    def process_single_batch(self, batch: Dict) -> List:
        """단일 파일 배치 처리."""
        batch_files = batch['files']
        processed_files = []
        
        for file_group in batch_files:
            # 여기에 특정 처리 로직 적용
            processed_file = self.process_file_group(file_group)
            processed_files.append(processed_file)
        
        return processed_files
    
    def process_file_group(self, file_group: Dict) -> Dict:
        """개별 파일 그룹 처리 - 여기에 로직을 구현하세요."""
        # 예제: 배치 처리 메타데이터 추가
        file_group['batch_processed'] = True
        file_group['processed_timestamp'] = datetime.now().isoformat()
        return file_group
```

## 오류 처리 및 로깅

### 포괄적인 오류 처리

```python
class RobustUploader(BaseUploader):
    def process_files(self, organized_files: List) -> List:
        """포괄적인 오류 처리로 파일 처리."""
        processed_files = []
        failed_files = []
        
        for i, file_group in enumerate(organized_files):
            try:
                self.run.log_message(f"파일 그룹 {i+1}/{len(organized_files)} 처리 중")
                
                # 검증과 함께 처리
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
                
                self.run.log_message(f"파일 그룹 처리 실패: {str(e)}")
                
                # 다른 파일 처리 계속
                continue
        
        # 요약 로그
        self.run.log_message(
            f"처리 완료: {len(processed_files)}개 성공, {len(failed_files)}개 실패"
        )
        
        if failed_files:
            # 오류 보고서 저장
            self.save_error_report(failed_files)
        
        return processed_files
    
    def process_file_group_safely(self, file_group: Dict) -> Dict:
        """검증 및 오류 검사와 함께 파일 그룹 처리."""
        # 파일 그룹 구조 검증
        if 'files' not in file_group:
            raise ValueError("파일 그룹에 'files' 키가 없습니다")
        
        files_dict = file_group['files']
        if not files_dict:
            raise ValueError("파일 그룹에 파일이 없습니다")
        
        # 파일 접근 가능성 검증
        for spec_name, file_path in files_dict.items():
            if not file_path.exists():
                raise FileNotFoundError(f"파일을 찾을 수 없음: {file_path}")
            
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"파일을 읽을 수 없음: {file_path}")
        
        # 실제 처리 수행
        return self.apply_processing_logic(file_group)
    
    def save_error_report(self, failed_files: List):
        """디버깅을 위한 상세 오류 보고서 저장."""
        error_report_path = self.path / 'error_report.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'plugin_name': self.__class__.__name__,
            'total_errors': len(failed_files),
            'errors': failed_files
        }
        
        with open(error_report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.run.log_message(f"오류 보고서 저장됨: {error_report_path}")
```

### 구조화된 로깅

```python
class LoggingUploader(BaseUploader):
    def setup_directories(self):
        """로깅 디렉토리 설정."""
        log_dir = self.path / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # 구조화된 로깅 초기화
        self.setup_structured_logging(log_dir)
    
    def setup_structured_logging(self, log_dir: Path):
        """다양한 레벨의 구조화된 로깅 설정."""
        import logging
        import json
        
        # 구조화된 로그를 위한 커스텀 포매터 생성
        class StructuredFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'plugin': 'LoggingUploader'
                }
                
                # 추가 필드가 있으면 추가
                if hasattr(record, 'file_path'):
                    log_entry['file_path'] = str(record.file_path)
                if hasattr(record, 'operation'):
                    log_entry['operation'] = record.operation
                if hasattr(record, 'duration'):
                    log_entry['duration'] = record.duration
                
                return json.dumps(log_entry)
        
        # 로거 설정
        self.logger = logging.getLogger('upload_plugin')
        self.logger.setLevel(logging.INFO)
        
        # 파일 핸들러
        handler = logging.FileHandler(log_dir / 'plugin.log')
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
    
    def process_files(self, organized_files: List) -> List:
        """상세 로깅과 함께 파일 처리."""
        start_time = time.time()
        
        self.logger.info(
            f"파일 처리 시작",
            extra={'operation': 'process_files', 'file_count': len(organized_files)}
        )
        
        processed_files = []
        
        for i, file_group in enumerate(organized_files):
            file_start_time = time.time()
            
            try:
                # 파일 그룹 처리
                processed_file = self.process_file_group(file_group)
                processed_files.append(processed_file)
                
                # 성공 로그
                duration = time.time() - file_start_time
                self.logger.info(
                    f"파일 그룹 {i+1} 처리 성공",
                    extra={
                        'operation': 'process_file_group',
                        'file_group_index': i,
                        'duration': duration
                    }
                )
                
            except Exception as e:
                # 오류 로그
                duration = time.time() - file_start_time
                self.logger.error(
                    f"파일 그룹 {i+1} 처리 실패: {str(e)}",
                    extra={
                        'operation': 'process_file_group',
                        'file_group_index': i,
                        'duration': duration,
                        'error': str(e)
                    }
                )
                raise
        
        # 전체 완료 로그
        total_duration = time.time() - start_time
        self.logger.info(
            f"파일 처리 완료",
            extra={
                'operation': 'process_files',
                'total_duration': total_duration,
                'processed_count': len(processed_files)
            }
        )
        
        return processed_files
```

## 성능 최적화

### 메모리 관리

```python
class MemoryEfficientUploader(BaseUploader):
    """대용량 파일 처리에 최적화된 업로더."""
    
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
        
        self.chunk_size = extra_params.get('chunk_size', 8192)  # 8KB 청크
        self.memory_limit = extra_params.get('memory_limit_mb', 100) * 1024 * 1024
    
    def process_files(self, organized_files: List) -> List:
        """메모리 관리와 함께 파일 처리."""
        import psutil
        import gc
        
        processed_files = []
        
        for file_group in organized_files:
            # 처리 전 메모리 사용량 확인
            memory_usage = psutil.Process().memory_info().rss
            
            if memory_usage > self.memory_limit:
                self.run.log_message(f"높은 메모리 사용량: {memory_usage / 1024 / 1024:.1f}MB")
                
                # 가비지 컬렉션 강제 실행
                gc.collect()
                
                # 정리 후 다시 확인
                memory_usage = psutil.Process().memory_info().rss
                if memory_usage > self.memory_limit:
                    self.run.log_message("메모리 한계 초과, 더 작은 청크로 처리합니다")
                    processed_file = self.process_file_group_chunked(file_group)
                else:
                    processed_file = self.process_file_group_normal(file_group)
            else:
                processed_file = self.process_file_group_normal(file_group)
            
            processed_files.append(processed_file)
        
        return processed_files
    
    def process_file_group_chunked(self, file_group: Dict) -> Dict:
        """메모리 관리를 위해 큰 파일을 청크로 처리."""
        files_dict = file_group.get('files', {})
        processed_files = {}
        
        for spec_name, file_path in files_dict.items():
            if file_path.stat().st_size > 50 * 1024 * 1024:  # 50MB
                # 큰 파일을 청크로 처리
                processed_path = self.process_large_file_chunked(file_path)
                processed_files[spec_name] = processed_path
            else:
                # 작은 파일은 일반적으로 처리
                processed_files[spec_name] = file_path
        
        file_group['files'] = processed_files
        return file_group
    
    def process_large_file_chunked(self, file_path: Path) -> Path:
        """큰 파일을 청크로 처리."""
        output_path = self.path / 'processed' / file_path.name
        
        with open(file_path, 'rb') as infile, open(output_path, 'wb') as outfile:
            while True:
                chunk = infile.read(self.chunk_size)
                if not chunk:
                    break
                
                # 청크에 처리 적용
                processed_chunk = self.process_chunk(chunk)
                outfile.write(processed_chunk)
        
        return output_path
    
    def process_chunk(self, chunk: bytes) -> bytes:
        """개별 청크 처리 - 로직으로 오버라이드하세요."""
        # 예제: 단순 통과
        return chunk
```

### 비동기 처리

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

class AsyncUploader(BaseUploader):
    """비동기 처리 기능을 갖춘 업로더."""
    
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
        
        self.max_concurrent = extra_params.get('max_concurrent', 5)
        self.use_process_pool = extra_params.get('use_process_pool', False)
    
    def process_files(self, organized_files: List) -> List:
        """비동기적으로 파일 처리."""
        # 동기 컨텍스트에서 비동기 처리 실행
        return asyncio.run(self._process_files_async(organized_files))
    
    async def _process_files_async(self, organized_files: List) -> List:
        """주요 비동기 처리 메소드."""
        if self.use_process_pool:
            return await self._process_with_process_pool(organized_files)
        else:
            return await self._process_with_async_tasks(organized_files)
    
    async def _process_with_async_tasks(self, organized_files: List) -> List:
        """동시성 제한과 함께 비동기 작업을 사용하여 처리."""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_with_semaphore(file_group):
            async with semaphore:
                return await self._process_file_group_async(file_group)
        
        # 모든 파일 그룹에 대한 작업 생성
        tasks = [
            process_with_semaphore(file_group) 
            for file_group in organized_files
        ]
        
        # 모든 작업 완료 대기
        processed_files = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 필터링 및 오류 로그
        valid_files = []
        for i, result in enumerate(processed_files):
            if isinstance(result, Exception):
                self.run.log_message(f"파일 그룹 {i} 처리 오류: {str(result)}")
            else:
                valid_files.append(result)
        
        return valid_files
    
    async def _process_with_process_pool(self, organized_files: List) -> List:
        """CPU 집약적 작업을 위해 프로세스 풀 사용."""
        loop = asyncio.get_event_loop()
        
        with ProcessPoolExecutor(max_workers=self.max_concurrent) as executor:
            # 모든 작업을 프로세스 풀에 제출
            futures = [
                loop.run_in_executor(executor, self._process_file_group_sync, file_group)
                for file_group in organized_files
            ]
            
            # 완료 대기
            processed_files = await asyncio.gather(*futures, return_exceptions=True)
            
            # 예외 필터링
            valid_files = []
            for i, result in enumerate(processed_files):
                if isinstance(result, Exception):
                    self.run.log_message(f"파일 그룹 {i}의 프로세스 풀 오류: {str(result)}")
                else:
                    valid_files.append(result)
            
            return valid_files
    
    async def _process_file_group_async(self, file_group: Dict) -> Dict:
        """개별 파일 그룹의 비동기 처리."""
        # 비동기 I/O 작업 시뮬레이션
        await asyncio.sleep(0.1)
        
        # 여기에 처리 로직 적용
        file_group['async_processed'] = True
        file_group['processed_timestamp'] = datetime.now().isoformat()
        
        return file_group
    
    def _process_file_group_sync(self, file_group: Dict) -> Dict:
        """프로세스 풀을 위한 동기 처리."""
        # 별도 프로세스에서 실행됨
        import time
        time.sleep(0.1)  # CPU 작업 시뮬레이션
        
        file_group['process_pool_processed'] = True
        file_group['processed_timestamp'] = datetime.now().isoformat()
        
        return file_group
```

## 테스트 및 디버깅

### 단위 테스트 프레임워크

```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

class TestMyUploader(unittest.TestCase):
    """커스텀 업로더를 위한 테스트 스위트."""
    
    def setUp(self):
        """테스트 환경 설정."""
        # 임시 디렉토리 생성
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # run 객체 모킹
        self.mock_run = Mock()
        self.mock_run.log_message = Mock()
        
        # 샘플 파일 사양
        self.file_specification = [
            {'name': 'image_data', 'file_type': 'image'},
            {'name': 'text_data', 'file_type': 'text'}
        ]
        
        # 테스트 파일 생성
        self.test_files = self.create_test_files()
        
        # 샘플 조직화된 파일
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
        """테스트 환경 정리."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_files(self) -> Dict[str, Path]:
        """테스트를 위한 테스트 파일 생성."""
        files = {}
        
        # 테스트 이미지 파일 생성
        image_file = self.temp_dir / 'test_image.jpg'
        with open(image_file, 'wb') as f:
            f.write(b'fake_image_data')
        files['image'] = image_file
        
        # 테스트 텍스트 파일 생성
        text_file = self.temp_dir / 'test_text.txt'
        with open(text_file, 'w') as f:
            f.write('test content')
        files['text'] = text_file
        
        return files
    
    def test_initialization(self):
        """업로더 초기화 테스트."""
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
        """process_files 메소드 테스트."""
        uploader = MyUploader(
            run=self.mock_run,
            path=self.temp_dir,
            file_specification=self.file_specification,
            organized_files=self.organized_files
        )
        
        result = uploader.process_files(self.organized_files)
        
        # 결과 구조 검증
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        
        # 처리가 발생했는지 검증
        processed_file = result[0]
        self.assertIn('processed_by', processed_file)
        self.assertEqual(processed_file['processed_by'], 'MyUploader')
    
    def test_handle_upload_files_workflow(self):
        """전체 워크플로우 테스트."""
        uploader = MyUploader(
            run=self.mock_run,
            path=self.temp_dir,
            file_specification=self.file_specification,
            organized_files=self.organized_files
        )
        
        # 워크플로우 메소드 모킹
        with patch.object(uploader, 'setup_directories') as mock_setup, \
             patch.object(uploader, 'organize_files', return_value=self.organized_files) as mock_organize, \
             patch.object(uploader, 'before_process', return_value=self.organized_files) as mock_before, \
             patch.object(uploader, 'process_files', return_value=self.organized_files) as mock_process, \
             patch.object(uploader, 'after_process', return_value=self.organized_files) as mock_after, \
             patch.object(uploader, 'validate_files', return_value=self.organized_files) as mock_validate:
            
            result = uploader.handle_upload_files()
            
            # 모든 메소드가 올바른 순서로 호출되었는지 검증
            mock_setup.assert_called_once()
            mock_organize.assert_called_once()
            mock_before.assert_called_once()
            mock_process.assert_called_once()
            mock_after.assert_called_once()
            mock_validate.assert_called_once()
            
            self.assertEqual(result, self.organized_files)
    
    def test_error_handling(self):
        """process_files의 오류 처리 테스트."""
        uploader = MyUploader(
            run=self.mock_run,
            path=self.temp_dir,
            file_specification=self.file_specification,
            organized_files=self.organized_files
        )
        
        # 유효하지 않은 파일 그룹으로 테스트
        invalid_files = [{'invalid': 'structure'}]
        
        with self.assertRaises(Exception):
            uploader.process_files(invalid_files)
    
    @patch('your_module.some_external_dependency')
    def test_external_dependencies(self, mock_dependency):
        """외부 의존성과의 통합 테스트."""
        mock_dependency.return_value = 'mocked_result'
        
        uploader = MyUploader(
            run=self.mock_run,
            path=self.temp_dir,
            file_specification=self.file_specification,
            organized_files=self.organized_files
        )
        
        # 외부 의존성을 사용하는 메소드 테스트
        result = uploader.some_method_using_dependency()
        
        mock_dependency.assert_called_once()
        self.assertEqual(result, 'expected_result_based_on_mock')

if __name__ == '__main__':
    # 특정 테스트 실행
    unittest.main()
```

### 통합 테스트

```python
class TestUploaderIntegration(unittest.TestCase):
    """실제 파일 작업을 포함한 업로더 통합 테스트."""
    
    def setUp(self):
        """통합 테스트 환경 설정."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_run = Mock()
        
        # 현실적인 테스트 파일 생성
        self.create_realistic_test_files()
    
    def create_realistic_test_files(self):
        """통합 테스트를 위한 현실적인 테스트 파일 생성."""
        # 다양한 파일 타입 생성
        (self.temp_dir / 'images').mkdir()
        (self.temp_dir / 'data').mkdir()
        
        # 실제로 처리할 수 있는 TIFF 이미지
        tiff_path = self.temp_dir / 'images' / 'test.tif'
        # 최소한의 유효한 TIFF 파일 생성
        self.create_minimal_tiff(tiff_path)
        
        # JSON 데이터 파일
        json_path = self.temp_dir / 'data' / 'test.json'
        with open(json_path, 'w') as f:
            json.dump({'test': 'data', 'values': [1, 2, 3]}, f)
        
        self.test_files = {
            'image_file': tiff_path,
            'data_file': json_path
        }
    
    def create_minimal_tiff(self, path: Path):
        """테스트를 위한 최소한의 유효한 TIFF 파일 생성."""
        try:
            from PIL import Image
            import numpy as np
            
            # 작은 테스트 이미지 생성
            array = np.zeros((50, 50, 3), dtype=np.uint8)
            array[10:40, 10:40] = [255, 0, 0]  # 빨간 사각형
            
            image = Image.fromarray(array)
            image.save(path, 'TIFF')
        except ImportError:
            # 대안: PIL을 사용할 수 없으면 빈 파일 생성
            path.touch()
    
    def test_full_workflow_with_real_files(self):
        """실제 파일 작업과 함께 전체 워크플로우 테스트."""
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
        
        # 전체 워크플로우 실행
        result = uploader.handle_upload_files()
        
        # 결과 검증
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        
        # 처리 디렉토리가 생성되었는지 확인
        self.assertTrue((self.temp_dir / 'processed').exists())
        self.assertTrue((self.temp_dir / 'thumbnails').exists())
        
        # 로깅 호출 검증
        self.assertTrue(self.mock_run.log_message.called)
```

### 디버깅 유틸리티

```python
class DebuggingUploader(BaseUploader):
    """향상된 디버깅 기능을 갖춘 업로더."""
    
    def __init__(self, run, path: Path, file_specification: List = None, 
                 organized_files: List = None, extra_params: Dict = None):
        super().__init__(run, path, file_specification, organized_files, extra_params)
        
        self.debug_mode = extra_params.get('debug_mode', False)
        self.debug_dir = self.path / 'debug'
        
        if self.debug_mode:
            self.debug_dir.mkdir(exist_ok=True)
            self.setup_debugging()
    
    def setup_debugging(self):
        """디버깅 인프라 초기화."""
        import json
        
        # 초기화 상태 저장
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
        """향상된 디버그 로깅."""
        if not self.debug_mode:
            return
        
        debug_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'data': data
        }
        
        # 디버그 로그에 작성
        debug_log_path = self.debug_dir / 'debug.log'
        with open(debug_log_path, 'a') as f:
            f.write(json.dumps(debug_entry, default=str) + '\n')
        
        # 메인 run에도 로그
        self.run.log_message(f"DEBUG: {message}")
    
    def setup_directories(self):
        """디버깅과 함께 디렉토리 설정."""
        self.debug_log("디렉토리 설정 중")
        super().setup_directories()
        
        if self.debug_mode:
            # 디렉토리 상태 저장
            dirs_state = {
                'existing_dirs': [str(p) for p in self.path.iterdir() if p.is_dir()],
                'path_exists': self.path.exists(),
                'path_writable': os.access(self.path, os.W_OK)
            }
            self.debug_log("디렉토리 설정 완료", dirs_state)
    
    def process_files(self, organized_files: List) -> List:
        """디버깅 계측과 함께 파일 처리."""
        self.debug_log(f"{len(organized_files)}개 파일 그룹으로 process_files 시작")
        
        # 입력 상태 저장
        if self.debug_mode:
            with open(self.debug_dir / 'input_files.json', 'w') as f:
                json.dump(organized_files, f, indent=2, default=str)
        
        processed_files = []
        
        for i, file_group in enumerate(organized_files):
            self.debug_log(f"파일 그룹 {i+1} 처리 중")
            
            try:
                # 타이밍과 함께 처리
                start_time = time.time()
                processed_file = self.process_file_group_with_debug(file_group, i)
                duration = time.time() - start_time
                
                processed_files.append(processed_file)
                self.debug_log(f"파일 그룹 {i+1} 처리 성공", {'duration': duration})
                
            except Exception as e:
                error_data = {
                    'file_group_index': i,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'file_group': file_group
                }
                self.debug_log(f"파일 그룹 {i+1} 처리 오류", error_data)
                
                # 오류 상태 저장
                if self.debug_mode:
                    with open(self.debug_dir / f'error_group_{i}.json', 'w') as f:
                        json.dump(error_data, f, indent=2, default=str)
                
                raise
        
        # 출력 상태 저장
        if self.debug_mode:
            with open(self.debug_dir / 'output_files.json', 'w') as f:
                json.dump(processed_files, f, indent=2, default=str)
        
        self.debug_log(f"{len(processed_files)}개 처리된 파일로 process_files 완료")
        return processed_files
    
    def process_file_group_with_debug(self, file_group: Dict, index: int) -> Dict:
        """디버깅과 함께 개별 파일 그룹 처리."""
        if self.debug_mode:
            # 중간 상태 저장
            with open(self.debug_dir / f'group_{index}_input.json', 'w') as f:
                json.dump(file_group, f, indent=2, default=str)
        
        # 처리 로직 적용
        processed_group = self.apply_custom_processing(file_group)
        
        if self.debug_mode:
            # 결과 상태 저장
            with open(self.debug_dir / f'group_{index}_output.json', 'w') as f:
                json.dump(processed_group, f, indent=2, default=str)
        
        return processed_group
    
    def apply_custom_processing(self, file_group: Dict) -> Dict:
        """커스텀 처리 로직 - 필요에 따라 구현하세요."""
        # 예제 구현
        file_group['debug_processed'] = True
        file_group['processing_timestamp'] = datetime.now().isoformat()
        return file_group
    
    def generate_debug_report(self):
        """포괄적인 디버그 보고서 생성."""
        if not self.debug_mode:
            return
        
        report = {
            'plugin_name': self.__class__.__name__,
            'debug_session': datetime.now().isoformat(),
            'files_processed': 0,
            'errors': [],
            'performance': {}
        }
        
        # 디버그 파일 분석
        for debug_file in self.debug_dir.glob('*.json'):
            if debug_file.name.startswith('error_'):
                with open(debug_file) as f:
                    error_data = json.load(f)
                    report['errors'].append(error_data)
            elif debug_file.name == 'output_files.json':
                with open(debug_file) as f:
                    output_data = json.load(f)
                    report['files_processed'] = len(output_data)
        
        # 최종 보고서 저장
        with open(self.debug_dir / 'debug_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.run.log_message(f"디버그 보고서 생성됨: {self.debug_dir / 'debug_report.json'}")
```

## 모범 사례 요약

### 1. 코드 구성
- `process_files()`를 핵심 로직에 집중시키기
- 설정, 정리, 검증을 위한 훅 메소드 사용
- 헬퍼 메소드를 사용하여 관심사 분리
- 단일 책임 원칙 따르기

### 2. 오류 처리
- 포괄적인 오류 처리 구현
- 컨텍스트 정보와 함께 오류 로깅
- 가능할 때 우아하게 실패
- 의미 있는 오류 메시지 제공

### 3. 성능
- 처리 로직 프로파일링
- 적절한 데이터 구조 사용
- 대용량 파일의 메모리 사용량 고려
- I/O 집약적 작업에 비동기 처리 구현

### 4. 테스트
- 모든 메소드에 대한 단위 테스트 작성
- 실제 파일과 함께 통합 테스트 포함
- 오류 조건 및 엣지 케이스 테스트
- 외부 의존성에 모킹 사용

### 5. 로깅
- 중요한 작업 및 이정표 로깅
- 성능 분석을 위한 타이밍 정보 포함
- 더 나은 분석을 위한 구조화된 로깅 사용
- 다양한 로그 레벨 제공 (info, warning, error)

### 6. 구성
- 플러그인 구성에 `extra_params` 사용
- 합리적인 기본값 제공
- 구성 매개변수 검증
- 모든 구성 옵션 문서화

### 7. 문서화
- 명확한 독스트링으로 모든 메소드 문서화
- 사용 예제 제공
- 구성 옵션 문서화
- 문제 해결 정보 포함

이 포괄적인 가이드는 BaseUploader 템플릿을 사용하여 견고하고 효율적이며 유지보수 가능한 업로드 플러그인을 개발하는 데 도움이 될 것입니다. 예제를 특정 사용 사례와 요구사항에 맞게 조정하는 것을 기억하세요.