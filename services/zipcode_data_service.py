"""
ZipCode Data Service for Azure Functions
Loads and manages zipcode data with population density calculations
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from geopy.distance import geodesic
import os

logger = logging.getLogger(__name__)

class ZipcodeDataService:
    """Manages zipcode data loading and geographic calculations"""
    
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.data_loaded = False
        
    async def initialize(self) -> None:
        """Initialize the data service by loading zipcode data"""
        if self.data_loaded:
            return
            
        try:
            self._load_zipcode_data()
            self.data_loaded = True
            logger.info(f"Zipcode data service initialized with {len(self.data)} zipcodes")
        except Exception as e:
            logger.error(f"Failed to initialize zipcode data service: {e}")
            raise
    
    def _load_zipcode_data(self) -> None:
        """Load zipcode data from CSV file"""
        data_path = Path(__file__).parent.parent / "data" / "zipcode_data.csv"
        
        if not data_path.exists():
            raise FileNotFoundError(f"Zipcode data file not found: {data_path}")
        
        logger.info(f"Loading zipcode data from {data_path}")
        
        # Load CSV with proper column handling
        self.data = pd.read_csv(data_path)
        
        # Ensure zipcode is string type for consistent handling
        self.data['zipcode'] = self.data['zipcode'].astype(str).str.zfill(5)
        
        # Handle duplicate longitude column if present
        if 'longitude.1' in self.data.columns:
            self.data = self.data.drop('longitude.1', axis=1)
        
        # Ensure required columns exist
        required_cols = ['zipcode', 'latitude', 'longitude', 'population_density', 'city', 'county_name']
        missing_cols = [col for col in required_cols if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in zipcode data: {missing_cols}")
        
        # Clean and validate data
        self.data = self.data.dropna(subset=['latitude', 'longitude', 'population_density'])
        self.data = self.data[self.data['population_density'] > 0]
        
        logger.info(f"Loaded and cleaned {len(self.data)} zipcode records")
    
    def get_zipcode_info(self, zipcode: str) -> Optional[Dict]:
        """Get information for a specific zipcode"""
        if not self.data_loaded:
            raise RuntimeError("Data service not initialized. Call initialize() first.")
        
        zipcode = str(zipcode).zfill(5)
        matches = self.data[self.data['zipcode'] == zipcode]
        
        if matches.empty:
            return None
        
        row = matches.iloc[0]
        return {
            'zipcode': row['zipcode'],
            'city': row.get('city', ''),
            'county_name': row.get('county_name', ''),
            'latitude': float(row['latitude']),
            'longitude': float(row['longitude']),
            'population_density': float(row['population_density']),
            'population': int(row.get('population', 0)) if pd.notna(row.get('population', 0)) else 0,
            'area_sq_miles': float(row.get('area_sq_miles', 0)) if pd.notna(row.get('area_sq_miles', 0)) else 0
        }
    
    def get_nearby_zipcodes(self, zipcode: str, radius_miles: float = 50.0) -> List[Dict]:
        """Find nearby zipcodes within the specified radius"""
        if not self.data_loaded:
            raise RuntimeError("Data service not initialized. Call initialize() first.")
        
        zipcode_info = self.get_zipcode_info(zipcode)
        if not zipcode_info:
            return []
        
        center_lat = zipcode_info['latitude']
        center_lon = zipcode_info['longitude']
        nearby_zipcodes = []
        
        for _, row in self.data.iterrows():
            if row['zipcode'] == zipcode:
                continue
            
            distance = geodesic(
                (center_lat, center_lon),
                (row['latitude'], row['longitude'])
            ).miles
            
            if distance <= radius_miles:
                nearby_zipcodes.append({
                    'zipcode': row['zipcode'],
                    'city': row.get('city', ''),
                    'county_name': row.get('county_name', ''),
                    'distance_miles': round(distance, 2),
                    'population_density': float(row['population_density']),
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude'])
                })
        
        # Sort by distance
        return sorted(nearby_zipcodes, key=lambda x: x['distance_miles'])
    
    def calculate_national_percentile(self, population_density: float) -> float:
        """Calculate the national percentile for a given population density"""
        if not self.data_loaded:
            raise RuntimeError("Data service not initialized. Call initialize() first.")
        
        if len(self.data) == 0:
            return 0.0
        
        # Calculate percentile rank
        percentile = (self.data['population_density'] < population_density).mean() * 100
        return round(percentile, 1)
    
    def get_density_stats(self) -> Dict:
        """Get overall density statistics for the dataset"""
        if not self.data_loaded:
            raise RuntimeError("Data service not initialized. Call initialize() first.")
        
        density_values = self.data['population_density']
        return {
            'total_zipcodes': len(self.data),
            'min_density': float(density_values.min()),
            'max_density': float(density_values.max()),
            'mean_density': float(density_values.mean()),
            'median_density': float(density_values.median()),
            'std_density': float(density_values.std())
        }

# Global instance
zipcode_service = ZipcodeDataService()