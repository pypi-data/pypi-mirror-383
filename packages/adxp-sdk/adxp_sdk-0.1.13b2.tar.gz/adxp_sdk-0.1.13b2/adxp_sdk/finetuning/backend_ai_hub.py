from typing import Dict, Any, Optional, Union, List
import requests
from requests.exceptions import RequestException
from adxp_sdk.auth import TokenCredentials
from .base_hub import BaseFineTuningHub


class BackendAIFineTuningHub(BaseFineTuningHub):
    """
    A class for providing Backend.ai specific fine-tuning functionality.
    
    This class provides access to Backend.ai specific API endpoints for training management.
    """

    def __init__(
        self,
        credentials: Union[TokenCredentials, None] = None,
        headers: Optional[Dict[str, str]] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the Backend.ai fine-tuning hub object.

        Args:
            credentials: Authentication information (deprecated, use headers and base_url instead)
            headers: HTTP headers for authentication
            base_url: Base URL of the API
        """
        super().__init__(credentials, headers, base_url)

    # ====================================================================
    # Backend.ai Training Management
    # ====================================================================

    def create_backend_ai_training(
        self, 
        training_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new Backend.ai training via POST /api/v1/backend-ai/finetuning/trainings
        
        Args:
            training_data (Dict[str, Any]): Training creation data
                Required fields:
                - name (str): Training name
                - dataset_ids (List[str]): List of dataset IDs(uuids) for training
                - base_model_id (str): Base model ID(uuid) for fine-tuning
                - trainer_id (str): Trainer ID(uuid) for the training
                - resource (Dict[str, Any]): Resource configuration (e.g., {"cpu_quota": 2, "mem_quota": 8, "gpu_quota": 1.0})
                - params (str): Training parameters in string format
                
                Optional fields:
                - id (str, optional): Training ID (UUID, auto-generated if not provided)
                - description (str, optional): Training description
                - envs (Dict[str, Any], optional): Environment variables
                - is_auto_model_creation (bool, optional): Auto model creation after training (default: false)
                - policy (List[Dict], optional): Access policy configuration
                - project_id (str, optional): Project ID(uuid)

        Returns:
            dict: The API response containing created training data

        Raises:
            RequestException: If the API request fails
            ValueError: If training_data is empty or invalid
        """
        try:
            # Validate training_data
            required_fields = ['name', 'dataset_ids', 'base_model_id', 'trainer_id', 'resource', 'params']
            self._validate_required_fields(training_data, required_fields)
            
            # Validate dataset_ids is a list
            dataset_ids = training_data.get('dataset_ids')
            if not isinstance(dataset_ids, list) or not dataset_ids:
                raise ValueError("dataset_ids must be a non-empty list of strings")
            
            # Validate resource is a dict
            resource = training_data.get('resource')
            if not isinstance(resource, dict):
                raise ValueError("resource must be a dictionary")
            
            # Validate resource structure (actual API format)
            if 'cpu_quota' in resource or 'gpu_quota' in resource:
                # Actual API format: {"cpu_quota": 2, "mem_quota": 8, "gpu_quota": 1.0}
                if 'gpu_quota' in resource and not isinstance(resource.get('gpu_quota'), (int, float)):
                    raise ValueError("gpu_quota must be a number (int or float)")
                if 'cpu_quota' in resource and not isinstance(resource.get('cpu_quota'), int):
                    raise ValueError("cpu_quota must be an integer")
                if 'mem_quota' in resource and not isinstance(resource.get('mem_quota'), int):
                    raise ValueError("mem_quota must be an integer")
                if 'gpu_type' in resource and not isinstance(resource.get('gpu_type'), str):
                    raise ValueError("gpu_type must be a string")
            elif 'type' in resource and 'count' in resource:
                # Alternative format: {"type": "gpu", "count": 1}
                if not isinstance(resource.get('type'), str) or not isinstance(resource.get('count'), (int, float)):
                    raise ValueError("resource with 'type' and 'count' must have string type and numeric count")
            else:
                raise ValueError("resource must contain quota fields (cpu_quota, gpu_quota, etc.) or type/count fields")
            
            # Validate params is a string
            if not isinstance(training_data.get('params'), str):
                raise ValueError("params must be a string")
            
            # Validate optional fields if provided
            if 'id' in training_data and not isinstance(training_data.get('id'), str):
                raise ValueError("id must be a string (UUID)")
            
            if 'description' in training_data and not isinstance(training_data.get('description'), str):
                raise ValueError("description must be a string")
            
            if 'envs' in training_data and not isinstance(training_data.get('envs'), dict):
                raise ValueError("envs must be a dictionary")
            
            if 'is_auto_model_creation' in training_data and not isinstance(training_data.get('is_auto_model_creation'), bool):
                raise ValueError("is_auto_model_creation must be a boolean")
            
            if 'policy' in training_data and not isinstance(training_data.get('policy'), list):
                raise ValueError("policy must be a list")
            
            if 'project_id' in training_data and not isinstance(training_data.get('project_id'), str):
                raise ValueError("project_id must be a string")
            
            # Make API request
            try:
                result = self._make_request(
                    method="POST",
                    endpoint="/api/v1/backend-ai/finetuning/trainings",
                    json_data=training_data
                )
            except RequestException as e:
                # Handle specific server errors
                error_str = str(e)
                if "400" in error_str:
                    if "Private trainer requires uploaded script file" in error_str:
                        raise RequestException(
                            f"Bad request: {error_str}. "
                            f"Private trainer requires uploaded script file."
                        )
                    else:
                        raise RequestException(
                            f"Bad request: {error_str}. "
                            f"Please check your training_data format and required fields."
                        )
                elif "404" in error_str:
                    raise RequestException(
                        f"Not found: {error_str}. "
                        f"Trainer not found. Please use the registered trainer."
                    )
                elif "409" in error_str:
                    raise RequestException(
                        f"Conflict: {error_str}. "
                        f"Training ID already exists. Please use a different ID or omit it for auto-generation."
                    )
                elif "422" in error_str:
                    raise RequestException(
                        f"Validation error: {error_str}. "
                        f"Please check your training_data format and required fields."
                    )
                elif "500" in error_str:
                    raise RequestException(
                        f"Internal server error: {error_str}. "
                        f"Failed to register training. Please try again later."
                    )
                raise
            
            # Ensure response has expected structure
            if not isinstance(result, dict):
                raise RequestException("Invalid response format from API")
            
            # Validate response contains expected fields
            expected_fields = ['id', 'name', 'status', 'dataset_ids', 'base_model_id', 'trainer_id', 'resource', 'params']
            missing_response_fields = [field for field in expected_fields if field not in result]
            if missing_response_fields:
                raise RequestException(f"API response missing expected fields: {missing_response_fields}")
            
            # Validate critical fields
            if not result.get('id'):
                raise RequestException("API response missing training ID")
            
            if not result.get('name'):
                raise RequestException("API response missing training name")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise RequestException(f"Failed to create Backend.ai training: {str(e)}")

    def list_backend_ai_trainings(
        self,
        page: int = 1,
        size: int = 10,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List Backend.ai trainings via GET /api/v1/backend-ai/finetuning/trainings
        
        Args:
            page (int): Page number (default: 1)
            size (int): Number of trainings per page (default: 10)
            sort (str, optional): Sort field (e.g., "created_at,desc")
            filter (str, optional): Filter criteria (e.g., "status:running")
            search (str, optional): Search term

        Returns:
            dict: The API response containing list of trainings with pagination

        Raises:
            RequestException: If the API request fails
            ValueError: If pagination parameters are invalid
        """
        try:
            # Validate pagination parameters
            self._validate_pagination_params(page, size)
            
            # Prepare query parameters
            params = {
                'page': page,
                'size': size
            }
            if sort:
                params['sort'] = sort
            if filter:
                params['filter'] = filter
            if search:
                params['search'] = search
            
            # Make API request
            result = self._make_request(
                method="GET",
                endpoint="/api/v1/backend-ai/finetuning/trainings",
                params=params
            )
            
            return result
            
        except RequestException:
            raise
        except Exception as e:
            raise RequestException(f"Failed to list Backend.ai trainings: {str(e)}")

    def get_backend_ai_training(self, training_id: str) -> Dict[str, Any]:
        """
        Get Backend.ai training details via GET /api/v1/backend-ai/finetuning/trainings/{training_id}
        
        Args:
            training_id (str): Training ID (uuid)

        Returns:
            dict: The API response containing training details

        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is invalid
        """
        try:
            # Validate training_id
            self._validate_uuid(training_id, "training_id")
            
            # Make API request
            result = self._make_request(
                method="GET",
                endpoint=f"/api/v1/backend-ai/finetuning/trainings/{training_id}"
            )
            
            if not result.get('id'):
                raise RequestException("API response missing training ID")
            
            return result
            
        except RequestException:
            raise
        except Exception as e:
            raise RequestException(f"Failed to get Backend.ai training {training_id}: {str(e)}")

    def update_backend_ai_training(self, training_id: str, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update Backend.ai training via PUT /api/v1/backend-ai/finetuning/trainings/{training_id}
        
        Args:
            training_id (str): Training ID (uuid)
            training_data (Dict[str, Any]): Training update data
                Optional fields:
                - name (str): Training name
                - description (str): Training description
                - status (str): Training status

        Returns:
            dict: The API response containing updated training data

        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is invalid or training_data is empty
        """
        try:
            # Validate training_id
            self._validate_uuid(training_id, "training_id")
            
            # Validate training_data
            if not training_data or not isinstance(training_data, dict):
                raise ValueError("training_data must be a non-empty dictionary")
            
            # Make API request
            result = self._make_request(
                method="PUT",
                endpoint=f"/api/v1/backend-ai/finetuning/trainings/{training_id}",
                json_data=training_data
            )
            
            if not result.get('id'):
                raise RequestException("API response missing training ID")
            
            return result
            
        except RequestException:
            raise
        except Exception as e:
            raise RequestException(f"Failed to update Backend.ai training {training_id}: {str(e)}")

    def delete_backend_ai_training(self, training_id: str) -> bool:
        """
        Delete Backend.ai training via DELETE /api/v1/backend-ai/finetuning/trainings/{training_id}
        
        Args:
            training_id (str): Training ID (uuid)

        Returns:
            bool: True if deletion was successful

        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is invalid
        """
        try:
            # Validate training_id
            self._validate_uuid(training_id, "training_id")
            
            # Make API request
            self._make_request(
                method="DELETE",
                endpoint=f"/api/v1/backend-ai/finetuning/trainings/{training_id}"
            )
            
            return True
            
        except RequestException:
            raise
        except Exception as e:
            raise RequestException(f"Failed to delete Backend.ai training {training_id}: {str(e)}")

    def get_backend_ai_training_status(self, training_id: str) -> Dict[str, Any]:
        """
        Get Backend.ai training status via GET /api/v1/backend-ai/finetuning/trainings/{training_id}/status
        
        Args:
            training_id (str): Training ID (uuid)

        Returns:
            dict: The API response containing training status

        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is invalid
        """
        try:
            # Validate training_id
            self._validate_uuid(training_id, "training_id")
            
            # Make API request
            result = self._make_request(
                method="GET",
                endpoint=f"/api/v1/backend-ai/finetuning/trainings/{training_id}/status"
            )
            
            return result
            
        except RequestException:
            raise
        except Exception as e:
            raise RequestException(f"Failed to get Backend.ai training status {training_id}: {str(e)}")

    def get_backend_ai_training_events(
        self, 
        training_id: str, 
        after: Optional[str] = None, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get Backend.ai training events via GET /api/v1/backend-ai/finetuning/trainings/{training_id}/events
        
        Args:
            training_id (str): Training ID (uuid)
            after (str, optional): Get events after this timestamp (e.g., "2024-10-22T15:00:00.000Z")
            limit (int): Limit number of events (default: 100, max: 1000)

        Returns:
            dict: The API response containing training events

        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is invalid or limit is invalid
        """
        try:
            # Validate training_id
            self._validate_uuid(training_id, "training_id")
            
            # Validate limit
            if not isinstance(limit, int) or limit < 1 or limit > 1000:
                raise ValueError("limit must be an integer between 1 and 1000")
            
            # Prepare query parameters
            params = {'limit': limit}
            if after:
                params['after'] = after
            
            # Make API request
            result = self._make_request(
                method="GET",
                endpoint=f"/api/v1/backend-ai/finetuning/trainings/{training_id}/events",
                params=params
            )
            
            return result
            
        except RequestException:
            raise
        except Exception as e:
            raise RequestException(f"Failed to get Backend.ai training events {training_id}: {str(e)}")

    def get_backend_ai_training_metrics(
        self, 
        training_id: str, 
        type: str = "train", 
        page: int = 1, 
        size: int = 10
    ) -> Dict[str, Any]:
        """
        Get Backend.ai training metrics via GET /api/v1/backend-ai/finetuning/trainings/{training_id}/metrics
        
        Args:
            training_id (str): Training ID (uuid)
            type (str): Metric type (default: "train")
            page (int): Page number (default: 1)
            size (int): Number of metrics per page (default: 10)

        Returns:
            dict: The API response containing training metrics with pagination

        Raises:
            RequestException: If the API request fails
            ValueError: If parameters are invalid
        """
        try:
            # Validate training_id
            self._validate_uuid(training_id, "training_id")
            
            # Validate pagination parameters
            self._validate_pagination_params(page, size)
            
            # Prepare query parameters
            params = {
                'type': type,
                'page': page,
                'size': size
            }
            
            # Make API request
            result = self._make_request(
                method="GET",
                endpoint=f"/api/v1/backend-ai/finetuning/trainings/{training_id}/metrics",
                params=params
            )
            
            return result
            
        except RequestException:
            raise
        except Exception as e:
            raise RequestException(f"Failed to get Backend.ai training metrics {training_id}: {str(e)}")

    def force_stop_backend_ai_training(self, training_id: str) -> Dict[str, Any]:
        """
        Force stop Backend.ai training via POST /api/v1/backend-ai/finetuning/trainings/{training_id}/force-stop
        
        Args:
            training_id (str): Training ID (uuid)

        Returns:
            dict: The API response

        Raises:
            RequestException: If the API request fails
            ValueError: If training_id is invalid
        """
        try:
            # Validate training_id
            self._validate_uuid(training_id, "training_id")
            
            # Make API request
            result = self._make_request(
                method="POST",
                endpoint=f"/api/v1/backend-ai/finetuning/trainings/{training_id}/force-stop"
            )
            
            return result
            
        except RequestException:
            raise
        except Exception as e:
            raise RequestException(f"Failed to force stop Backend.ai training {training_id}: {str(e)}")

    # ====================================================================
    # Platform Type and Common APIs
    # ====================================================================

    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get platform information via GET /api/v1/finetuning/trainers/platform-info
        
        Returns:
            dict: The API response containing platform information
                Structure:
                {
                    "platform_type": "axp" | "backend_ai",  # Platform type
                    "base_url": "string"                     # AXP base URL (Backend.ai only)
                }
                
        Raises:
            RequestException: If the API request fails
        """
        try:
            result = self._make_request(
                method="GET",
                endpoint="/api/v1/finetuning/trainers/platform-info"
            )
            
            # Ensure response has expected structure
            if not isinstance(result, dict):
                raise RequestException("Invalid response format from API")
            
            # Validate response contains required fields
            if 'platform_type' not in result:
                raise RequestException("API response missing platform_type field")
            
            # Validate platform_type value
            valid_platform_types = ['axp', 'backend_ai']
            if result['platform_type'] not in valid_platform_types:
                raise RequestException(f"Invalid platform_type: {result['platform_type']}")
            
            return result
            
        except RequestException:
            raise
        except Exception as e:
            raise RequestException(f"Failed to get platform info: {str(e)}")
