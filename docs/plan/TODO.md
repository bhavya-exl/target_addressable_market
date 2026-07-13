# TAM Tool - SharePoint Integration & Data Pipeline

## Current Project Structure
```
TAM/
├── .config                  # Configuration (API keys, etc.)
├── README.md
├── requirements.txt
├── TAM_Project_Plan.md
├── config/
│   ├── __init__.py
│   └── config.py            # Configuration management
└── src/
    ├── __init__.py
    ├── main.py               # Entry point
    ├── logging_config.py     # Logging setup
    ├── aws/
    │   ├── __init__.py
    │   └── bedrock_client.py  # Bedrock LLM client
    └── models/
        └── __init__.py       # Empty - for data models
```

## Plan: SharePoint Integration & Data Pipeline

### Step 1: Create S3 Client Module
- [ ] Create `src/aws/s3_client.py`
  - Upload raw Excel files to S3
  - Download files from S3
  - List files in S3 bucket

### Step 2: Create SharePoint Client Module  
- [ ] Create `src/sharepoint/__init__.py`
- [ ] Create `src/sharepoint/client.py`
  - Authenticate with SharePoint using MSAL
  - Connect to SharePoint site and drive
  - List Excel files in the specified library
  - Download Excel files

### Step 3: Create Data Processing Module
- [ ] Create `src/data_processing/__init__.py`
- [ ] Create `src/data_processing/excel_processor.py`
  - Read Excel files using pandas
  - Extract structured data (companies, metrics, etc.)
  - Validate data structure

### Step 4: Create Data Models
- [ ] Update `src/models/__init__.py` with Pydantic models
  - CompanyModel
  - MarketDataModel
  - RawFileMetadata

### Step 5: Create Data Ingestion Pipeline
- [ ] Create `src/pipelines/__init__.py`
- [ ] Create `src/pipelines/ingestion.py`
  - Orchestrate: SharePoint → S3 → Excel Processor
  - Handle errors and logging

### Step 6: Update Main Entry Point
- [ ] Update `src/main.py` to include ingestion functionality

## Dependencies (already in requirements.txt)
- boto3 (S3)
- office365-rest-python-client (SharePoint)
- pandas (Excel processing)
- openpyxl (Excel reading)

## Files to Create
1. `src/aws/s3_client.py` - S3 operations
2. `src/sharepoint/__init__.py` 
3. `src/sharepoint/client.py` - SharePoint client
4. `src/data_processing/__init__.py`
5. `src/data_processing/excel_processor.py` - Excel parsing
6. `src/models/__init__.py` - Data models
7. `src/pipelines/__init__.py`
8. `src/pipelines/ingestion.py` - Main pipeline

## Configuration Additions
- Update `.config` with SharePoint credentials (tenant ID, client ID, client secret)
