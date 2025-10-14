"""
Dataset CRUD API 클라이언트 - 핵심 CRUD 기능만 제공

Dataset 생성, 조회, 수정, 삭제를 위한 클라이언트 클래스
"""

import requests
import os
import time
from typing import Dict, Any, Optional, List, Union
from requests.exceptions import RequestException
import json

try:
    from .schemas import (
        DatasetCreateRequest, DatasetUpdateRequest, DatasetResponse,
        DatasetListResponse, DatasetCreateResponse, DatasetType,
        DatasetStatus, DatasetFile, DatasetTag, DatasetProcessor, DatasetFilter,
        DatasetListRequest
    )
except ImportError:
    # 직접 실행할 때를 위한 절대 import
    from schemas import (
        DatasetCreateRequest, DatasetUpdateRequest, DatasetResponse,
        DatasetListResponse, DatasetCreateResponse, DatasetType,
        DatasetStatus, DatasetFile, DatasetTag, DatasetProcessor, DatasetFilter,
        DatasetListRequest
    )


class AXDatasetHub:
    """Dataset CRUD API 클라이언트 - 핵심 CRUD 기능만 제공"""

    def __init__(self, base_url: str, api_key: str):
        """
        AXDatasetHub 초기화

        Args:
            base_url: API 기본 URL (예: "https://aip-stg.sktai.io/api/v1/data")
            api_key: API 키
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """API 요청 실행"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            # 빈 응답 처리 (삭제 API 등 - 204 No Content)
            if response.status_code == 204 or not response.text.strip():
                return {
                    "success": True,
                    "message": "요청이 성공적으로 처리되었습니다.",
                    "status_code": response.status_code
                }

            result = response.json()
            return result

        except RequestException as e:
            raise Exception(f"API 요청 실패: {e}")

    # ====================================================================
    # 핵심 CRUD Operations
    # ====================================================================

    def create_dataset(self, dataset_data: Union[DatasetCreateRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Dataset 생성 (실제 API 스펙에 맞춤)

        Args:
            dataset_data: Dataset 생성 데이터

        Returns:
            생성된 Dataset 정보
        """
        if isinstance(dataset_data, DatasetCreateRequest):
            data = dataset_data.model_dump(exclude_none=True)
        else:
            data = dataset_data.copy()
        
        # Enum 객체를 문자열로 변환
        if 'type' in data and hasattr(data['type'], 'value'):
            data['type'] = data['type'].value
        if 'status' in data and hasattr(data['status'], 'value'):
            data['status'] = data['status'].value

        # Dataset 타입별 특별 처리
        dataset_type = data.get('type')
        
        # Model Benchmark는 Data Processor를 건너뛰도록 처리
        if dataset_type == DatasetType.MODEL_BENCHMARK:
            data['processor'] = {"ids": [], "duplicate_subset_columns": [], "regular_expression": []}
        
        # Supervised Finetuning은 기본 프로세서 설정 필요
        elif dataset_type == DatasetType.SUPERVISED_FINETUNING:
            if 'processor' not in data or not data['processor']:
                # supervised_finetuning의 경우 빈 객체로 설정
                data['processor'] = {}
        
        # Unsupervised Finetuning은 기본 프로세서 설정 필요
        elif dataset_type == DatasetType.UNSUPERVISED_FINETUNING:
            if 'processor' not in data or not data['processor']:
                # 기본 프로세서 설정
                data['processor'] = {
                    "ids": [],
                    "duplicate_subset_columns": [],
                    "regular_expression": []
                }
        
        # DPO Finetuning은 특별한 처리 필요
        elif dataset_type == DatasetType.DPO_FINETUNING:
            # DPO 타입에 대한 특별한 데이터 포맷 정의
            if 'processor' not in data or not data['processor']:
                # 기본 프로세서 설정
                data['processor'] = {
                    "ids": ["remove_duplicates", "rnn_masking"],
                    "duplicate_subset_columns": ["content"],
                    "regular_expression": ["email_pattern", "phone_pattern"]
                }

        return self._make_request("POST", "/datasets", data)

    def get_datasets(self,
                    project_id: str,
                    page: int = 1,
                    size: int = 10,
                    sort: Optional[str] = None,
                    filter: Optional[DatasetFilter] = None,
                    search: Optional[str] = None) -> Dict[str, Any]:
        """
        Dataset 목록 조회 (실제 API 스펙에 맞춤)

        Args:
            project_id: 프로젝트 ID
            page: 페이지 번호
            size: 페이지 크기
            sort: 정렬 기준
            filter: 필터 조건
            search: 검색어

        Returns:
            Dataset 목록
        """
        params = {
            "project_id": project_id,
            "page": page,
            "size": size
        }

        if sort:
            params["sort"] = sort
        if search:
            params["search"] = search
        if filter:
            filter_dict = filter.model_dump(exclude_none=True)
            # type 필드명 변경
            if 'type' in filter_dict:
                params['type'] = filter_dict['type']
            if 'status' in filter_dict:
                params['status'] = filter_dict['status']
            if 'tags' in filter_dict:
                params['tags'] = filter_dict['tags']

        return self._make_request("GET", "/datasets", params=params)

    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Dataset 상세 조회 (ID로 조회)

        Args:
            dataset_id: Dataset ID

        Returns:
            Dataset 상세 정보
        """
        return self._make_request("GET", f"/datasets/{dataset_id}")

    def update_dataset(self, dataset_id: str, dataset_data: Union[DatasetUpdateRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Dataset 수정 (description, project_id, tags만 수정 가능)

        Args:
            dataset_id: Dataset ID
            dataset_data: 수정할 Dataset 데이터 (description, project_id, tags만)

        Returns:
            수정 결과
        """
        if isinstance(dataset_data, DatasetUpdateRequest):
            data = dataset_data.model_dump(exclude_none=True)
        else:
            data = dataset_data

        return self._make_request("PUT", f"/datasets/{dataset_id}", data)

    def update_dataset_tags(self, dataset_id: str, tags: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Dataset 태그 수정

        Args:
            dataset_id: Dataset ID
            tags: 수정할 태그 목록 [{"name": "tag1"}, {"name": "tag2"}]

        Returns:
            수정 결과
        """
        return self._make_request("PUT", f"/datasets/{dataset_id}/tags", tags)

    def delete_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Dataset 삭제 (논리적 삭제 - is_deleted=True로 설정)

        Args:
            dataset_id: Dataset ID

        Returns:
            삭제 결과 (204 No Content)
        """
        return self._make_request("DELETE", f"/datasets/{dataset_id}")

    # ====================================================================
    # 파일 업로드 관련 기능
    # ====================================================================

    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        파일 업로드 (임시 저장) - 실제 API 스펙에 맞춤

        Args:
            file_path: 업로드할 파일 경로

        Returns:
            업로드 결과 (temp_file_path 포함)
        """
        url = f"{self.base_url}/datasources/upload/files"

        try:
            with open(file_path, 'rb') as file:
                files = {'files': file}
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.post(url, files=files, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"파일 업로드 실패: {e}")

    def upload_multiple_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        여러 파일 업로드 (임시 저장) - 실제 API 스펙에 맞춤

        Args:
            file_paths: 업로드할 파일 경로 목록

        Returns:
            업로드 결과 (temp_file_path 목록 포함)
        """
        url = f"{self.base_url}/datasources/upload/files"

        try:
            files = []
            for file_path in file_paths:
                files.append(('files', open(file_path, 'rb')))
            
            # budget 파라미터 제거 (추후 작업 예정)
            data = {}
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(url, files=files, data=data, headers=headers)
            response.raise_for_status()
            
            # 파일 핸들 닫기
            for _, file_handle in files:
                file_handle.close()
                
            return response.json()
        except Exception as e:
            raise Exception(f"다중 파일 업로드 실패: {e}")

    def create_datasource(self, project_id: str, name: str, temp_files: List[Dict[str, Any]], 
                         description: str = "", scope: str = "private_logical") -> Dict[str, Any]:
        """
        데이터소스 생성 (실제 API 스펙에 맞춤)

        Args:
            project_id: 프로젝트 ID
            name: 데이터소스 이름
            temp_files: temp_files 배열 (파일 업로드 결과에서 가져온 것)
            description: 데이터소스 설명
            scope: 데이터소스 범위

        Returns:
            생성된 데이터소스 정보 (datasource_id 포함)
        """
        datasource_data = {
            "project_id": project_id,
            "name": name,
            "type": "file",  # 파일 타입으로 수정
            "created_by": "",
            "updated_by": "",
            "description": description,
            "s3_config": {
                "bucket_name": "",
                "access_key": "",
                "secret_key": "",
                "region": "",
                "prefix": ""
            },
            "temp_files": temp_files,
            "policy": []
        }

        return self._make_request("POST", "/datasources", datasource_data)

    def get_datasources(self, project_id: str, page: int = 1, size: int = 10, 
                       search: Optional[str] = None) -> Dict[str, Any]:
        """
        데이터소스 목록 조회

        Args:
            project_id: 프로젝트 ID
            page: 페이지 번호
            size: 페이지 크기
            search: 검색어

        Returns:
            데이터소스 목록
        """
        params = {
            "project_id": project_id,
            "page": page,
            "size": size
        }

        if search:
            params["search"] = search

        return self._make_request("GET", "/datasources", params=params)

    # ====================================================================
    # 데이터 프로세서 관련 기능
    # ====================================================================

    def get_available_processors(self) -> Dict[str, Any]:
        """
        사용 가능한 데이터 프로세서 목록 조회

        Returns:
            프로세서 목록
        """
        return self._make_request("GET", "/datasets/processors")

    def apply_processors(self, dataset_id: str, processors: List[DatasetProcessor]) -> Dict[str, Any]:
        """
        Dataset에 데이터 프로세서 적용

        Args:
            dataset_id: Dataset ID
            processors: 적용할 프로세서 목록

        Returns:
            적용 결과
        """
        data = {
            "processors": [processor.model_dump() for processor in processors]
        }
        return self._make_request("POST", f"/datasets/{dataset_id}/processors", data)

    # ====================================================================
    # 통합 Dataset 생성 기능 (파일 업로드 + 데이터소스 생성 + Dataset 생성)
    # ====================================================================

    def create_dataset_with_files(self, name: str, description: str, project_id: str, 
                                 file_paths: List[str], dataset_type: DatasetType, 
                                 tags: Optional[List[str]] = None, 
                                 processor: Optional[DatasetProcessor] = None) -> Dict[str, Any]:
        """
        파일을 포함한 Dataset 생성 (전체 플로우)

        Args:
            name: Dataset 이름
            description: Dataset 설명
            project_id: 프로젝트 ID
            file_paths: 업로드할 파일 경로 목록
            dataset_type: Dataset 타입
            tags: 태그 목록
            processor: 데이터 프로세서 설정

        Returns:
            생성된 Dataset 정보
        """
        try:
            # model_benchmark 타입은 다른 엔드포인트 사용
            if dataset_type == DatasetType.MODEL_BENCHMARK:
                return self._create_model_benchmark_dataset(name, description, project_id, file_paths, tags)
            
            # 1단계: 파일 업로드
            print("1단계: 파일 업로드 중...")
            upload_result = self.upload_multiple_files(file_paths)
            print(f"파일 업로드 완료: {upload_result}")

            # 2단계: temp_files 배열 구성
            temp_files = []
            upload_data = upload_result.get("data", [])
            for i, file_path in enumerate(file_paths):
                temp_file_path = upload_data[i].get("temp_file_path") if i < len(upload_data) else None
                temp_files.append({
                    "file_name": os.path.basename(file_path),
                    "temp_file_path": temp_file_path,
                    "file_metadata": None,
                    "knowledge_config": None
                })

            # 3단계: 데이터소스 생성
            print("2단계: 데이터소스 생성 중...")
            datasource_name = f"datasource_{name}_{int(time.time())}"
            datasource_result = self.create_datasource(
                project_id=project_id,
                name=datasource_name,
                temp_files=temp_files,
                description=f"Data source for {name}"
            )
            datasource_id = datasource_result.get("id")
            print(f"데이터소스 생성 완료: {datasource_id}")

            # 데이터소스 생성 후 잠시 대기 (데이터소스가 완전히 준비될 때까지)
            print("데이터소스 준비 대기 중...")
            time.sleep(2)  # 2초 대기

            # 4단계: Dataset 생성
            print("3단계: Dataset 생성 중...")
            dataset_tags = [{"name": tag} for tag in (tags or [])]
            
            # processor 설정 - supervised_finetuning과 unsupervised_finetuning의 경우 빈 객체로 설정
            processor_data = {}
            if processor:
                processor_dict = processor.model_dump() if hasattr(processor, 'model_dump') else processor
                # 빈 배열 필드 제거
                processor_data = {k: v for k, v in processor_dict.items() if v}
                if not processor_data:
                    processor_data = {}
            elif dataset_type == DatasetType.SUPERVISED_FINETUNING:
                # supervised_finetuning의 경우 빈 객체로 설정
                processor_data = {}
            elif dataset_type == DatasetType.UNSUPERVISED_FINETUNING:
                # unsupervised_finetuning의 경우 실제 프로세서 설정
                processor_data = {
                    "ids": ["3398014c-e0ad-4b4d-a8d2-44f4b0d0ff1d"],
                    "duplicate_subset_columns": ["no"],
                    "regular_expression": []
                }
            
            # 성공하는 형식에 맞춰 빈 배열로 설정
            policy_data = []
            
            dataset_data = DatasetCreateRequest(
                name=name,
                description=description,
                project_id=project_id,
                type=dataset_type,
                tags=dataset_tags,
                datasource_id=datasource_id,
                processor=processor_data,  # 설정된 processor_data 사용
                is_deleted=False,
                created_by="",
                updated_by="",
                policy=policy_data
            )
            
            # status는 기본값 PROCESSING 사용 (빈 문자열 대신)
            # dataset_data.status = ""  # 이 줄 제거

            result = self.create_dataset(dataset_data)
            print(f"Dataset 생성 완료: {result.get('id')}")
            return result

        except Exception as e:
            raise Exception(f"Dataset 생성 실패: {e}")

    def _create_model_benchmark_dataset(self, name: str, description: str, project_id: str, 
                                       file_paths: List[str], tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Model Benchmark Dataset 생성 (직접 업로드 방식)
        
        Args:
            name: Dataset 이름
            description: Dataset 설명
            project_id: 프로젝트 ID
            file_paths: 업로드할 파일 경로 목록
            tags: 태그 목록
            
        Returns:
            생성된 Dataset 정보
        """
        try:
            print("Model Benchmark Dataset 생성 중...")
            
            # /api/v1/datasets/upload/files 엔드포인트 사용
            url = f"{self.base_url}/datasets/upload/files"
            
            # 파일 준비
            files = []
            for file_path in file_paths:
                files.append(('files', open(file_path, 'rb')))
            
            # 데이터 준비 (datasource_id 없이)
            dataset_tags = [{"name": tag} for tag in (tags or [])]
            
            data = {
                'name': name,
                'description': description,
                'project_id': project_id,
                'type': DatasetType.MODEL_BENCHMARK.value,
                'tags': str(dataset_tags),  # JSON 문자열로 변환
                'status': '',
                'created_by': '',
                'updated_by': '',
                'payload': ''
            }
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.post(url, files=files, data=data, headers=headers)
            response.raise_for_status()
            
            # 파일 핸들 닫기
            for _, file_handle in files:
                file_handle.close()
                
            result = response.json()
            print(f"Model Benchmark Dataset 생성 완료: {result.get('id')}")
            return result
            
        except Exception as e:
            # 파일 핸들 닫기 (에러 발생 시)
            try:
                for _, file_handle in files:
                    file_handle.close()
            except:
                pass
            raise Exception(f"Model Benchmark Dataset 생성 실패: {e}")

    # ====================================================================
    # Dataset 타입별 특별 기능
    # ====================================================================

    def create_dpo_dataset(self, name: str, description: str, project_id: str, 
                          datasource_id: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        DPO Finetuning Dataset 생성 (실제 API 스펙에 맞춤)

        Args:
            name: Dataset 이름
            description: Dataset 설명
            project_id: 프로젝트 ID
            datasource_id: 데이터 소스 ID
            tags: 태그 목록

        Returns:
            생성된 Dataset 정보
        """
        # DPO 타입에 맞는 프로세서 설정
        processor = {
            "ids": ["remove_duplicates", "rnn_masking", "email_masking"],
            "duplicate_subset_columns": ["content", "preference"],
            "regular_expression": ["email_pattern", "phone_pattern", "ssn_pattern"]
        }

        dataset_data = {
            "name": name,
            "type": DatasetType.DPO_FINETUNING,
            "description": description,
            "project_id": project_id,
            "datasource_id": datasource_id,
            "tags": [{"name": tag} for tag in (tags or [])],
            "processor": processor,
            "status": DatasetStatus.PROCESSING
        }

        return self.create_dataset(dataset_data)

    def create_custom_dataset(self, name: str, description: str, project_id: str,
                             tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Custom Dataset 생성 (Data source 없이, 실제 API 스펙에 맞춤)

        Args:
            name: Dataset 이름
            description: Dataset 설명
            project_id: 프로젝트 ID
            tags: 태그 목록

        Returns:
            생성된 Dataset 정보
        """
        dataset_data = {
            "name": name,
            "type": DatasetType.CUSTOM,
            "description": description,
            "project_id": project_id,
            "datasource_id": None,  # Custom은 데이터 소스 없이 생성
            "tags": [{"name": tag} for tag in (tags or [])],
            "processor": {"ids": [], "duplicate_subset_columns": [], "regular_expression": []},  # Custom은 프로세서 없음
            "status": DatasetStatus.PROCESSING
        }

        return self.create_dataset(dataset_data)

    def create_model_benchmark_dataset(self, name: str, description: str, project_id: str,
                                      datasource_id: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Model Benchmark Dataset 생성 (ZIP 파일 전용, 프로세서 없음)

        Args:
            name: Dataset 이름
            description: Dataset 설명
            project_id: 프로젝트 ID
            datasource_id: 데이터 소스 ID
            tags: 태그 목록

        Returns:
            생성된 Dataset 정보
        """
        dataset_data = {
            "name": name,
            "type": DatasetType.MODEL_BENCHMARK,
            "description": description,
            "project_id": project_id,
            "datasource_id": datasource_id,
            "tags": [{"name": tag} for tag in (tags or [])],
            "processor": None,  # Model Benchmark는 프로세서 없음
            "status": DatasetStatus.PROCESSING
        }

        return self.create_dataset(dataset_data)
