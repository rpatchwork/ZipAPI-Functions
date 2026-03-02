# ZipCode Population Density Assessment - Azure Functions

A serverless Azure Functions application that assesses zipcode population density and provides relative comparisons to nearby zipcodes across the United States.

## 🚀 Features

- **Population Density Assessment**: Analyze population density for any US zipcode from a comprehensive dataset of 33,784+ zipcodes
- **Relative Comparisons**: Compare density with nearby zipcodes within a specified radius  
- **National Rankings**: Get percentile rankings compared to all US zipcodes
- **Serverless Architecture**: Azure Functions HTTP triggers with automatic scaling
- **Health Monitoring**: Built-in health check endpoint for service monitoring

## 📊 Dataset

- **Source**: Custom zipcode dataset loaded from C:\temp\zipcode_data.csv
- **Coverage**: 33,784+ US zipcodes with comprehensive geographic and demographic data
- **Data Points**: Latitude, longitude, population density, city, county information

## 🔗 API Endpoints

### Core Functions

- `POST /api/zipcode/density` - Comprehensive zipcode density assessment
- `GET /api/zipcode/{zipcode}/nearby` - Get nearby zipcodes with density comparisons
- `GET /api/zipcode/{zipcode}/stats` - Detailed zipcode statistics and analysis
- `GET /api/health` - Health check and service status

### Example Usage

**Assess Zipcode Density:**
```http
POST /api/zipcode/density
Content-Type: application/json

{
  "zipcode": "10001",
  "radius_miles": 50
}
```

**Get Nearby Zipcodes:**
```http
GET /api/zipcode/10001/nearby?radius=25&limit=10
```

**Get Zipcode Statistics:**
```http
GET /api/zipcode/10001/stats
```

## 📋 Project Structure

```
rp_zip_fx_app/
├── data/
│   └── zipcode_data.csv          # 33,784+ zipcode dataset
├── services/
│   ├── zipcode_data_service.py   # Data loading and geographic calculations
│   └── density_assessment_service.py  # Density scoring and analysis
├── ZipCodeDensityAssessment/     # Main density assessment function
│   ├── __init__.py
│   └── function.json
├── GetNearbyZipcodes/           # Nearby zipcodes function
│   ├── __init__.py
│   └── function.json
├── GetZipcodeStats/             # Statistics function
│   ├── __init__.py
│   └── function.json
├── HealthCheck/                 # Health monitoring function
│   ├── __init__.py
│   └── function.json
├── host.json                    # Function app configuration
├── local.settings.json         # Local development settings
└── requirements.txt            # Python dependencies
```

## 🛠️ Local Development

### Prerequisites
- Python 3.9+
- Azure Functions Core Tools
- Azure CLI (for deployment)

### Setup
1. Install Azure Functions Core Tools
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `func start`
4. Test endpoints at: http://localhost:7071

## 🚀 Deployment to Azure

### Option 1: Azure CLI
```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-zipcode-functions --location eastus

# Create storage account
az storage account create --name zipcodedata --resource-group rg-zipcode-functions

# Create function app
az functionapp create --resource-group rg-zipcode-functions --consumption-plan-location eastus --runtime python --runtime-version 3.9 --functions-version 4 --name zipcode-density-functions --storage-account zipcodedata

# Deploy function code
func azure functionapp publish zipcode-density-functions
```

### Option 2: VS Code Extension
1. Install Azure Functions extension for VS Code
2. Sign in to Azure
3. Deploy using the extension's deployment commands

## 📖 API Documentation

### Density Assessment Response
```json
{
  "zipcode": "10001",
  "city": "New York",
  "county_name": "New York County", 
  "population_density": 74829.78,
  "density_score": 95.8,
  "national_percentile": 99.2,
  "nearby_stats": {
    "nearby_count": 15,
    "avg_nearby_density": 68420.5,
    "relative_score": "Higher"
  },
  "nearby_comparison": [
    {
      "zipcode": "10002",
      "distance_miles": 1.2,
      "population_density": 83927.84,
      "density_score": 97.1
    }
  ]
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "service": "zipcode-population-density-functions",
  "version": "1.0.0",
  "data_service": {
    "status": "operational", 
    "total_zipcodes": 33784
  }
}
```

## 🔧 Configuration

### Function App Settings
- `FUNCTIONS_WORKER_RUNTIME`: python
- `FUNCTIONS_EXTENSION_VERSION`: ~4
- `PYTHON_ENABLE_WORKER_EXTENSIONS`: 1

### Customization
- Modify `radius_miles` default in density assessment (default: 50 miles)
- Adjust `limit` for nearby results (default: 20, max: 100)
- Update density scoring algorithm in `density_assessment_service.py`

## 📊 Performance

- **Cold Start**: ~2-3 seconds for first request
- **Warm Execution**: ~200-500ms for subsequent requests
- **Concurrency**: Automatic scaling based on load
- **Memory**: ~128MB typical usage

## 🏗️ Architecture

**Serverless Design:**
- Azure Functions HTTP triggers for each endpoint
- Shared data service singleton for zipcode data
- Geographic distance calculations using geopy library
- Logarithmic density scoring for normalized comparisons

**Data Flow:**
1. HTTP request triggers Azure Function
2. Data service loads/caches zipcode dataset
3. Geographic calculations find nearby zipcodes
4. Density scoring and percentile calculations
5. JSON response with comprehensive analysis

## 🔍 Monitoring

- Built-in Azure Functions monitoring and logging
- Application Insights integration available
- Health check endpoint for external monitoring
- Structured logging with request/response tracking

---

**Ready for deployment to Azure Function Apps with automatic scaling and serverless architecture!**