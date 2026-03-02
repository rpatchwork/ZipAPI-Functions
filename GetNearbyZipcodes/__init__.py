import json
import logging
import azure.functions as func
from services.zipcode_data_service import zipcode_service
from services.density_assessment_service import density_service

async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function: Get nearby zipcodes with density comparisons
    GET endpoint for finding nearby zipcodes within specified radius
    """
    logging.info('GetNearbyZipcodes function processed a request.')
    
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
        
        # Extract query parameters
        radius_miles = float(req.params.get('radius', 50.0))
        limit = int(req.params.get('limit', 20))
        
        if radius_miles <= 0:
            radius_miles = 50.0
        if limit <= 0 or limit > 100:
            limit = 20
        
        # Get zipcode info
        zipcode_info = zipcode_service.get_zipcode_info(zipcode)
        if not zipcode_info:
            return func.HttpResponse(
                json.dumps({"error": f"Zipcode {zipcode} not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        # Get nearby zipcodes
        nearby_zipcodes = zipcode_service.get_nearby_zipcodes(zipcode, radius_miles)
        
        # Limit results and add density scores
        limited_nearby = nearby_zipcodes[:limit]
        for nearby in limited_nearby:
            nearby['density_score'] = density_service.calculate_density_score(
                nearby['population_density']
            )
        
        result = {
            'center_zipcode': {
                'zipcode': zipcode_info['zipcode'],
                'city': zipcode_info['city'],
                'county_name': zipcode_info['county_name'],
                'latitude': zipcode_info['latitude'],
                'longitude': zipcode_info['longitude'],
                'population_density': zipcode_info['population_density'],
                'density_score': density_service.calculate_density_score(zipcode_info['population_density'])
            },
            'search_parameters': {
                'radius_miles': radius_miles,
                'limit': limit
            },
            'nearby_zipcodes': limited_nearby,
            'total_found': len(nearby_zipcodes),
            'returned_count': len(limited_nearby)
        }
        
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as ve:
        logging.error(f"Value error in GetNearbyZipcodes: {str(ve)}")
        return func.HttpResponse(
            json.dumps({"error": "Invalid parameter value", "details": str(ve)}),
            status_code=400,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error in GetNearbyZipcodes function: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )