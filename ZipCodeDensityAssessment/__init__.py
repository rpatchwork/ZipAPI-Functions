import json
import logging
import azure.functions as func
from services.density_assessment_service import density_service

async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function: Assess zipcode population density
    POST endpoint for comprehensive zipcode density analysis
    """
    logging.info('ZipCode density assessment function processed a request.')
    
    try:
        # Parse request body
        try:
            req_body = req.get_json()
            if not req_body:
                return func.HttpResponse(
                    json.dumps({"error": "Request body is required"}),
                    status_code=400,
                    mimetype="application/json"
                )
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Extract parameters
        zipcode = req_body.get('zipcode')
        if not zipcode:
            return func.HttpResponse(
                json.dumps({"error": "zipcode parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        radius_miles = req_body.get('radius_miles', 50.0)
        if not isinstance(radius_miles, (int, float)) or radius_miles <= 0:
            radius_miles = 50.0
        
        # Assess zipcode density
        result = await density_service.assess_zipcode_density(
            zipcode=str(zipcode).zfill(5),
            radius_miles=float(radius_miles)
        )
        
        if not result:
            return func.HttpResponse(
                json.dumps({"error": f"Zipcode {zipcode} not found"}),
                status_code=404,
                mimetype="application/json"
            )
        
        # Return successful response
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in ZipCodeDensityAssessment function: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json"
        )