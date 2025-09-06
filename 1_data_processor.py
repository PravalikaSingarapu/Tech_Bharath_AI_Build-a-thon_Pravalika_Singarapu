"""
Data Processor Module
Handles data cleaning, transformation, and standardization for any dataset
"""

import pandas as pd
import numpy as np
import requests
from pathlib import Path
import json
import logging
from typing import Optional, Dict, Any, List
import re

class DataProcessor:
    """
    Data-agnostic processor that can clean and transform any dataset
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['csv', 'json', 'excel', 'xlsx', 'xls']
        
    def process_file(self, input_path: str, output_path: Optional[str] = None, 
                    output_format: str = 'csv') -> Optional[str]:
        """Process a local file"""
        try:
            # Load data based on file extension
            df = self._load_data(input_path)
            if df is None:
                return None
                
            # Clean and transform
            cleaned_df = self._clean_data(df)
            
            # Save processed data
            if output_path:
                return self._save_data(cleaned_df, output_path, output_format)
            else:
                # Generate default output name
                input_file = Path(input_path)
                output_file = input_file.parent / f"cleaned_{input_file.stem}.{output_format}"
                return self._save_data(cleaned_df, str(output_file), output_format)
                
        except Exception as e:
            self.logger.error(f"Error processing file {input_path}: {e}")
            return None
    
    def process_url(self, url: str, output_path: Optional[str] = None, 
                   output_format: str = 'csv') -> Optional[str]:
        """Process data from a URL"""
        try:
            # Download data
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Determine format from URL or content type
            if url.endswith('.json') or 'application/json' in response.headers.get('content-type', ''):
                df = pd.read_json(response.text)
            elif url.endswith(('.csv', '.txt')):
                df = pd.read_csv(response.text)
            elif url.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(response.content)
            else:
                # Try to infer format
                try:
                    df = pd.read_json(response.text)
                except:
                    try:
                        df = pd.read_csv(response.text)
                    except:
                        self.logger.error(f"Could not determine format for URL: {url}")
                        return None
            
            # Clean and transform
            cleaned_df = self._clean_data(df)
            
            # Save processed data
            if output_path:
                return self._save_data(cleaned_df, output_path, output_format)
            else:
                output_file = f"cleaned_data_from_url.{output_format}"
                return self._save_data(cleaned_df, output_file, output_format)
                
        except Exception as e:
            self.logger.error(f"Error processing URL {url}: {e}")
            return None
    
    def _load_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load data from various file formats"""
        file_path_obj = Path(file_path)
        
        try:
            if file_path_obj.suffix.lower() == '.csv':
                return pd.read_csv(file_path, encoding='utf-8', low_memory=False)
            elif file_path_obj.suffix.lower() == '.json':
                return pd.read_json(file_path)
            elif file_path_obj.suffix.lower() in ['.xlsx', '.xls']:
                return pd.read_excel(file_path)
            else:
                self.logger.error(f"Unsupported file format: {file_path_obj.suffix}")
                return None
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            return None
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Comprehensive data cleaning that works for any dataset
        """
        print(f"🔧 Starting data cleaning for dataset with {len(df)} rows and {len(df.columns)} columns")
        
        # Make a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # 1. Basic info about the dataset
        original_rows = len(cleaned_df)
        original_cols = len(cleaned_df.columns)
        
        # 2. Clean column names
        cleaned_df.columns = self._standardize_column_names(list(cleaned_df.columns))
        
        # 3. Handle missing values
        cleaned_df = self._handle_missing_values(cleaned_df)
        
        # 4. Remove duplicate rows
        duplicates_before = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates()
        duplicates_removed = duplicates_before - len(cleaned_df)
        
        # 5. Clean text data
        cleaned_df = self._clean_text_columns(cleaned_df)
        
        # 6. Standardize data types
        cleaned_df = self._standardize_data_types(cleaned_df)
        
        # 7. Remove outliers (for numerical columns)
        cleaned_df = self._handle_outliers(cleaned_df)
        
        # 8. Final validation
        cleaned_df = self._final_validation(cleaned_df)
        
        final_rows = len(cleaned_df)
        final_cols = len(cleaned_df.columns)
        
        print(f"✅ Data cleaning completed:")
        print(f"   📊 Rows: {original_rows} → {final_rows} ({original_rows - final_rows} removed)")
        print(f"   📋 Columns: {original_cols} → {final_cols}")
        print(f"   🔍 Duplicates removed: {duplicates_removed}")
        
        return cleaned_df
    
    def _standardize_column_names(self, columns: List[str]) -> List[str]:
        """Standardize column names"""
        standardized = []
        for col in columns:
            # Convert to string and strip whitespace
            col = str(col).strip()
            # Replace spaces and special chars with underscores
            col = re.sub(r'[^\w\s]', '', col)
            col = re.sub(r'\s+', '_', col)
            # Convert to lowercase
            col = col.lower()
            # Remove leading/trailing underscores
            col = col.strip('_')
            # Handle empty column names
            if not col:
                col = f"column_{len(standardized)}"
            standardized.append(col)
        return standardized
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently"""
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_percent = (missing_count / len(df)) * 100
            
            if missing_percent > 50:
                # If more than 50% missing, consider dropping the column
                print(f"⚠️  Column '{column}' has {missing_percent:.1f}% missing values")
                continue
            
            # Handle based on data type
            if df[column].dtype in ['object', 'string']:
                # For text columns, fill with 'Unknown' or most frequent
                df[column] = df[column].fillna('Unknown')
            elif df[column].dtype in ['int64', 'float64', 'int32', 'float32']:
                # For numeric columns, use median
                median_val = df[column].median()
                df[column] = df[column].fillna(median_val)
            elif 'datetime' in str(df[column].dtype):
                # For datetime columns, forward fill
                df[column] = df[column].fillna(method='ffill')
        
        return df
    
    def _clean_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean text data in string columns"""
        for column in df.select_dtypes(include=['object', 'string']).columns:
            # Strip whitespace
            df[column] = df[column].astype(str).str.strip()
            # Remove extra whitespace
            df[column] = df[column].str.replace(r'\s+', ' ', regex=True)
            # Handle common inconsistencies
            df[column] = df[column].replace(['', 'null', 'NULL', 'None', 'NONE'], 'Unknown')
        
        return df
    
    def _standardize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize data types for better analysis"""
        for column in df.columns:
            # Try to convert numeric strings to numbers
            if df[column].dtype == 'object':
                # Check if it's numeric
                try:
                    # Remove common non-numeric characters
                    cleaned_series = df[column].astype(str).str.replace(r'[,\s$%]', '', regex=True)
                    numeric_series = pd.to_numeric(cleaned_series, errors='coerce')
                    
                    # If most values are numeric, convert the column
                    if (~numeric_series.isna()).sum() / len(df) > 0.8:
                        df[column] = numeric_series
                        print(f"🔄 Converted '{column}' to numeric")
                except:
                    pass
                
                # Try to convert to datetime
                try:
                    if 'date' in column.lower() or 'time' in column.lower():
                        df[column] = pd.to_datetime(df[column], errors='coerce')
                        print(f"📅 Converted '{column}' to datetime")
                except:
                    pass
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers in numeric columns using IQR method"""
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            
            # Define outlier bounds
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_count = ((df[column] < lower_bound) | (df[column] > upper_bound)).sum()
            
            if outliers_count > 0:
                print(f"🎯 Found {outliers_count} outliers in '{column}'")
                # Cap outliers instead of removing them
                df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
        
        return df
    
    def _final_validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final validation and cleanup"""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Remove completely empty columns
        df = df.dropna(axis=1, how='all')
        
        return df
    
    def _save_data(self, df: pd.DataFrame, output_path: str, format: str) -> str:
        """Save processed data in specified format"""
        try:
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'csv':
                df.to_csv(output_path_obj, index=False)
            elif format.lower() == 'json':
                df.to_json(output_path_obj, orient='records', indent=2)
            elif format.lower() in ['excel', 'xlsx']:
                df.to_excel(output_path_obj, index=False)
            else:
                raise ValueError(f"Unsupported output format: {format}")
            
            return str(output_path)
        except Exception as e:
            self.logger.error(f"Error saving data to {output_path}: {e}")
            return None
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a summary of the dataset"""
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
            'text_columns': list(df.select_dtypes(include=['object', 'string']).columns),
            'datetime_columns': list(df.select_dtypes(include=['datetime64']).columns)
        }
        return summary
