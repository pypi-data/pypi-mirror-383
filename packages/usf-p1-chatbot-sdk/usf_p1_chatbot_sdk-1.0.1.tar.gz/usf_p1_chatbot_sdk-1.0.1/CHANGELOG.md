# Changelog

All notable changes to the USF P1 Chatbot SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-01-14

### Fixed
- **CRITICAL BUG**: Fixed PDF ingestion functionality that was broken in v1.0.0
  - Removed hardcoded `Content-Type: application/json` header from default headers
  - This header was preventing multipart/form-data uploads from working correctly
  - `ingest_pdfs()` and `ingest_default()` methods now work as expected
  - httpx now correctly sets `Content-Type: multipart/form-data` with proper boundary for file uploads

### Changed
- Updated internal header management to add `Content-Type: application/json` only for JSON requests
- Improved file handling in PDF ingestion methods with proper try/finally blocks for file cleanup
- Enhanced `ingest_pdfs()` documentation with detailed docstring

### Added
- Comprehensive PDF ingestion examples in README.md
- Progress monitoring example for PDF ingestion
- Complete working example showcasing PDF upload workflow

## [1.0.0] - 2025-01-14

### Added
- Initial release with complete API coverage
- Support for all 33 API endpoints
- Health check endpoint
- Collection management (create, list, delete)
- Patient management (register, validate, get, delete, list, data summary)
- Data ingestion (PDFs, URLs, default)
- Ingestion status monitoring
- Chat functionality with streaming support
- Comprehensive logging endpoints
- File operations (database and S3)
- Type hints for better IDE support
- Async support for streaming operations
- Context manager support
- Proper error handling with custom exceptions
- Comprehensive documentation and examples

### Known Issues in 1.0.0
- ❌ PDF ingestion (`ingest_pdfs()`) did not work due to header conflict (FIXED in 1.0.1)
- ❌ Default ingestion (`ingest_default()`) with files did not work (FIXED in 1.0.1)
