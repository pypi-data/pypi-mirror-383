# USF P1 Chatbot SDK

A Python SDK for interacting with the USF P1 Chatbot API

[![PyPI version](https://badge.fury.io/py/usf-p1-chatbot-sdk.svg)](https://badge.fury.io/py/usf-p1-chatbot-sdk)
[![Python Versions](https://img.shields.io/pypi/pyversions/usf-p1-chatbot-sdk.svg)](https://pypi.org/project/usf-p1-chatbot-sdk/)

## Features

- ✅ **Complete API Coverage** - All 33 endpoints wrapped
- ✅ **Easy to Use** - Simple, intuitive interface
- ✅ **Type Hints** - Full type annotations for IDE support
- ✅ **Async Support** - Streaming chat responses
- ✅ **Production Ready** - Proper error handling and timeouts
- ✅ **Well Documented** - Comprehensive examples and API reference

## Installation

```bash
pip install usf-p1-chatbot-sdk
```

## Quick Start

```python
from usf_p1_chatbot_sdk import ChatbotClient

# Initialize client with your API key and base URL
client = ChatbotClient(
    api_key="your-api-key-here",
    base_url="https://your-api-endpoint.com"
)

# Check API health
health = client.health_check()
print(f"API Status: {health['status']}")

# List collections
collections = client.list_collections()
print(f"Collections: {collections}")

# Create a new collection
collection = client.create_collection(
    collection_name="my_documents",
    description="My document collection"
)
collection_id = collection["collection_info"]["collection_id"]

# Register a patient
patient = client.register_patient(
    collection_id=collection_id,
    patient_name="John Doe",
    age=35,
    gender="M"
)

# Ingest documents from URLs
result = client.ingest_urls(
    collection_id=collection_id,
    urls=["https://example.com/document.html"],
    patient_user_name="John Doe"
)
print(f"Ingestion started: {result['task_id']}")

# Or ingest PDF files
result = client.ingest_pdfs(
    collection_id=collection_id,
    files=["report1.pdf", "report2.pdf", "report3.pdf"],
    patient_user_name="John Doe"
)
print(f"PDF ingestion started: {result['request_id']}")

# Chat with the AI
response = client.chat(
    collection_id=collection_id,
    patient_user_name="John Doe",
    message="What information do you have about me?"
)
print(f"AI Response: {response['response']}")

# Close the client
client.close()
```

## API Reference

### Initialization

```python
client = ChatbotClient(
    api_key="your-api-key",              # Required
    base_url="https://your-api-endpoint.com",  # Required
    timeout=300.0                          # Optional, request timeout in seconds
)
```

### All 33 Available Methods

#### Health Check (1 method)
- `client.health_check()` - Check API health

#### Collections (3 methods)
- `client.create_collection(name, description)` - Create a new collection
- `client.list_collections()` - List all collections
- `client.delete_collection(collection_id)` - Delete a collection

#### Patients (7 methods)
- `client.register_patient(collection_id, patient_name, **data)` - Register a patient
- `client.validate_patient(collection_id, patient_name)` - Validate patient exists
- `client.get_patient(patient_name)` - Get patient information
- `client.delete_patient(patient_name)` - Delete a patient
- `client.list_patients()` - List all patients
- `client.list_patients_by_collection(collection_id)` - List patients in a collection
- `client.get_patient_data_summary(patient_name)` - Get patient data summary

#### Data Ingestion (3 methods)
- `client.ingest_pdfs(collection_id, files, patient_name)` - Ingest PDF files
- `client.ingest_urls(collection_id, urls, patient_name)` - Ingest from URLs
- `client.ingest_default(collection_id, files, urls, patient_name)` - Ingest files and/or URLs

#### Ingestion Status (4 methods)
- `client.get_ingestion_progress(request_id)` - Get ingestion progress
- `client.list_ingestion_requests()` - List recent ingestion requests
- `client.get_ingestion_status()` - Get ingestion service status
- `client.cancel_ingestion_request(request_id)` - Cancel an ingestion request

#### Chat (2 methods)
- `client.chat(collection_id, patient_name, message, ...)` - Send a chat message
- `client.chat_stream(collection_id, patient_name, message, ...)` - Stream chat response (async)

#### Logging (8 methods)
- `client.get_log_collections()` - List log collections
- `client.get_log_stats()` - Get log statistics
- `client.get_recent_logs(limit)` - Get recent logs
- `client.get_logs_from_collection(collection_name, limit)` - Get logs from a collection
- `client.clear_logs_collection(collection_name)` - Clear a log collection
- `client.get_patient_logs(collection_id, patient_name, minutes)` - Get patient logs
- `client.get_patient_logs_from_collection(...)` - Get patient logs from specific collection
- `client.get_logs_by_collection_and_log_collection(...)` - Get logs by collection

#### File Operations (5 methods)
- `client.get_db_files()` - Get all database files
- `client.get_db_files_by_collection(collection_id)` - Get DB files by collection
- `client.get_s3_files()` - Get all S3 files
- `client.get_s3_files_by_collection(collection_id)` - Get S3 files by collection
- `client.delete_document(document_uuid)` - Delete a document

## Advanced Usage

### Context Manager

```python
with ChatbotClient(
    api_key="your-api-key",
    base_url="https://your-api-endpoint.com"
) as client:
    collections = client.list_collections()
    # Client automatically closed
```

### Async Streaming Chat

```python
import asyncio

async def stream_chat():
    client = ChatbotClient(
        api_key="your-api-key",
        base_url="https://your-api-endpoint.com"
    )
    
    async for chunk in client.chat_stream(
        collection_id="col-123",
        patient_user_name="John Doe",
        message="Tell me about my documents"
    ):
        print(chunk, end="", flush=True)
    
    await client.aclose()

asyncio.run(stream_chat())
```

### Error Handling

```python
from usf_p1_chatbot_sdk import ChatbotClient, ChatbotClientError

client = ChatbotClient(
    api_key="your-api-key",
    base_url="https://your-api-endpoint.com"
)

try:
    response = client.chat(
        collection_id="col-123",
        patient_user_name="John Doe",
        message="Hello!"
    )
except ChatbotClientError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    client.close()
```

### Custom Timeout

```python
# Set custom timeout for long-running operations
client = ChatbotClient(
    api_key="your-api-key",
    base_url="https://your-api-endpoint.com",
    timeout=600.0  # 10 minutes
)
```

### PDF Ingestion with Progress Monitoring

```python
from usf_p1_chatbot_sdk import ChatbotClient
import time

client = ChatbotClient(
    api_key="your-api-key",
    base_url="https://your-api-endpoint.com"
)

# Start PDF ingestion
result = client.ingest_pdfs(
    collection_id="col-123",
    files=["report1.pdf", "report2.pdf", "report3.pdf"],
    patient_user_name="John_Doe"  # Use underscores in names
)

request_id = result.get('request_id') or result.get('task_id')
print(f"✅ Ingestion started: {request_id}")

# Monitor progress
print("⏳ Monitoring ingestion progress...")
while True:
    progress = client.get_ingestion_progress(request_id)
    status = progress['status']
    percentage = progress.get('progress_percentage', 0)
    
    print(f"   Status: {status} ({percentage}%)")
    
    if status in ['completed', 'failed']:
        print(f"✅ Ingestion {status}")
        break
    
    time.sleep(5)  # Check every 5 seconds

client.close()
```

## Complete Example

```python
from usf_p1_chatbot_sdk import ChatbotClient
import time

# Initialize
client = ChatbotClient(
    api_key="your-api-key-here",
    base_url="https://your-api-endpoint.com"
)

try:
    # 1. Health check
    health = client.health_check()
    print(f"✅ API Status: {health['status']}")
    
    # 2. Create collection
    collection = client.create_collection("medical_reports", "Patient medical reports")
    cid = collection["collection_info"]["collection_id"]
    print(f"✅ Created collection: {cid}")
    
    # 3. Register patient (use underscores in names)
    patient = client.register_patient(
        collection_id=cid,
        patient_name="John_Doe",
        age=35,
        gender="M",
        blood_type="O+"
    )
    print("✅ Registered patient: John_Doe")
    
    # 4. Ingest PDF documents
    result = client.ingest_pdfs(
        collection_id=cid,
        files=["report1.pdf", "report2.pdf", "report3.pdf"],
        patient_user_name="John_Doe"
    )
    request_id = result.get('request_id') or result.get('task_id')
    print(f"✅ Started PDF ingestion: {request_id}")
    
    # 5. Monitor ingestion progress
    print("⏳ Monitoring ingestion...")
    while True:
        progress = client.get_ingestion_progress(request_id)
        status = progress['status']
        percentage = progress.get('progress_percentage', 0)
        
        print(f"   Status: {status} ({percentage}%)")
        
        if status in ['completed', 'failed']:
            print(f"✅ Ingestion {status}")
            break
        
        time.sleep(5)
    
    # 6. Chat with AI about the documents
    response = client.chat(
        collection_id=cid,
        patient_user_name="John_Doe",
        message="Summarize my medical reports and highlight any concerns."
    )
    print(f"\n💬 AI Response:\n{response['response']}")
    
    # 7. Get patient logs
    logs = client.get_patient_logs(
        collection_id=cid,
        patient_name="John_Doe",
        minutes=60
    )
    print(f"\n✅ Found {len(logs.get('logs', []))} log entries")
    
    # 8. Get patient data summary
    summary = client.get_patient_data_summary("John_Doe")
    print(f"✅ Patient has {summary.get('document_count', 0)} documents")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    client.close()
    print("✅ Client closed")
```

## API Documentation

Contact your API provider for detailed API documentation.

## Requirements

- Python 3.9+
- httpx >= 0.24.0
