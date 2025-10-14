"""
Model 관련 스키마 정의 V2
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
from enum import Enum


class ModelType(str, Enum):
    """모델 타입"""
    LANGUAGE = "language"
    EMBEDDING = "embedding"
    IMAGE = "image"
    MULTIMODAL = "multimodal"
    RERANKER = "reranker"
    STT = "stt"
    TTS = "tts"
    AUDIO = "audio"
    CODE = "code"
    VISION = "vision"
    VIDEO = "video"


class ServingType(str, Enum):
    """서빙 타입"""
    SERVERLESS = "serverless"
    SELF_HOSTING = "self-hosting"


class ModelCreateRequest(BaseModel):
    """모델 생성 요청"""
    name: str = Field(description="모델 이름")
    type: ModelType = Field(description="모델 타입")
    provider_id: str = Field(description="프로바이더 ID")
    serving_type: ServingType = Field(description="서빙 타입")
    
    # 필수 조건부 파라미터
    path: Optional[str] = Field(None, description="모델 파일 경로 (self-hosting 필수)")
    endpoint_url: Optional[str] = Field(None, description="엔드포인트 URL (serverless 필수)")
    endpoint_identifier: Optional[str] = Field(None, description="엔드포인트 식별자 (serverless 필수)")
    endpoint_key: Optional[str] = Field(None, description="엔드포인트 키 (serverless 필수)")
    
    # 선택 파라미터
    display_name: Optional[str] = Field(None, description="표시 이름")
    description: Optional[str] = Field(None, description="모델 설명")
    size: Optional[str] = Field(None, description="모델 크기")
    token_size: Optional[str] = Field(None, description="토큰 크기")
    license: Optional[str] = Field(None, description="라이선스 정보")
    readme: Optional[str] = Field(None, description="README 내용")
    tags: Optional[List[Dict[str, str]]] = Field(None, description="태그 목록")
    languages: Optional[List[Dict[str, str]]] = Field(None, description="언어 목록")
    tasks: Optional[List[Dict[str, str]]] = Field(None, description="태스크 목록")
    inference_param: Optional[Dict[str, Any]] = Field(None, description="추론 파라미터")
    quantization: Optional[Dict[str, Any]] = Field(None, description="양자화 파라미터")
    dtype: Optional[str] = Field(None, description="데이터 타입")
    default_params: Optional[Dict[str, Any]] = Field(None, description="기본 파라미터")
    is_private: Optional[bool] = Field(False, description="비공개 모델 여부")
    is_custom: Optional[bool] = Field(False, description="커스텀 모델 여부")
    
    # 커스텀 모델 관련
    custom_code_path: Optional[str] = Field(None, description="커스텀 코드 경로")
    custom_runtime_image_url: Optional[str] = Field(None, description="커스텀 런타임 이미지 URL")
    custom_runtime_use_bash: Optional[bool] = Field(False, description="커스텀 런타임 bash 사용 여부")
    custom_runtime_command: Optional[List[str]] = Field(None, description="커스텀 런타임 명령어")
    custom_runtime_args: Optional[List[str]] = Field(None, description="커스텀 런타임 인자")
    
    # self-hosting 관련 (이미지에서 본 구조에 맞춤)
    custom_runtime: Optional[Dict[str, Any]] = Field(None, description="커스텀 런타임 설정")
    endpoints: Optional[Dict[str, Any]] = Field(None, description="엔드포인트 설정")
    
    # 엔드포인트 관련 (serverless용)
    endpoint_description: Optional[str] = Field(None, description="엔드포인트 설명")


class ModelUpdateRequest(BaseModel):
    """모델 업데이트 요청"""
    display_name: Optional[str] = Field(None, description="표시 이름")
    description: Optional[str] = Field(None, description="모델 설명")
    size: Optional[str] = Field(None, description="모델 크기")
    token_size: Optional[str] = Field(None, description="토큰 크기")
    license: Optional[str] = Field(None, description="라이선스 정보")
    readme: Optional[str] = Field(None, description="README 내용")
    tags: Optional[List[Dict[str, str]]] = Field(None, description="태그 목록")
    languages: Optional[List[Dict[str, str]]] = Field(None, description="언어 목록")
    tasks: Optional[List[Dict[str, str]]] = Field(None, description="태스크 목록")
    inference_param: Optional[Dict[str, Any]] = Field(None, description="추론 파라미터")
    quantization: Optional[Dict[str, Any]] = Field(None, description="양자화 파라미터")
    dtype: Optional[str] = Field(None, description="데이터 타입")
    default_params: Optional[Dict[str, Any]] = Field(None, description="기본 파라미터")
    is_private: Optional[bool] = Field(None, description="비공개 모델 여부")


class ModelResponse(BaseModel):
    """모델 응답"""
    id: str = Field(description="모델 ID")
    name: str = Field(description="모델 이름")
    display_name: Optional[str] = Field(None, description="표시 이름")
    type: str = Field(description="모델 타입")
    serving_type: str = Field(description="서빙 타입")
    provider_id: str = Field(description="프로바이더 ID")
    description: Optional[str] = Field(None, description="모델 설명")
    size: Optional[str] = Field(None, description="모델 크기")
    token_size: Optional[str] = Field(None, description="토큰 크기")
    license: Optional[str] = Field(None, description="라이선스 정보")
    readme: Optional[str] = Field(None, description="README 내용")
    tags: Optional[List[Dict[str, str]]] = Field(None, description="태그 목록")
    languages: Optional[List[Dict[str, str]]] = Field(None, description="언어 목록")
    tasks: Optional[List[Dict[str, str]]] = Field(None, description="태스크 목록")
    inference_param: Optional[Dict[str, Any]] = Field(None, description="추론 파라미터")
    quantization: Optional[Dict[str, Any]] = Field(None, description="양자화 파라미터")
    dtype: Optional[str] = Field(None, description="데이터 타입")
    default_params: Optional[Dict[str, Any]] = Field(None, description="기본 파라미터")
    is_private: bool = Field(False, description="비공개 모델 여부")
    is_custom: bool = Field(False, description="커스텀 모델 여부")
    created_at: Optional[str] = Field(None, description="생성 시간")
    updated_at: Optional[str] = Field(None, description="업데이트 시간")
    custom_runtime: Optional[Dict[str, Any]] = Field(None, description="커스텀 런타임 정보")
