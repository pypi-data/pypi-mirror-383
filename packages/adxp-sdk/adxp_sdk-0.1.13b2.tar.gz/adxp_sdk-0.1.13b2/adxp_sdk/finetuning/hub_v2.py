"""
Finetuning CRUD Client V2

기존 finetuning 기능을 기반으로 한 파인튜닝 관리 클라이언트입니다.
핵심 CRUD 기능만 제공합니다.
"""

import requests
import os
from typing import Dict, Any, Optional, List, Union
from requests.exceptions import RequestException

try:
    from .schemas_v2 import FinetuningCreateRequest, FinetuningUpdateRequest
except ImportError:
    from schemas_v2 import FinetuningCreateRequest, FinetuningUpdateRequest


class AXFinetuningHubV2:
    """Finetuning CRUD API 클라이언트 V2 - 핵심 CRUD 기능만 제공"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        AXFinetuningHubV2 초기화
        
        Args:
            base_url: API 기본 URL (예: "https://aip-stg.sktai.io")
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
            # 디버깅 정보 출력
            print(f"🔍 API 요청 디버깅:")
            print(f"   - URL: {url}")
            print(f"   - Method: {method}")
            print(f"   - Headers: {self.headers}")
            if data:
                print(f"   - Data: {data}")
            if params:
                print(f"   - Params: {params}")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # 응답 정보 출력
            print(f"📥 API 응답:")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Response Headers: {dict(response.headers)}")
            print(f"   - Response Text: {response.text[:500]}...")  # 처음 500자만 출력
            
            if response.status_code >= 400:
                print(f"❌ API 요청 실패 상세 정보:")
                print(f"   - URL: {url}")
                print(f"   - Method: {method}")
                print(f"   - Error: {response.status_code} {response.reason}")
                print(f"   - Response Status: {response.status_code}")
                print(f"   - Response Text: {response.text}")
                raise RequestException(f"API 요청 실패: {response.status_code} {response.reason} for url: {url}")
            
            # DELETE 요청의 경우 204 No Content를 반환하므로 빈 응답 처리
            if response.status_code == 204:
                return {"message": "삭제 완료", "status_code": 204}
            
            # 응답이 비어있는 경우 처리
            if not response.text.strip():
                return {"message": "요청 완료", "status_code": response.status_code}
            
            return response.json()
            
        except RequestException as e:
            raise e
        except Exception as e:
            raise RequestException(f"API 요청 중 오류 발생: {str(e)}")
    
    def create_training(self, training_data: Union[FinetuningCreateRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        파인튜닝 트레이닝 생성 (기존 create_training 기능)
        
        Args:
            training_data: 트레이닝 생성 데이터
                - name: 트레이닝 이름
                - dataset_ids: 데이터셋 ID 목록
                - base_model_id: 베이스 모델 ID
                - trainer_id: 트레이너 ID
                - resource: 리소스 설정
                - params: 트레이닝 파라미터
                - description: 설명 (선택)
            
        Returns:
            생성된 트레이닝 정보
        """
        if isinstance(training_data, FinetuningCreateRequest):
            data = training_data.model_dump(exclude_none=True)
        else:
            data = training_data
            
        return self._make_request("POST", "/api/v1/finetuning/trainings", data)
    
    def get_trainings(self, 
                     limit: Optional[int] = None,
                     offset: Optional[int] = None,
                     status: Optional[str] = None) -> Dict[str, Any]:
        """
        트레이닝 목록 조회 (기존 get_finetuning_jobs 기능)
        
        Args:
            limit: 조회할 개수
            offset: 시작 위치
            status: 상태 필터
            
        Returns:
            트레이닝 목록
        """
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if status:
            params["status"] = status
        
        endpoint = "/api/v1/finetuning/trainings"
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            endpoint += f"?{query_string}"
        
        return self._make_request("GET", endpoint)
    
    def get_training_by_id(self, training_id: str) -> Dict[str, Any]:
        """
        특정 트레이닝 조회 (기존 get_finetuning_job_by_id 기능)
        
        Args:
            training_id: 트레이닝 ID
            
        Returns:
            트레이닝 정보
        """
        return self._make_request("GET", f"/api/v1/finetuning/trainings/{training_id}")
    
    def update_training(self, training_id: str, training_data: Union[FinetuningUpdateRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        트레이닝 업데이트
        
        Args:
            training_id: 트레이닝 ID
            training_data: 업데이트할 트레이닝 데이터
            
        Returns:
            업데이트된 트레이닝 정보
        """
        if isinstance(training_data, FinetuningUpdateRequest):
            data = training_data.model_dump(exclude_none=True)
        else:
            data = training_data
            
        return self._make_request("PUT", f"/api/v1/finetuning/trainings/{training_id}", data)
    
    def cancel_training(self, training_id: str) -> Dict[str, Any]:
        """
        트레이닝 취소 (기존 cancel_finetuning_job 기능)
        
        Args:
            training_id: 트레이닝 ID
            
        Returns:
            취소 결과
        """
        return self._make_request("POST", f"/api/v1/finetuning/trainings/{training_id}/cancel")
    
    def delete_training(self, training_id: str) -> Dict[str, Any]:
        """
        트레이닝 삭제
        
        Args:
            training_id: 트레이닝 ID
            
        Returns:
            삭제 결과
        """
        return self._make_request("DELETE", f"/api/v1/finetuning/trainings/{training_id}")
    
    def get_training_logs(self, training_id: str, after: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        트레이닝 이벤트/로그 조회 (기존 get_finetuning_logs 기능)
        
        Args:
            training_id: 트레이닝 ID
            after: 특정 시간 이후의 이벤트 필터링 (ISO 8601 형식, 예: "2024-10-22T15:00:00.000Z")
            limit: 반환될 이벤트의 최대 개수 (기본값: 100)
            
        Returns:
            트레이닝 이벤트/로그
        """
        params = {}
        if after:
            params['after'] = after
        if limit:
            params['limit'] = limit
            
        return self._make_request("GET", f"/api/v1/finetuning/trainings/{training_id}/events", params=params)
    
    def get_training_metrics(self, training_id: str) -> Dict[str, Any]:
        """
        트레이닝 메트릭 조회 (기존 get_finetuning_metrics 기능)
        
        Args:
            training_id: 트레이닝 ID
            
        Returns:
            트레이닝 메트릭
        """
        return self._make_request("GET", f"/api/v1/finetuning/trainings/{training_id}/metrics")
