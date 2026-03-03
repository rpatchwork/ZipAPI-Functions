import json
import logging
import azure.functions as func

async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function: Swagger UI and OpenAPI documentation
    GET endpoint serving interactive API documentation
    """
    logging.info('SwaggerUI function processed a request.')
    
    # OpenAPI specification
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "ZipCode Population Density Assessment API",
            "description": "A serverless Azure Functions application that assesses zipcode population density and provides relative comparisons to nearby zipcodes across the United States.",
            "version": "1.0.0",
            "contact": {
                "name": "API Support"
            }
        },
        "servers": [
            {
                "url": "https://zipcode-density-api.azurewebsites.net/api",
                "description": "Production server"
            },
            {
                "url": "http://localhost:7071/api",
                "description": "Local development server"
            }
        ],
        "paths": {
            "/zipcode/density": {
                "post": {
                    "summary": "Assess zipcode population density",
                    "description": "Comprehensive zipcode density assessment with nearby comparisons and national percentile ranking",
                    "tags": ["Density Assessment"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "zipcode": {
                                            "type": "string",
                                            "pattern": "^[0-9]{5}$",
                                            "description": "5-digit US zipcode",
                                            "example": "10001"
                                        },
                                        "radius_miles": {
                                            "type": "number",
                                            "minimum": 1,
                                            "maximum": 500,
                                            "default": 50,
                                            "description": "Search radius for nearby zipcodes in miles",
                                            "example": 50
                                        }
                                    },
                                    "required": ["zipcode"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful density assessment",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/DensityAssessmentResponse"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request - invalid zipcode or parameters"
                        },
                        "404": {
                            "description": "Zipcode not found"
                        },
                        "500": {
                            "description": "Internal server error"
                        }
                    }
                }
            },
            "/zipcode/{zipcode}/nearby": {
                "get": {
                    "summary": "Get nearby zipcodes",
                    "description": "Find nearby zipcodes within specified radius with density comparisons",
                    "tags": ["Geographic Analysis"],
                    "parameters": [
                        {
                            "name": "zipcode",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "pattern": "^[0-9]{5}$"
                            },
                            "description": "5-digit US zipcode",
                            "example": "10001"
                        },
                        {
                            "name": "radius",
                            "in": "query",
                            "schema": {
                                "type": "number",
                                "default": 50,
                                "minimum": 1,
                                "maximum": 500
                            },
                            "description": "Search radius in miles",
                            "example": 25
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {
                                "type": "integer",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "description": "Maximum number of results to return",
                            "example": 10
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful nearby search",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/NearbyZipcodesResponse"
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Zipcode not found"
                        },
                        "500": {
                            "description": "Internal server error"
                        }
                    }
                }
            },
            "/zipcode/{zipcode}/stats": {
                "get": {
                    "summary": "Get zipcode statistics",
                    "description": "Detailed zipcode information and statistics",
                    "tags": ["Statistics"],
                    "parameters": [
                        {
                            "name": "zipcode",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "pattern": "^[0-9]{5}$"
                            },
                            "description": "5-digit US zipcode",
                            "example": "10001"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successful statistics retrieval",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ZipcodeStatsResponse"
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Zipcode not found"
                        },
                        "500": {
                            "description": "Internal server error"
                        }
                    }
                }
            },
            "/health": {
                "get": {
                    "summary": "Health check",
                    "description": "Service health and status endpoint",
                    "tags": ["Monitoring"],
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/HealthResponse"
                                    }
                                }
                            }
                        },
                        "503": {
                            "description": "Service is unhealthy"
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "DensityAssessmentResponse": {
                    "type": "object",
                    "properties": {
                        "zipcode": {"type": "string", "example": "10001"},
                        "city": {"type": "string", "example": "New York"},
                        "county_name": {"type": "string", "example": "New York County"},
                        "latitude": {"type": "number", "example": 40.7505},
                        "longitude": {"type": "number", "example": -73.9934},
                        "population": {"type": "integer", "example": 21102},
                        "area_sq_miles": {"type": "number", "example": 0.282},
                        "population_density": {"type": "number", "example": 74829.78},
                        "density_score": {"type": "number", "example": 95.8},
                        "national_percentile": {"type": "number", "example": 99.2},
                        "nearby_stats": {
                            "type": "object",
                            "properties": {
                                "nearby_count": {"type": "integer"},
                                "avg_nearby_density": {"type": "number"},
                                "density_rank_percentile": {"type": "number"},
                                "relative_score": {"type": "string"}
                            }
                        },
                        "nearby_comparison": {
                            "type": "array",
                            "items": {
                                "$ref": "#/components/schemas/NearbyZipcode"
                            }
                        },
                        "search_radius_miles": {"type": "number", "example": 50}
                    }
                },
                "NearbyZipcodesResponse": {
                    "type": "object",
                    "properties": {
                        "center_zipcode": {
                            "$ref": "#/components/schemas/ZipcodeInfo"
                        },
                        "search_parameters": {
                            "type": "object",
                            "properties": {
                                "radius_miles": {"type": "number"},
                                "limit": {"type": "integer"}
                            }
                        },
                        "nearby_zipcodes": {
                            "type": "array",
                            "items": {
                                "$ref": "#/components/schemas/NearbyZipcode"
                            }
                        },
                        "total_found": {"type": "integer"},
                        "returned_count": {"type": "integer"}
                    }
                },
                "ZipcodeStatsResponse": {
                    "type": "object",
                    "properties": {
                        "zipcode": {"type": "string"},
                        "location": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string"},
                                "county_name": {"type": "string"},
                                "latitude": {"type": "number"},
                                "longitude": {"type": "number"}
                            }
                        },
                        "demographics": {
                            "type": "object",
                            "properties": {
                                "population": {"type": "integer"},
                                "area_sq_miles": {"type": "number"},
                                "population_density": {"type": "number"}
                            }
                        },
                        "density_analysis": {
                            "type": "object",
                            "properties": {
                                "density_score": {"type": "number"},
                                "national_percentile": {"type": "number"},
                                "classification": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        },
                        "national_context": {
                            "type": "object",
                            "properties": {
                                "total_zipcodes_in_dataset": {"type": "integer"},
                                "national_density_range": {
                                    "type": "object",
                                    "properties": {
                                        "min": {"type": "number"},
                                        "max": {"type": "number"},
                                        "mean": {"type": "number"},
                                        "median": {"type": "number"}
                                    }
                                }
                            }
                        }
                    }
                },
                "NearbyZipcode": {
                    "type": "object",
                    "properties": {
                        "zipcode": {"type": "string"},
                        "city": {"type": "string"},
                        "county_name": {"type": "string"},
                        "distance_miles": {"type": "number"},
                        "population_density": {"type": "number"},
                        "density_score": {"type": "number"},
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"}
                    }
                },
                "ZipcodeInfo": {
                    "type": "object",
                    "properties": {
                        "zipcode": {"type": "string"},
                        "city": {"type": "string"},
                        "county_name": {"type": "string"},
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "population_density": {"type": "number"},
                        "density_score": {"type": "number"}
                    }
                },
                "HealthResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "healthy"},
                        "service": {"type": "string", "example": "zipcode-population-density-functions"},
                        "version": {"type": "string", "example": "1.0.0"},
                        "timestamp": {"type": "string", "format": "date-time"},
                        "data_service": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "total_zipcodes": {"type": "integer"}
                            }
                        },
                        "endpoints": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "method": {"type": "string"},
                                    "path": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Check if requesting raw OpenAPI spec
    format_param = req.params.get('format', '').lower()
    if format_param == 'json':
        return func.HttpResponse(
            json.dumps(openapi_spec, indent=2),
            status_code=200,
            mimetype="application/json"
        )
    
    # Generate Swagger UI HTML
    swagger_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ZipCode API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui.css" />
    <style>
        html {{ box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }}
        *, *:before, *:after {{ box-sizing: inherit; }}
        body {{ margin:0; background: #fafafa; }}
        .download-container {{ 
            position: fixed; top: 10px; right: 10px; z-index: 1000; 
            background: #fff; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .download-link {{ 
            background: #4CAF50; color: white; padding: 8px 16px; text-decoration: none; 
            border-radius: 4px; font-size: 14px; font-weight: 500;
        }}
        .download-link:hover {{ background: #45a049; color: white; }}
    </style>
</head>
<body>
    <div class="download-container">
        <a href="{window.location.origin + window.location.pathname}?format=json" 
           class="download-link" download="openapi.json">📥 Download OpenAPI JSON</a>
    </div>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.5/swagger-ui-standalone-preset.js"></script>
    <script>
    window.onload = function() {{
        // Update download button href with current URL
        const downloadBtn = document.querySelector('.download-link');
        if (downloadBtn) {{
            downloadBtn.href = window.location.origin + window.location.pathname + '?format=json';
        }}
        
        // Initialize Swagger UI
        const ui = SwaggerUIBundle({{
            url: window.location.origin + window.location.pathname + '?format=json',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIStandalonePreset
            ],
            plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout",
            validatorUrl: null,  // Disable validator
            displayRequestDuration: true,
            tryItOutEnabled: true,
            requestInterceptor: function(request) {{
                // Add any custom headers if needed
                return request;
            }}
        }});
    }};
    </script>
</body>
</html>
    """
    
    return func.HttpResponse(
        swagger_html,
        status_code=200,
        mimetype="text/html"
    )