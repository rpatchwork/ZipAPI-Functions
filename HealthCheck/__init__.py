import json
import logging
from datetime import datetime, timezone
import azure.functions as func
from services.zipcode_data_service import zipcode_service

async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function: Health Check endpoint
    GET endpoint for service health monitoring
    """
    logging.info('HealthCheck function processed a request.')
    
    try:
        # Test data service initialization
        await zipcode_service.initialize()
        stats = zipcode_service.get_density_stats()
        
        result = {
            'status': 'healthy',
            'service': 'zipcode-population-density-functions',
            'version': '1.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data_service': {
                'status': 'operational',
                'total_zipcodes': stats['total_zipcodes']
            },
            'endpoints': [
                {
                    'method': 'POST',
                    'path': '/api/zipcode/density',
                    'description': 'Assess zipcode population density'
                },
                {
                    'method': 'GET', 
                    'path': '/api/zipcode/{zipcode}/nearby',
                    'description': 'Get nearby zipcodes with comparisons'
                },
                {
                    'method': 'GET',
                    'path': '/api/zipcode/{zipcode}/stats', 
                    'description': 'Get detailed zipcode statistics'
                },
                {
                    'method': 'GET',
                    'path': '/api/health',
                    'description': 'Health check endpoint'
                }
            ]
        }
        
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        
        error_result = {
            'status': 'unhealthy',
            'service': 'zipcode-population-density-functions',
            'version': '1.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e),
            'data_service': {
                'status': 'error'
            }
        }
        
        return func.HttpResponse(
            json.dumps(error_result, indent=2),
            status_code=503,
            mimetype="application/json"
        )