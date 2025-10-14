"""
Model CRUD Hub V2

API를 통한 모델 관리 기능을 제공하는 클라이언트입니다.
핵심 CRUD 기능만 제공합니다.
"""

import requests
import os
from typing import Dict, Any, Optional, List, Union
from requests.exceptions import RequestException
from adxp_sdk.auth import TokenCredentials

try:
    from .schemas_v2 import ModelCreateRequest, ModelUpdateRequest
except ImportError:
    from schemas_v2 import ModelCreateRequest, ModelUpdateRequest


class AXModelHubV2:
    """Model CRUD API 클라이언트 - 핵심 CRUD 기능만 제공"""
    
    def __init__(self, 
                 credentials: Union[TokenCredentials, None] = None,
                 headers: Optional[Dict[str, str]] = None,
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None):
        """
        AXModelHubV2 초기화
        
        Args:
            credentials: 인증 정보 (deprecated, use headers and base_url instead)
            headers: HTTP 헤더
            base_url: API 기본 URL
            api_key: API 키 (headers와 base_url이 없을 때 사용)
        """
        if credentials is not None:
            # Legacy mode: use Credentials object
            self.credentials = credentials
            self.base_url = credentials.base_url
            self.headers = credentials.get_headers()
        elif headers is not None and base_url is not None:
            # New mode: use headers and base_url directly
            self.credentials = None
            self.base_url = base_url
            self.headers = headers
        elif api_key is not None and base_url is not None:
            # Simple mode: use api_key and base_url
            self.credentials = None
            self.base_url = base_url.rstrip('/')
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        else:
            raise ValueError("Either credentials, (headers and base_url), or (api_key and base_url) must be provided")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """API 요청 실행"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            # 파일 업로드용 헤더 (multipart/form-data)
            if files:
                headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
            else:
                headers = self.headers
            
            # 디버깅 정보 출력
            print(f"🔍 API 요청 디버깅:")
            print(f"   - URL: {url}")
            print(f"   - Method: {method}")
            print(f"   - Headers: {headers}")
            if data:
                print(f"   - Data: {data}")
            if files:
                print(f"   - Files: {files}")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, headers=headers, data=data, files=files)
                else:
                    response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                if files:
                    response = requests.put(url, headers=headers, data=data, files=files)
                else:
                    response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                if files:
                    response = requests.delete(url, headers=headers, data=data, files=files)
                else:
                    response = requests.delete(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # 응답 정보 출력
            print(f"📥 API 응답:")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Response Headers: {dict(response.headers)}")
            print(f"   - Response Text: {response.text[:500]}...")  # 처음 500자만 출력
            
            response.raise_for_status()
            
            # 빈 응답 처리 (삭제 API 등)
            if not response.text.strip():
                return {"success": True, "message": "요청이 성공적으로 처리되었습니다."}
            
            return response.json()
            
        except RequestException as e:
            print(f"❌ API 요청 실패 상세 정보:")
            print(f"   - URL: {url}")
            print(f"   - Method: {method}")
            print(f"   - Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   - Response Status: {e.response.status_code}")
                print(f"   - Response Text: {e.response.text}")
            raise Exception(f"API 요청 실패: {e}")
    
    # ====================================================================
    # 파일 업로드 Operations
    # ====================================================================
    
    def upload_model_file(self, file_path: str) -> Dict[str, Any]:
        """
        모델 파일 업로드 (self-hosting용)
        
        Args:
            file_path: 업로드할 파일 경로
            
        Returns:
            업로드된 파일 정보 (file_name, temp_file_path 포함)
        """
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, 'application/octet-stream')}
                return self._make_request("POST", "/api/v1/models/files", files=files)
        except FileNotFoundError:
            raise Exception(f"파일을 찾을 수 없습니다: {file_path}")
        except Exception as e:
            raise Exception(f"파일 업로드 실패: {e}")
    
    # ====================================================================
    # 핵심 CRUD Operations
    # ====================================================================
    
    def create_model(self, model_data: Union[ModelCreateRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        모델 생성
        
        Args:
            model_data: 모델 생성 데이터
            
        Returns:
            생성된 모델 정보
        """
        if isinstance(model_data, ModelCreateRequest):
            data = model_data.model_dump(exclude_none=True)
        else:
            data = model_data
            
        return self._make_request("POST", "/api/v1/models", data)
    
    def get_models(self, 
                   page: int = 1, 
                   size: int = 10, 
                   type: Optional[str] = None,
                   serving_type: Optional[str] = None,
                   provider_id: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   languages: Optional[List[str]] = None,
                   tasks: Optional[List[str]] = None,
                   is_private: Optional[bool] = None,
                   is_custom: Optional[bool] = None) -> Dict[str, Any]:
        """
        모델 목록 조회
        
        Args:
            page: 페이지 번호
            size: 페이지 크기
            type: 모델 타입 필터
            serving_type: 서빙 타입 필터
            provider_id: 프로바이더 ID 필터
            tags: 태그 필터
            languages: 언어 필터
            tasks: 태스크 필터
            is_private: 비공개 모델 필터
            is_custom: 커스텀 모델 필터
            
        Returns:
            모델 목록
        """
        params = {
            "page": page,
            "size": size
        }
        
        if type:
            params["type"] = type
        if serving_type:
            params["serving_type"] = serving_type
        if provider_id:
            params["provider_id"] = provider_id
        if tags:
            params["tags"] = ",".join(tags)
        if languages:
            params["languages"] = ",".join(languages)
        if tasks:
            params["tasks"] = ",".join(tasks)
        if is_private is not None:
            params["is_private"] = is_private
        if is_custom is not None:
            params["is_custom"] = is_custom
        
        # GET 요청에 파라미터 추가
        endpoint = "/api/v1/models"
        if params:
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint += f"?{param_str}"
            
        return self._make_request("GET", endpoint)
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        특정 모델 조회
        
        Args:
            model_id: 모델 ID
            
        Returns:
            모델 정보
        """
        return self._make_request("GET", f"/api/v1/models/{model_id}")
    
    def update_model(self, model_id: str, model_data: Union[ModelUpdateRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        모델 업데이트 (태그 제외한 모든 필드를 한 번에 업데이트)
        
        Args:
            model_id: 모델 ID
            model_data: 업데이트할 모델 데이터 (display_name, description, tasks, languages 등 - 태그 제외)
            
        Returns:
            업데이트된 모델 정보
        """
        if isinstance(model_data, ModelUpdateRequest):
            data = model_data.model_dump(exclude_none=True)
        else:
            data = model_data
        
        # 태그 필드 제거 (태그는 별도 API로만 관리)
        if 'tags' in data:
            del data['tags']
            
        return self._make_request("PUT", f"/api/v1/models/{model_id}", data)
    
    def add_tags_to_model(self, model_id: str, tags: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        모델에 태그 추가
        
        Args:
            model_id: 모델 ID
            tags: 추가할 태그 목록 [{"name": "tag1"}, {"name": "tag2"}]
            
        Returns:
            업데이트된 모델 정보
        """
        return self._make_request("PUT", f"/api/v1/models/{model_id}/tags", tags)
    
    def remove_tags_from_model(self, model_id: str, tags: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        모델에서 태그 제거
        
        Args:
            model_id: 모델 ID
            tags: 제거할 태그 목록 [{"name": "tag1"}, {"name": "tag2"}]
            
        Returns:
            업데이트된 모델 정보
        """
        return self._make_request("DELETE", f"/api/v1/models/{model_id}/tags", tags)
    
    def delete_model(self, model_id: str) -> Dict[str, Any]:
        """
        모델 삭제
        
        Args:
            model_id: 모델 ID
            
        Returns:
            삭제 결과
        """
        return self._make_request("DELETE", f"/api/v1/models/{model_id}")
