"""
Telangana Open Data Portal Connector
Handles data fetching from Telangana government data portal
"""

import requests
import pandas as pd
from pathlib import Path
import json
from typing import Optional, Dict, Any, List
import time

class TelanganaConnector:
    """
    Connector for Telangana Open Data Portal
    """
    
    def __init__(self):
        self.base_url = "https://data.telangana.gov.in"
        self.api_endpoints = {
            'datasets': '/api/3/action/package_list',
            'dataset_info': '/api/3/action/package_show',
            'resource_data': '/api/3/action/datastore_search'
        }
        
    def fetch_dataset(self, dataset_id: str, output_dir: Optional[str] = None) -> Optional[str]:
        """Fetch a specific dataset by ID"""
        try:
            print(f"🌐 Fetching dataset: {dataset_id}")
            
            # Get dataset information
            dataset_info = self._get_dataset_info(dataset_id)
            if not dataset_info:
                print(f"❌ Dataset '{dataset_id}' not found")
                return None
            
            # Find CSV or data resources
            resources = dataset_info.get('resources', [])
            data_resources = [r for r in resources if r.get('format', '').lower() in ['csv', 'json', 'xlsx']]
            
            if not data_resources:
                print(f"❌ No downloadable data resources found for '{dataset_id}'")
                return None
            
            # Download the first available resource
            resource = data_resources[0]
            resource_url = resource.get('url')
            
            if resource_url:
                return self._download_resource(resource_url, dataset_id, output_dir)
            else:
                print(f"❌ No valid URL found for dataset '{dataset_id}'")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching dataset '{dataset_id}': {e}")
            return None
    
    def fetch_category_data(self, category: str = 'agriculture', output_dir: Optional[str] = None) -> Optional[str]:
        """Fetch datasets from a specific category"""
        try:
            print(f"🌐 Searching for {category} datasets...")
            
            # Get list of all datasets
            datasets = self._get_dataset_list()
            if not datasets:
                print("❌ Could not retrieve dataset list")
                return None
            
            # Filter datasets by category/tags
            relevant_datasets = []
            for dataset_id in datasets[:50]:  # Limit to first 50 for performance
                info = self._get_dataset_info(dataset_id)
                if info:
                    tags = [tag.get('name', '').lower() for tag in info.get('tags', [])]
                    title = info.get('title', '').lower()
                    
                    if (category.lower() in ' '.join(tags) or 
                        category.lower() in title or
                        any(keyword in title for keyword in ['crop', 'farm', 'agriculture', 'yield'])):
                        relevant_datasets.append(dataset_id)
                
                # Add small delay to be respectful to the API
                time.sleep(0.1)
            
            if not relevant_datasets:
                print(f"❌ No {category} datasets found")
                return None
            
            print(f"✅ Found {len(relevant_datasets)} {category} datasets")
            
            # Try to fetch the first available dataset
            for dataset_id in relevant_datasets[:3]:  # Try first 3
                result = self.fetch_dataset(dataset_id, output_dir)
                if result:
                    return result
            
            print(f"❌ Could not download any {category} datasets")
            return None
            
        except Exception as e:
            print(f"❌ Error fetching {category} data: {e}")
            return None
    
    def _get_dataset_list(self) -> Optional[List[str]]:
        """Get list of all available datasets"""
        try:
            url = f"{self.base_url}{self.api_endpoints['datasets']}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('result', [])
            
            # Fallback: try common agriculture dataset IDs
            return [
                'agriculture-crop-production-statistics',
                'crop-yield-data',
                'agriculture-statistics',
                'farmer-registration-data',
                'irrigation-data',
                'district-wise-agriculture-data'
            ]
            
        except Exception as e:
            print(f"Warning: Could not fetch dataset list: {e}")
            # Return fallback list
            return [
                'agriculture-crop-production-statistics',
                'crop-yield-data',
                'agriculture-statistics'
            ]
    
    def _get_dataset_info(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a dataset"""
        try:
            url = f"{self.base_url}{self.api_endpoints['dataset_info']}"
            params = {'id': dataset_id}
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('result', {})
            
            return None
            
        except Exception as e:
            print(f"Warning: Could not fetch info for dataset '{dataset_id}': {e}")
            return None
    
    def _download_resource(self, url: str, dataset_id: str, output_dir: Optional[str] = None) -> Optional[str]:
        """Download a data resource"""
        try:
            print(f"⬇️  Downloading data from: {url}")
            
            # Set up output path
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
            else:
                output_path = Path('.')
            
            # Determine file extension from URL
            if url.endswith('.csv'):
                filename = f"{dataset_id}.csv"
            elif url.endswith('.json'):
                filename = f"{dataset_id}.json"
            elif url.endswith(('.xlsx', '.xls')):
                filename = f"{dataset_id}.xlsx"
            else:
                filename = f"{dataset_id}.csv"  # Default to CSV
            
            output_file = output_path / filename
            
            # Download the file
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Save to file
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Data saved to: {output_file}")
            return str(output_file)
            
        except Exception as e:
            print(f"❌ Error downloading resource: {e}")
            return None
    
    def create_sample_agriculture_data(self, output_dir: Optional[str] = None) -> str:
        """Create sample agriculture data for testing purposes"""
        try:
            # Create sample data that mimics Telangana agriculture datasets
            import random
            
            districts = ['Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar', 'Khammam', 
                        'Adilabad', 'Medak', 'Rangareddy', 'Mahbubnagar', 'Nalgonda']
            
            crops = ['Rice', 'Cotton', 'Maize', 'Sugarcane', 'Groundnut', 'Soybean', 
                    'Sunflower', 'Chili', 'Turmeric', 'Wheat']
            
            seasons = ['Kharif', 'Rabi', 'Summer']
            years = [2019, 2020, 2021, 2022, 2023]
            
            # Generate sample data
            data = []
            for year in years:
                for district in districts:
                    for crop in crops:
                        for season in seasons:
                            if random.random() > 0.3:  # 70% chance of having data
                                data.append({
                                    'year': year,
                                    'district': district,
                                    'crop': crop,
                                    'season': season,
                                    'area_hectares': random.randint(1000, 50000),
                                    'production_tonnes': random.randint(500, 100000),
                                    'yield_kg_per_hectare': random.randint(800, 5000),
                                    'rainfall_mm': random.randint(400, 1200),
                                    'farmers_count': random.randint(100, 5000),
                                    'irrigation_percentage': random.randint(20, 90)
                                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Set up output path
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
            else:
                output_path = Path('.')
            
            output_file = output_path / 'telangana_agriculture_sample.csv'
            df.to_csv(output_file, index=False)
            
            print(f"✅ Sample agriculture data created: {output_file}")
            print(f"📊 Generated {len(df)} records covering {len(districts)} districts and {len(crops)} crops")
            
            return str(output_file)
            
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            return None
