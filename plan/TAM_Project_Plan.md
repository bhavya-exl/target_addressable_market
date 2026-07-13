# Total Addressable Market (TAM) Tool - Project Plan

## 1. Project Overview
Build an AI-powered addressable market analysis tool that:
- Aggregates company data from SharePoint (Excel files) + external sources
- Uses AWS Bedrock (LLMs) for intelligent analysis
- Identifies market opportunities for consulting company
- Determines optimal timing for market entry

## 2. AWS Services to Use
- **AWS Bedrock**: For LLM/AI capabilities (already have API key)
- **Amazon S3**: Data lake for storing Excel files and processed data
- **Amazon DynamoDB**: For storing company profiles, opportunities
- **AWS Lambda**: For processing data and triggering analysis
- **Amazon API Gateway**: For exposing APIs
- **Amazon QuickSight**: For visualization/dashboards

## 3. Initial Project Structure
```
TAM-Tool/
├── config/
│   └── config.py          # Configuration management
├── src/
│   ├── data_ingestion/    # SharePoint & data sources
│   ├── data_processing/   # Excel parsing, data cleaning
│   ├── analysis/          # Market analysis engines
│   ├── llm_integration/   # Bedrock/LLM wrappers
│   └── api/               # API endpoints
├── tests/
├── requirements.txt
└── README.md
```

## 4. Next Steps (Phase 1 - Basic Structure)
- [ ] Set up Python project with virtual environment
- [ ] Create configuration management (read .config)
- [ ] Set up AWS SDK/boto3 integration
- [ ] Create basic data models
- [ ] Set up logging
- [ ] Create basic folder structure

## 5. Follow-up: Architecture Planning
After Phase 1, we will plan:
- Data flow architecture
- SharePoint integration approach
- LLM prompt engineering strategy
- Database schema design
- API design
