# Real Time Governance System (RTGS)

## Overview
A CLI-first agentic system that transforms raw public data into standardized, cleaned, trustworthy evidence and communicates insights clearly from the command line. Built specifically for policymakers using datasets from the Telangana Open Data Portal.

## Purpose
Create a data-agnostic system that can:
- Clean and standardize any dataset
- Transform raw data into actionable insights
- Generate comprehensive analysis reports
- Support downstream tasks like recommendation engines and policy evaluation

## Current State
✅ **Fully Functional** - Complete prototype ready for use

The system successfully processes agriculture datasets and generates:
- Data cleaning and standardization
- Statistical insights and quality metrics  
- Correlation analysis and distribution patterns
- Domain-specific agriculture insights
- Visual analysis charts and plots

## Recent Changes
**2025-09-06**: Initial complete implementation
- Created modular CLI application with 4 main commands
- Implemented comprehensive data processor with intelligent cleaning
- Built insight generator with agriculture-specific analysis
- Added Telangana Open Data Portal connector
- Generated sample test data and verified full pipeline functionality

## User Preferences
- Focus on agriculture datasets from Telangana
- CLI-first interface for terminal-based workflow
- Data-agnostic approach - should work with any dataset
- Comprehensive cleaning and insight generation
- Visual output when requested

## Project Architecture

### Core Components
1. **main.py** - CLI interface with Click framework
   - `clean` - Data cleaning and standardization
   - `analyze` - Insight generation from cleaned data  
   - `fetch` - Data retrieval from Telangana portal
   - `pipeline` - Complete end-to-end workflow

2. **src/data_processor.py** - Data cleaning engine
   - Handles multiple formats (CSV, JSON, Excel)
   - Intelligent column name standardization
   - Missing value handling with data type awareness
   - Outlier detection and capping using IQR method
   - Duplicate removal and data validation

3. **src/insight_generator.py** - Analysis and insight generation
   - Basic statistical analysis
   - Data quality assessment
   - Correlation pattern detection
   - Distribution analysis with skewness detection
   - Agriculture-specific domain insights
   - Visual chart generation (correlation matrix, distributions, categories)

4. **src/telangana_connector.py** - Data source integration
   - Telangana Open Data Portal API integration
   - Sample data generation for testing
   - Flexible dataset fetching by category or ID

### Key Features
- **Data Agnostic**: Works with any dataset structure
- **Comprehensive Cleaning**: Handles missing values, outliers, duplicates
- **Smart Type Detection**: Automatically converts data types
- **Domain Intelligence**: Special agriculture-focused insights
- **Visual Analysis**: Generates charts and correlation matrices
- **Robust Error Handling**: Graceful failure with helpful messages

### Dependencies
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **requests**: HTTP requests for data fetching
- **click**: CLI framework
- **matplotlib/seaborn**: Data visualization
- **scikit-learn**: Statistical analysis and clustering
- **openpyxl**: Excel file support

### Testing Results
Successfully processed sample Telangana agriculture dataset:
- 1,010 records across 10 districts and 10 crops
- Generated 18 comprehensive insights
- Created 6 visualization charts
- Zero data quality issues detected
- Complete pipeline execution in under 30 seconds

## Next Steps
The system is ready for:
1. Integration with live Telangana Open Data Portal
2. Extension to other data domains beyond agriculture  
3. Addition of recommendation engine capabilities
4. Policy evaluation framework integration
5. Semantic Q&A functionality for natural language queries
