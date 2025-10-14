"""
프롬프트 CRUD Client

API를 통한 프롬프트 관리 기능을 제공하는 클라이언트입니다.
핵심 CRUD 기능만 제공합니다.
"""

import requests
from typing import Dict, Any, Optional, List, Union
from requests.exceptions import RequestException

try:
    from .prompt_schemas import PromptCreateRequest, PromptUpdateRequest
except ImportError:
    try:
        from prompt_schemas import PromptCreateRequest, PromptUpdateRequest
    except ImportError:
        # 예제에서 직접 실행할 때를 위한 fallback
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from prompt_schemas import PromptCreateRequest, PromptUpdateRequest


class PromptClient:
    """프롬프트 CRUD API 클라이언트 - 핵심 CRUD 기능만 제공"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        PromptClient 초기화
        
        Args:
            base_url: API 기본 URL (예: "https://api.example.com")
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
            
            return response.json()
            
        except RequestException as e:
            raise Exception(f"API 요청 실패: {e}")
    
    # ====================================================================
    # 핵심 CRUD Operations
    # ====================================================================
    
    def create_prompt(self, prompt_data: Union[PromptCreateRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        프롬프트 생성

        Args:
            prompt_data: 프롬프트 생성 데이터 (template 필드가 있으면 템플릿 기반 생성)

        Returns:
            생성된 프롬프트 정보
        """
        if isinstance(prompt_data, PromptCreateRequest):
            data = prompt_data.model_dump(exclude_none=True)
        else:
            data = prompt_data.copy()

        # template 필드가 있으면 템플릿 기반으로 처리
        if 'template' in data and data['template']:
            try:
                template_name = data.pop('template')  # template 필드 제거
                project_id = data.get('project_id')
                
                if not project_id:
                    raise Exception("템플릿 사용 시 project_id가 필요합니다.")
                
                # 템플릿 데이터 가져오기
                templates_response = self.get_templates()
                if not templates_response.get('data'):
                    raise Exception("템플릿 목록을 가져올 수 없습니다.")
                
                # 선택된 템플릿 찾기
                template = None
                for t in templates_response['data']:
                    if t.get('name') == template_name:
                        template = t
                        break
                
                if not template:
                    available_templates = [t.get('name') for t in templates_response['data']]
                    raise Exception(f"템플릿 '{template_name}'을 찾을 수 없습니다. 사용 가능한 템플릿: {available_templates}")
                
                # 템플릿 데이터로 메시지와 변수 채우기
                template_variables = template.get('variables', [])
                formatted_variables = []
                for var in template_variables:
                    formatted_var = var.copy()
                    # variable 필드가 {{}} 없이 있다면 추가
                    if 'variable' in formatted_var and not formatted_var['variable'].startswith('{{'):
                        formatted_var['variable'] = f"{{{{{formatted_var['variable']}}}}}"
                    formatted_variables.append(formatted_var)
                
                # 템플릿 데이터로 오버라이드
                data.update({
                    "name": data.get('name', template.get('name', '')),
                    "desc": data.get('desc', f"Template: {template.get('name', '')}"),
                    "messages": template.get('messages', []),
                    "tags": data.get('tags', template.get('tags', [])),
                    "variables": formatted_variables,
                    "release": data.get('release', False)
                })
            except Exception as e:
                # 템플릿 처리 실패 시 원래 데이터로 진행
                print(f"템플릿 처리 실패, 원래 데이터로 진행: {e}")
                pass

        return self._make_request("POST", "/inference-prompts", data)
    
    def get_prompts(self, 
                   project_id: str,
                   page: int = 1, 
                   size: int = 10, 
                   sort: Optional[str] = None,
                   filter: Optional[str] = None,
                   search: Optional[str] = None) -> Dict[str, Any]:
        """
        프롬프트 목록 조회
        
        Args:
            project_id: 프로젝트 ID (필수)
            page: 페이지 번호 (기본값: 1)
            size: 페이지 크기 (기본값: 10)
            sort: 정렬 기준
            filter: 필터 조건
            search: 검색어
            
        Returns:
            프롬프트 목록
        """
        params = {
            "project_id": project_id,
            "page": page,
            "size": size
        }
        
        if sort:
            params["sort"] = sort
        if filter:
            params["filter"] = filter
        if search:
            params["search"] = search
            
        return self._make_request("GET", "/inference-prompts", params=params)
    
    def get_prompt(self, prompt_uuid: str) -> Dict[str, Any]:
        """
        특정 프롬프트 조회
        
        Args:
            prompt_uuid: 프롬프트 UUID
            
        Returns:
            프롬프트 정보
        """
        return self._make_request("GET", f"/inference-prompts/{prompt_uuid}")
    
    def update_prompt(self, prompt_uuid: str, prompt_data: Union[PromptUpdateRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """
        프롬프트 수정
        
        Args:
            prompt_uuid: 프롬프트 UUID
            prompt_data: 수정할 프롬프트 데이터
            
        Returns:
            수정된 프롬프트 정보
        """
        if isinstance(prompt_data, PromptUpdateRequest):
            data = prompt_data.model_dump(exclude_none=True)
        else:
            data = prompt_data
            
        return self._make_request("PUT", f"/inference-prompts/{prompt_uuid}", data)
    
    def delete_prompt(self, prompt_uuid: str) -> Dict[str, Any]:
        """
        프롬프트 삭제

        Args:
            prompt_uuid: 프롬프트 UUID

        Returns:
            삭제 결과
        """
        return self._make_request("DELETE", f"/inference-prompts/{prompt_uuid}")

    # ====================================================================
    # 템플릿 관련 기능
    # ====================================================================

    def get_templates(self) -> Dict[str, Any]:
        """
        내장 템플릿 목록 조회

        Returns:
            템플릿 목록
        """
        return self._make_request("GET", "/inference-prompts/templates/builtin")
