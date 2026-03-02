"""
Population Density Assessment Service for Azure Functions
Provides density analysis and scoring functionality
"""

import logging
from typing import Dict, List, Optional
from services.zipcode_data_service import zipcode_service

logger = logging.getLogger(__name__)

class DensityAssessmentService:
    """Handles population density assessment and scoring"""
    
    def __init__(self):
        self.max_density_score = 100.0
        
    def calculate_density_score(self, population_density: float) -> float:
        """
        Calculate a normalized density score (0-100) based on population density
        Uses logarithmic scaling to handle the wide range of density values
        """
        if population_density <= 0:
            return 0.0
        
        # Get overall stats for normalization
        stats = zipcode_service.get_density_stats()
        max_density = stats['max_density']
        min_density = max(stats['min_density'], 0.1)  # Avoid log(0)
        
        # Use logarithmic scaling for better distribution
        import numpy as np
        log_density = np.log10(max(population_density, 0.1))
        log_max = np.log10(max_density)
        log_min = np.log10(min_density)
        
        # Normalize to 0-100 scale
        if log_max == log_min:
            return 50.0  # Fallback if all densities are the same
        
        score = ((log_density - log_min) / (log_max - log_min)) * self.max_density_score
        return round(max(0.0, min(100.0, score)), 1)
    
    async def assess_zipcode_density(self, zipcode: str, radius_miles: float = 50.0) -> Optional[Dict]:
        """
        Comprehensive zipcode density assessment
        """
        # Ensure data service is initialized
        await zipcode_service.initialize()
        
        # Get zipcode information
        zipcode_info = zipcode_service.get_zipcode_info(zipcode)
        if not zipcode_info:
            return None
        
        population_density = zipcode_info['population_density']
        
        # Calculate density score
        density_score = self.calculate_density_score(population_density)
        
        # Calculate national percentile
        national_percentile = zipcode_service.calculate_national_percentile(population_density)
        
        # Get nearby zipcodes for comparison
        nearby_zipcodes = zipcode_service.get_nearby_zipcodes(zipcode, radius_miles)
        
        # Calculate nearby comparison statistics
        nearby_stats = self._calculate_nearby_stats(population_density, nearby_zipcodes)
        
        # Prepare nearby comparison data
        nearby_comparison = []
        for nearby in nearby_zipcodes[:10]:  # Limit to top 10 nearest
            nearby_score = self.calculate_density_score(nearby['population_density'])
            nearby_comparison.append({
                'zipcode': nearby['zipcode'],
                'city': nearby['city'],
                'county_name': nearby['county_name'],
                'distance_miles': nearby['distance_miles'],
                'population_density': nearby['population_density'],
                'density_score': nearby_score,
                'latitude': nearby['latitude'],
                'longitude': nearby['longitude']
            })
        
        return {
            'zipcode': zipcode,
            'city': zipcode_info['city'],
            'county_name': zipcode_info['county_name'],
            'latitude': zipcode_info['latitude'],
            'longitude': zipcode_info['longitude'],
            'population': zipcode_info['population'],
            'area_sq_miles': zipcode_info['area_sq_miles'],
            'population_density': population_density,
            'density_score': density_score,
            'national_percentile': national_percentile,
            'nearby_stats': nearby_stats,
            'nearby_comparison': nearby_comparison,
            'search_radius_miles': radius_miles
        }
    
    def _calculate_nearby_stats(self, target_density: float, nearby_zipcodes: List[Dict]) -> Dict:
        """Calculate statistics comparing target density to nearby zipcodes"""
        if not nearby_zipcodes:
            return {
                'nearby_count': 0,
                'avg_nearby_density': 0.0,
                'density_rank': 'N/A',
                'relative_score': 'N/A'
            }
        
        nearby_densities = [z['population_density'] for z in nearby_zipcodes]
        avg_nearby_density = sum(nearby_densities) / len(nearby_densities)
        
        # Calculate rank (how many nearby zipcodes have lower density)
        lower_count = sum(1 for d in nearby_densities if d < target_density)
        total_count = len(nearby_densities)
        rank_percentile = (lower_count / total_count * 100) if total_count > 0 else 0
        
        # Determine relative score
        if rank_percentile >= 80:
            relative_score = "Much Higher"
        elif rank_percentile >= 60:
            relative_score = "Higher"
        elif rank_percentile >= 40:
            relative_score = "Average"
        elif rank_percentile >= 20:
            relative_score = "Lower"
        else:
            relative_score = "Much Lower"
        
        return {
            'nearby_count': total_count,
            'avg_nearby_density': round(avg_nearby_density, 1),
            'density_rank_percentile': round(rank_percentile, 1),
            'relative_score': relative_score
        }

# Global instance
density_service = DensityAssessmentService()