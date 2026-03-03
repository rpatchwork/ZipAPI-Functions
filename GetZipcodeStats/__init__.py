import json
import logging
import azure.functions as func
from services.zipcode_data_service import zipcode_service
from services.density_assessment_service import density_service

async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function: Get detailed zipcode statistics
    GET endpoint for retrieving comprehensive zipcode information
    """
    logging.info('GetZipcodeStats function processed a request.')
    
    try:
        # Ensure data service is initialized
        await zipcode_service.initialize()
        
        # Extract zipcode from route
        zipcode = req.route_params.get('zipcode')
        if not zipcode:
            return func.HttpResponse(
                json.dumps({"error": "zipcode parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get zipcode info
        zipcode_info = zipcode_service.get_zipcode_info(zipcode)
        if not zipcode_info:
            return func.HttpResponse(
                json.dumps({"error": f"Zipcode {zipcode} not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        # Calculate additional statistics
        population_density = zipcode_info['population_density']
        density_score = density_service.calculate_density_score(population_density)
        national_percentile = zipcode_service.calculate_national_percentile(population_density)
        overall_stats = zipcode_service.get_density_stats()
        
        result = {
            'zipcode': zipcode_info['zipcode'],
            'location': {
                'city': zipcode_info['city'],
                'county_name': zipcode_info['county_name'],
                'latitude': zipcode_info['latitude'],
                'longitude': zipcode_info['longitude']
            },
            'demographics': {
                'population': zipcode_info['population'],
                'area_sq_miles': zipcode_info['area_sq_miles'],
                'population_density': population_density
            },
            'density_analysis': {
                'density_score': density_score,
                'national_percentile': national_percentile,
                'classification': _get_density_classification(density_score),
                'description': _get_density_description(population_density, national_percentile)
            },
            'national_context': {
                'total_zipcodes_in_dataset': overall_stats['total_zipcodes'],
                'national_density_range': {
                    'min': overall_stats['min_density'],
                    'max': overall_stats['max_density'],
                    'mean': overall_stats['mean_density'],
                    'median': overall_stats['median_density']
                }
            }
        }
        
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in GetZipcodeStats function: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

def _get_density_classification(density_score: float) -> str:
    """Get density classification based on score"""
    if density_score >= 90:
        return "Very High Density"
    elif density_score >= 75:
        return "High Density"
    elif density_score >= 50:
        return "Moderate Density"
    elif density_score >= 25:
        return "Low Density"
    else:
        return "Very Low Density"

def _get_density_description(density: float, percentile: float) -> str:
    """Get human-readable description of density"""
    if percentile >= 95:
        return f"Extremely dense urban area ({density:,.1f} people/sq mi) - among the top 5% densest areas in the dataset"
    elif percentile >= 90:
        return f"Very high density urban area ({density:,.1f} people/sq mi) - denser than {percentile}% of all areas"
    elif percentile >= 75:
        return f"High density area ({density:,.1f} people/sq mi) - denser than {percentile}% of all areas"
    elif percentile >= 50:
        return f"Moderate density area ({density:,.1f} people/sq mi) - denser than {percentile}% of all areas"
    elif percentile >= 25:
        return f"Lower density area ({density:,.1f} people/sq mi) - denser than {percentile}% of all areas"
    else:
        return f"Low density rural area ({density:,.1f} people/sq mi) - among the least dense areas"