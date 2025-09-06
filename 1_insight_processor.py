"""
Insight Generator Module
Generates meaningful insights from cleaned data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from typing import List, Dict, Any, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

class InsightGenerator:
    """
    Generates key insights from any dataset
    """
    
    def __init__(self):
        self.insights = []
        
    def generate_insights(self, data_path: str, visual: bool = False) -> List[str]:
        """Generate comprehensive insights from the dataset"""
        try:
            # Load the cleaned data
            df = self._load_data(data_path)
            if df is None:
                return ["❌ Could not load data for analysis"]
            
            print(f"🔍 Generating insights for dataset with {len(df)} rows and {len(df.columns)} columns")
            
            insights = []
            
            # Basic statistics
            insights.extend(self._basic_statistics(df))
            
            # Data quality insights
            insights.extend(self._data_quality_insights(df))
            
            # Column-specific insights
            insights.extend(self._column_insights(df))
            
            # Correlation insights
            insights.extend(self._correlation_insights(df))
            
            # Distribution insights
            insights.extend(self._distribution_insights(df))
            
            # Pattern recognition
            insights.extend(self._pattern_insights(df))
            
            # Agriculture-specific insights (if applicable)
            insights.extend(self._domain_specific_insights(df))
            
            # Generate visualizations if requested
            if visual:
                self._generate_visualizations(df)
                insights.append("📊 Visual insights generated and saved as plots")
            
            print(f"✅ Generated {len(insights)} insights")
            return insights
            
        except Exception as e:
            return [f"❌ Error generating insights: {str(e)}"]
    
    def _load_data(self, data_path: str) -> Optional[pd.DataFrame]:
        """Load data from file"""
        try:
            path = Path(data_path)
            if path.suffix.lower() == '.csv':
                return pd.read_csv(data_path)
            elif path.suffix.lower() == '.json':
                return pd.read_json(data_path)
            elif path.suffix.lower() in ['.xlsx', '.xls']:
                return pd.read_excel(data_path)
            else:
                return None
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def _basic_statistics(self, df: pd.DataFrame) -> List[str]:
        """Generate basic statistical insights"""
        insights = []
        
        # Dataset overview
        insights.append(f"📊 Dataset contains {len(df):,} records across {len(df.columns)} attributes")
        
        # Numeric columns analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            insights.append(f"🔢 Found {len(numeric_cols)} numeric attributes for quantitative analysis")
            
            # Summary statistics
            for col in numeric_cols[:3]:  # Top 3 numeric columns
                mean_val = df[col].mean()
                std_val = df[col].std()
                insights.append(f"   • {col}: Mean = {mean_val:.2f}, Std = {std_val:.2f}")
        
        # Categorical columns analysis
        text_cols = df.select_dtypes(include=['object', 'string']).columns
        if len(text_cols) > 0:
            insights.append(f"📝 Found {len(text_cols)} categorical attributes")
            
            for col in text_cols[:3]:  # Top 3 categorical columns
                unique_count = df[col].nunique()
                insights.append(f"   • {col}: {unique_count} unique values")
        
        return insights
    
    def _data_quality_insights(self, df: pd.DataFrame) -> List[str]:
        """Analyze data quality"""
        insights = []
        
        # Missing data analysis
        missing_data = df.isnull().sum()
        total_missing = missing_data.sum()
        
        if total_missing > 0:
            missing_percent = (total_missing / (len(df) * len(df.columns))) * 100
            insights.append(f"⚠️  Data completeness: {100 - missing_percent:.1f}% ({total_missing:,} missing values)")
            
            # Highlight columns with significant missing data
            high_missing = missing_data[missing_data > len(df) * 0.1]  # >10% missing
            if len(high_missing) > 0:
                insights.append(f"🔍 Attributes with >10% missing data: {', '.join(high_missing.index)}")
        else:
            insights.append("✅ Excellent data quality: No missing values detected")
        
        # Duplicate analysis
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            insights.append(f"🔄 Found {duplicates:,} duplicate records ({duplicates/len(df)*100:.1f}%)")
        else:
            insights.append("✅ No duplicate records found")
        
        return insights
    
    def _column_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate insights for individual columns"""
        insights = []
        
        # Analyze each column
        for col in df.columns[:5]:  # Limit to first 5 columns for brevity
            if df[col].dtype in ['object', 'string']:
                # Categorical analysis
                unique_count = df[col].nunique()
                most_common = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else "N/A"
                insights.append(f"📋 {col}: {unique_count} categories, most common = '{most_common}'")
                
            elif df[col].dtype in [np.number]:
                # Numeric analysis
                min_val = df[col].min()
                max_val = df[col].max()
                median_val = df[col].median()
                insights.append(f"📈 {col}: Range [{min_val:.2f} - {max_val:.2f}], Median = {median_val:.2f}")
        
        return insights
    
    def _correlation_insights(self, df: pd.DataFrame) -> List[str]:
        """Find correlation patterns"""
        insights = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            
            # Find strong correlations (>0.7 or <-0.7)
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        strong_corr.append((col1, col2, corr_val))
            
            if strong_corr:
                insights.append(f"🔗 Found {len(strong_corr)} strong correlations:")
                for col1, col2, corr_val in strong_corr[:3]:  # Top 3
                    insights.append(f"   • {col1} ↔ {col2}: {corr_val:.3f}")
            else:
                insights.append("📊 No strong correlations found between numeric attributes")
        
        return insights
    
    def _distribution_insights(self, df: pd.DataFrame) -> List[str]:
        """Analyze data distributions"""
        insights = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols[:3]:  # Analyze top 3 numeric columns
            # Check for normal distribution
            skewness = df[col].skew()
            if abs(skewness) > 1:
                direction = "right" if skewness > 0 else "left"
                insights.append(f"📊 {col} shows {direction}-skewed distribution (skewness: {skewness:.2f})")
            
            # Check for outliers
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)).sum()
            
            if outliers > 0:
                insights.append(f"🎯 {col}: {outliers} potential outliers detected")
        
        return insights
    
    def _pattern_insights(self, df: pd.DataFrame) -> List[str]:
        """Identify patterns in the data"""
        insights = []
        
        # Time-based patterns
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        if len(datetime_cols) > 0:
            for col in datetime_cols:
                date_range = (df[col].max() - df[col].min())
                insights.append(f"📅 Time span in {col}: {date_range.days if hasattr(date_range, 'days') else 'N/A'} days")
        
        # Categorical patterns
        text_cols = df.select_dtypes(include=['object', 'string']).columns
        for col in text_cols[:2]:  # Top 2 categorical columns
            value_counts = df[col].value_counts()
            if len(value_counts) > 1:
                dominant_percent = (value_counts.iloc[0] / len(df)) * 100
                if dominant_percent > 50:
                    insights.append(f"🎯 {col}: '{value_counts.index[0]}' dominates ({dominant_percent:.1f}%)")
        
        return insights
    
    def _domain_specific_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate domain-specific insights (agriculture focus)"""
        insights = []
        
        # Look for agriculture-related columns
        agri_keywords = ['crop', 'yield', 'production', 'area', 'season', 'district', 'farmer', 'agriculture']
        agri_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in agri_keywords)]
        
        if agri_cols:
            insights.append(f"🌾 Agriculture-related attributes identified: {', '.join(agri_cols[:3])}")
            
            # Specific agriculture insights
            for col in agri_cols:
                if 'yield' in col.lower() and df[col].dtype in [np.number]:
                    avg_yield = df[col].mean()
                    insights.append(f"🌾 Average {col}: {avg_yield:.2f}")
                
                elif 'area' in col.lower() and df[col].dtype in [np.number]:
                    total_area = df[col].sum()
                    insights.append(f"🌾 Total {col}: {total_area:,.0f}")
                
                elif 'district' in col.lower():
                    district_count = df[col].nunique()
                    insights.append(f"🌾 Data covers {district_count} districts")
        
        return insights
    
    def _generate_visualizations(self, df: pd.DataFrame):
        """Generate visualization plots"""
        try:
            plt.style.use('default')
            fig_count = 1
            
            # 1. Correlation heatmap for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                plt.figure(figsize=(10, 8))
                corr_matrix = df[numeric_cols].corr()
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
                plt.title('Correlation Matrix')
                plt.tight_layout()
                plt.savefig(f'correlation_matrix_{fig_count}.png', dpi=300, bbox_inches='tight')
                plt.close()
                fig_count += 1
            
            # 2. Distribution plots for top numeric columns
            for i, col in enumerate(numeric_cols[:3]):
                plt.figure(figsize=(10, 6))
                plt.subplot(1, 2, 1)
                df[col].hist(bins=30, alpha=0.7)
                plt.title(f'Distribution of {col}')
                plt.xlabel(col)
                plt.ylabel('Frequency')
                
                plt.subplot(1, 2, 2)
                df[col].plot(kind='box')
                plt.title(f'Box Plot of {col}')
                plt.ylabel(col)
                
                plt.tight_layout()
                plt.savefig(f'distribution_{col}_{fig_count}.png', dpi=300, bbox_inches='tight')
                plt.close()
                fig_count += 1
            
            # 3. Categorical analysis for top text columns
            text_cols = df.select_dtypes(include=['object', 'string']).columns
            for col in text_cols[:2]:
                if df[col].nunique() <= 20:  # Only if reasonable number of categories
                    plt.figure(figsize=(12, 6))
                    value_counts = df[col].value_counts().head(10)
                    value_counts.plot(kind='bar')
                    plt.title(f'Top Categories in {col}')
                    plt.xlabel(col)
                    plt.ylabel('Count')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    plt.savefig(f'categories_{col}_{fig_count}.png', dpi=300, bbox_inches='tight')
                    plt.close()
                    fig_count += 1
                    
        except Exception as e:
            print(f"Error generating visualizations: {e}")
    
    def save_insights(self, insights: List[str], output_path: str):
        """Save insights to a file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("RTGS Data Insights Report\n")
                f.write("=" * 50 + "\n\n")
                
                for i, insight in enumerate(insights, 1):
                    f.write(f"{i}. {insight}\n")
                
                f.write(f"\n\nReport generated on: {pd.Timestamp.now()}\n")
            
            print(f"💾 Insights saved to: {output_path}")
            
        except Exception as e:
            print(f"Error saving insights: {e}")
