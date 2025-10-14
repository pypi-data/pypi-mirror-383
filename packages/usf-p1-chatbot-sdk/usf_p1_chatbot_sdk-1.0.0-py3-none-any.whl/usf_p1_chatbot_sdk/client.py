"""
USF P1 Chatbot SDK Client

Complete Python client for USF P1 Chatbot API with all 33 endpoints.
Connects to the deployed API at https://api-civie.us.inc

Example:
    >>> from usf_p1_chatbot_sdk import ChatbotClient
    >>> 
    >>> client = ChatbotClient(api_key="your-api-key")
    >>> health = client.health_check()
    >>> collections = client.list_collections()
"""

import httpx
from typing import List, Dict, Any, Optional, Union
import json
from pathlib import Path


class ChatbotClientError(Exception):
    """Base exception for Chatbot Client errors"""
    pass


class ChatbotClient:
    """
    Complete Python client for USF P1 Chatbot API with ALL 33 endpoints.
    
    Args:
        api_key: API key for authentication (required)
        base_url: Base URL of the API (default: https://api-civie.us.inc)
        timeout: Request timeout in seconds (default: 300)
        
    Example:
        >>> client = ChatbotClient(api_key="your-api-key")
        >>> health = client.health_check()
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api-civie.us.inc",
        timeout: float = 300.0
    ):
        if not api_key:
            raise ValueError("api_key is required")
            
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        
        self.client = httpx.Client(timeout=timeout, headers=self._get_headers())
        self.async_client = httpx.AsyncClient(timeout=timeout, headers=self._get_headers())
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        return headers
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_json = json.loads(e.response.text)
                error_message = error_json.get("detail", e.response.text)
            except:
                error_message = e.response.text
            raise ChatbotClientError(f"API Error: {error_message}") from e
        except json.JSONDecodeError:
            return {"status": "success", "response": response.text}
    
    # ==================== 1. HEALTH CHECK (1 endpoint) ====================
    
    def health_check(self) -> Dict[str, Any]:
        """GET /health - Check API health status"""
        response = self.client.get(f"{self.base_url}/health")
        return self._handle_response(response)
    
    # ==================== 2. CHAT (2 endpoints) ====================
    
    def chat(
        self,
        collection_id: str,
        patient_user_name: str,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        include_uuids: Optional[List[str]] = None,
        exclude_uuids: Optional[List[str]] = None,
        k: int = 3
    ) -> Dict[str, Any]:
        """POST /api/chat - Conversational chat endpoint"""
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"user": message})
        
        data = {
            "messages": messages,
            "collection_id": collection_id,
            "patient_user_name": patient_user_name,
            "k": k
        }
        if include_uuids:
            data["include_uuids"] = include_uuids
        if exclude_uuids:
            data["exclude_uuids"] = exclude_uuids
        
        response = self.client.post(f"{self.base_url}/api/chat", json=data)
        return self._handle_response(response)
    
    async def chat_stream(
        self,
        collection_id: str,
        patient_user_name: str,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        include_uuids: Optional[List[str]] = None,
        exclude_uuids: Optional[List[str]] = None
    ):
        """POST /api/chat/stream - Streaming chat endpoint"""
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"user": message})
        
        data = {
            "messages": messages,
            "collection_id": collection_id,
            "patient_user_name": patient_user_name
        }
        if include_uuids:
            data["include_uuids"] = include_uuids
        if exclude_uuids:
            data["exclude_uuids"] = exclude_uuids
        
        async with self.async_client.stream("POST", f"{self.base_url}/api/chat/stream", json=data) as response:
            response.raise_for_status()
            async for chunk in response.aiter_text():
                if chunk:
                    yield chunk
    
    # ==================== 3. DATA INGESTION (3 endpoints) ====================
    
    def ingest_pdfs(
        self,
        collection_id: str,
        files: List[Union[str, Path]],
        patient_user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """POST /api/data/async/pdfs - Ingest PDF files"""
        file_objects = []
        for file_path in files:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            file_objects.append(("files", (file_path.name, open(file_path, "rb"), "application/pdf")))
        
        data = {"collection_id": collection_id}
        if patient_user_name:
            data["patient_user_name"] = patient_user_name
        
        response = self.client.post(f"{self.base_url}/api/data/async/pdfs", data=data, files=file_objects)
        
        for _, file_tuple in file_objects:
            file_tuple[1].close()
        
        return self._handle_response(response)
    
    def ingest_urls(
        self,
        collection_id: str,
        urls: List[str],
        patient_user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """POST /api/data/async/urls - Ingest content from URLs"""
        data = {"collection_id": collection_id, "urls": urls}
        if patient_user_name:
            data["patient_user_name"] = patient_user_name
        
        response = self.client.post(f"{self.base_url}/api/data/async/urls", json=data)
        return self._handle_response(response)
    
    def ingest_default(
        self,
        collection_id: str,
        files: Optional[List[Union[str, Path]]] = None,
        urls: Optional[List[str]] = None,
        patient_user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """POST /api/data/async - Default data ingestion (PDFs and/or URLs)"""
        file_objects = []
        if files:
            for file_path in files:
                file_path = Path(file_path)
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                file_objects.append(("files", (file_path.name, open(file_path, "rb"), "application/pdf")))
        
        data = {"collection_id": collection_id}
        if patient_user_name:
            data["patient_user_name"] = patient_user_name
        if urls:
            data["urls"] = urls
        
        response = self.client.post(f"{self.base_url}/api/data/async", data=data, files=file_objects if file_objects else None)
        
        for _, file_tuple in file_objects:
            file_tuple[1].close()
        
        return self._handle_response(response)
    
    # ==================== 4. INGESTION STATUS (4 endpoints) ====================
    
    def get_ingestion_progress(self, request_id: str) -> Dict[str, Any]:
        """GET /api/data/progress/{request_id} - Get ingestion progress"""
        response = self.client.get(f"{self.base_url}/api/data/progress/{request_id}")
        return self._handle_response(response)
    
    def list_ingestion_requests(self) -> Dict[str, Any]:
        """GET /api/data/requests - List recent ingestion requests"""
        response = self.client.get(f"{self.base_url}/api/data/requests")
        return self._handle_response(response)
    
    def get_ingestion_status(self) -> Dict[str, Any]:
        """GET /api/data/status - Get ingestion service status"""
        response = self.client.get(f"{self.base_url}/api/data/status")
        return self._handle_response(response)
    
    def cancel_ingestion_request(self, request_id: str) -> Dict[str, Any]:
        """DELETE /api/data/request/{request_id} - Cancel ingestion request"""
        response = self.client.delete(f"{self.base_url}/api/data/request/{request_id}")
        return self._handle_response(response)
    
    # ==================== 5. LOGGING (8 endpoints) ====================
    
    def get_log_collections(self) -> Dict[str, Any]:
        """GET /api/logs/collections - List all log collections"""
        response = self.client.get(f"{self.base_url}/api/logs/collections")
        return self._handle_response(response)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """GET /api/logs/stats - Get log statistics"""
        response = self.client.get(f"{self.base_url}/api/logs/stats")
        return self._handle_response(response)
    
    def get_recent_logs(self, limit: int = 100) -> Dict[str, Any]:
        """GET /api/logs/recent - Get recent logs"""
        response = self.client.get(f"{self.base_url}/api/logs/recent", params={"limit": limit})
        return self._handle_response(response)
    
    def get_logs_from_collection(self, collection_name: str, limit: int = 100) -> Dict[str, Any]:
        """GET /api/logs/{collection_name} - Get logs from specific collection"""
        response = self.client.get(f"{self.base_url}/api/logs/{collection_name}", params={"limit": limit})
        return self._handle_response(response)
    
    def clear_logs_collection(self, collection_name: str) -> Dict[str, Any]:
        """DELETE /api/logs/{collection_name} - Clear logs collection"""
        response = self.client.delete(f"{self.base_url}/api/logs/{collection_name}")
        return self._handle_response(response)
    
    def get_patient_logs(self, collection_id: str, patient_name: str, minutes: int = 60) -> Dict[str, Any]:
        """GET /api/logs/patient-recent/{collection_id}/{patient_user_name} - Get patient recent logs"""
        response = self.client.get(
            f"{self.base_url}/api/logs/patient-recent/{collection_id}/{patient_name}",
            params={"minutes": minutes}
        )
        return self._handle_response(response)
    
    def get_patient_logs_from_collection(
        self,
        collection_id: str,
        patient_name: str,
        log_collection_name: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """GET /api/logs/patient-from-collection/{collection_id}/{patient_user_name}/{log_collection_name}"""
        response = self.client.get(
            f"{self.base_url}/api/logs/patient-from-collection/{collection_id}/{patient_name}/{log_collection_name}",
            params={"limit": limit}
        )
        return self._handle_response(response)
    
    def get_logs_by_collection_and_log_collection(
        self,
        collection_id: str,
        log_collection_name: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """GET /api/logs/collection-specific/{collection_id}/{log_collection_name}"""
        response = self.client.get(
            f"{self.base_url}/api/logs/collection-specific/{collection_id}/{log_collection_name}",
            params={"limit": limit}
        )
        return self._handle_response(response)
    
    # ==================== 6. COLLECTIONS (3 endpoints) ====================
    
    def create_collection(self, collection_name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """POST /api/collections - Create new collection"""
        data = {"collection_name": collection_name, "description": description or ""}
        response = self.client.post(f"{self.base_url}/api/collections", json=data)
        return self._handle_response(response)
    
    def list_collections(self) -> Dict[str, Any]:
        """GET /api/collections - List all collections"""
        response = self.client.get(f"{self.base_url}/api/collections")
        return self._handle_response(response)
    
    def delete_collection(self, collection_id: str) -> Dict[str, Any]:
        """DELETE /api/collections/{collection_id} - Delete collection"""
        response = self.client.delete(f"{self.base_url}/api/collections/{collection_id}")
        return self._handle_response(response)
    
    # ==================== 7. FILE OPERATIONS (5 endpoints) ====================
    
    def get_db_files(self) -> Dict[str, Any]:
        """GET /api/db/files - Get all database files"""
        response = self.client.get(f"{self.base_url}/api/db/files")
        return self._handle_response(response)
    
    def get_db_files_by_collection(self, collection_id: str) -> Dict[str, Any]:
        """GET /api/db/files/{collection_id} - Get database files by collection"""
        response = self.client.get(f"{self.base_url}/api/db/files/{collection_id}")
        return self._handle_response(response)
    
    def get_s3_files(self) -> Dict[str, Any]:
        """GET /api/s3/files - Get all S3 files"""
        response = self.client.get(f"{self.base_url}/api/s3/files")
        return self._handle_response(response)
    
    def get_s3_files_by_collection(self, collection_id: str) -> Dict[str, Any]:
        """GET /api/s3/files/{collection_id} - Get S3 files by collection"""
        response = self.client.get(f"{self.base_url}/api/s3/files/{collection_id}")
        return self._handle_response(response)
    
    def delete_document(self, document_uuid: str) -> Dict[str, Any]:
        """DELETE /api/document/{document_uuid} - Delete document by UUID"""
        response = self.client.delete(f"{self.base_url}/api/document/{document_uuid}")
        return self._handle_response(response)
    
    # ==================== 8. PATIENT MANAGEMENT (7 endpoints) ====================
    
    def register_patient(
        self,
        collection_id: str,
        patient_name: str,
        **additional_data
    ) -> Dict[str, Any]:
        """POST /api/patient/register - Register new patient"""
        data = {"collection_id": collection_id, "patient_user_name": patient_name, **additional_data}
        response = self.client.post(f"{self.base_url}/api/patient/register", json=data)
        return self._handle_response(response)
    
    def validate_patient(self, collection_id: str, patient_name: str) -> Dict[str, Any]:
        """POST /api/patient/validate - Validate patient exists"""
        data = {"collection_id": collection_id, "patient_user_name": patient_name}
        response = self.client.post(f"{self.base_url}/api/patient/validate", json=data)
        return self._handle_response(response)
    
    def get_patient(self, patient_name: str) -> Dict[str, Any]:
        """GET /api/patient/{patient_user_name} - Get patient information"""
        response = self.client.get(f"{self.base_url}/api/patient/{patient_name}")
        return self._handle_response(response)
    
    def delete_patient(self, patient_name: str) -> Dict[str, Any]:
        """DELETE /api/patient/{patient_user_name} - Delete patient and all data"""
        response = self.client.delete(f"{self.base_url}/api/patient/{patient_name}")
        return self._handle_response(response)
    
    def list_patients(self) -> Dict[str, Any]:
        """GET /api/patients - List all patients"""
        response = self.client.get(f"{self.base_url}/api/patients")
        return self._handle_response(response)
    
    def list_patients_by_collection(self, collection_id: str) -> Dict[str, Any]:
        """GET /api/patients/collection/{collection_id} - List patients by collection"""
        response = self.client.get(f"{self.base_url}/api/patients/collection/{collection_id}")
        return self._handle_response(response)
    
    def get_patient_data_summary(self, patient_name: str) -> Dict[str, Any]:
        """GET /api/patient/{patient_user_name}/data - Get patient data summary"""
        response = self.client.get(f"{self.base_url}/api/patient/{patient_name}/data")
        return self._handle_response(response)
    
    # ==================== UTILITY METHODS ====================
    
    def close(self):
        """Close HTTP clients"""
        self.client.close()
    
    async def aclose(self):
        """Close async HTTP client"""
        await self.async_client.aclose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
