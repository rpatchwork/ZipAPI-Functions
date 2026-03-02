# GitHub to Azure Functions Deployment Plan

## Overview
Complete plan to publish the ZipCode Population Density API to GitHub and deploy to Azure Functions with automated CI/CD pipeline.

## Phase 1: GitHub Repository Setup (15 minutes)

### Prerequisites
- Git installed and configured
- GitHub CLI installed (`winget install --id GitHub.cli`)
- GitHub account with appropriate permissions

### Steps
1. **Initialize Repository**
   ```powershell
   .\setup-github.ps1
   ```

2. **Custom Configuration** (Optional)
   ```powershell
   .\setup-github.ps1 -RepoName "custom-zipcode-api" -IsPrivate $true
   ```

3. **Manual GitHub Setup** (Alternative)
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Azure Functions ZipCode API"
   gh repo create ZipAPI-Functions --public --source . --remote origin --push
   ```

### Deliverables
- ✅ GitHub repository: `https://github.com/{username}/ZipAPI-Functions`
- ✅ Initial codebase pushed with comprehensive README
- ✅ Repository topics and description configured
- ✅ .gitignore optimized for Azure Functions

## Phase 2: Azure Resources Setup (20 minutes)

### Prerequisites
- Azure CLI installed (`winget install -e --id Microsoft.AzureCLI`)
- Azure Functions Core Tools (`npm install -g azure-functions-core-tools@4 --unsafe-perm true`)
- Active Azure subscription with contributor access

### Automated Deployment
```powershell
.\deploy-azure.ps1
```

### Custom Deployment
```powershell
.\deploy-azure.ps1 -FunctionAppName "my-zipcode-api" -Location "westus2" -ResourceGroupName "rg-my-zipcode"
```

### Manual Azure Setup
```bash
# Create resource group
az group create --name rg-zipcode-functions --location eastus2

# Create storage account
az storage account create --name zipcodestorageacct --resource-group rg-zipcode-functions --location eastus2 --sku Standard_LRS

# Create Function App
az functionapp create --resource-group rg-zipcode-functions --consumption-plan-location eastus2 --runtime python --runtime-version 3.11 --functions-version 4 --name zipcode-density-api --storage-account zipcodestorageacct --os-type linux

# Deploy functions
func azure functionapp publish zipcode-density-api --build remote --python
```

### Azure Resources Created
- **Resource Group**: `rg-zipcode-functions`
- **Storage Account**: `zipcodestorageacct` (Standard_LRS)
- **Function App**: `zipcode-density-api` (Consumption Plan)
- **Runtime**: Python 3.11 on Linux

## Phase 3: CI/CD Pipeline Configuration (10 minutes)

### GitHub Actions Secrets Setup
1. **Create Azure Service Principal**
   ```bash
   az ad sp create-for-rbac --name "ZipAPI-Functions-deploy" --role contributor --scopes /subscriptions/{subscription-id} --sdk-auth
   ```

2. **Add GitHub Secrets** (Repository Settings > Secrets and variables > Actions)
   - `AZURE_CREDENTIALS` - Service principal JSON output
   - `AZURE_FUNCTIONAPP_NAME` - Function app name (e.g., `zipcode-density-api`)
   - `AZURE_FUNCTIONAPP_RESOURCE_GROUP` - Resource group name (e.g., `rg-zipcode-functions`)

### GitHub Actions Workflow
The pipeline (`.github/workflows/deploy-azure-functions.yml`) includes:
- **Build**: Python 3.11 setup, dependency installation
- **Test**: Data validation, endpoint testing
- **Deploy**: Azure Functions deployment with remote build
- **Verify**: Post-deployment endpoint validation

### Trigger Deployment
```bash
git push origin main
```

## Phase 4: Data and Configuration Management (5 minutes)

### Data File Validation
- ✅ **Zipcode Dataset**: 33,784+ records (data/zipcode_data.csv)
- ✅ **File Size**: ~3.2 MB (within Azure Functions limits)
- ✅ **Data Quality**: Population density, coordinates, demographics

### Configuration Files
- ✅ **host.json**: Azure Functions runtime configuration
- ✅ **requirements.txt**: Python dependencies (pandas, geopy, pydantic)
- ✅ **local.settings.json**: Local development settings (not deployed)

### Application Settings
```json
{
  "PYTHON_ENABLE_WORKER_EXTENSIONS": "1",
  "FUNCTIONS_WORKER_RUNTIME": "python",
  "FUNCTIONS_EXTENSION_VERSION": "~4",
  "WEBSITE_RUN_FROM_PACKAGE": "1"
}
```

## Phase 5: Testing and Validation (10 minutes)

### Local Testing
```powershell
# Start local Functions runtime
func start

# Test endpoints
.\test-api.ps1
```

### Production Testing
```powershell
# Health check
$baseUrl = "https://{function-app-name}.azurewebsites.net/api"
Invoke-RestMethod "$baseUrl/health"

# Swagger documentation
Start-Process "$baseUrl/docs"

# Test density assessment
$body = @{ zipcode = "10001"; radius_miles = 25 } | ConvertTo-Json
Invoke-RestMethod "$baseUrl/zipcode/density" -Method POST -Body $body -ContentType "application/json"
```

### Monitoring Setup
- **Application Insights**: Available through Azure Portal
- **Function App Logs**: Monitor via Azure Portal or Azure CLI
- **GitHub Actions**: Deployment status and logs

## Phase 6: Production Configuration (5 minutes)

### Performance Optimization
- **Consumption Plan**: Pay-per-execution, auto-scaling
- **Cold Start**: Optimized with lightweight initialization
- **Memory Usage**: ~200MB for dataset loading

### Security Configuration
- **HTTPS Only**: Enforced by default
- **Function Keys**: Available for additional security
- **CORS**: Configure if needed for web frontend

### Cost Estimation
- **Consumption Plan**: ~$0.20 per million executions
- **Storage Account**: ~$0.05/month for function storage
- **Data Transfer**: Minimal for typical API usage
- **Total Estimated**: $5-15/month for moderate usage

## Deployment Commands Summary

### Quick Start (Full Automation)
```powershell
# Setup GitHub repository
.\setup-github.ps1

# Deploy to Azure
.\deploy-azure.ps1

# Test deployment
Start-Process "https://{function-app-name}.azurewebsites.net/api/docs"
```

### Manual Process
```bash
# 1. Initialize Git and GitHub
git init
gh repo create ZipAPI-Functions --public --source . --remote origin --push

# 2. Create Azure resources
az group create --name rg-zipcode-functions --location eastus2
az storage account create --name zipcodestorageacct --resource-group rg-zipcode-functions --sku Standard_LRS --location eastus2
az functionapp create --name zipcode-density-api --storage-account zipcodestorageacct --resource-group rg-zipcode-functions --consumption-plan-location eastus2 --runtime python --runtime-version 3.11 --functions-version 4 --os-type linux

# 3. Deploy functions
func azure functionapp publish zipcode-density-api --build remote --python

# 4. Test deployment
curl "https://zipcode-density-api.azurewebsites.net/api/health"
```

## Expected Timeline
- **GitHub Setup**: 15 minutes
- **Azure Resources**: 20 minutes  
- **CI/CD Configuration**: 10 minutes
- **Testing**: 10 minutes
- **Documentation**: 5 minutes
- **Total**: ~60 minutes for complete setup

## Success Criteria
- ✅ GitHub repository with complete codebase
- ✅ Azure Function App successfully deployed
- ✅ All 5 API endpoints operational
- ✅ Swagger UI accessible and functional
- ✅ Health endpoint returns dataset statistics
- ✅ CI/CD pipeline triggers on code changes
- ✅ Performance within acceptable limits (<2s response times)

## Support and Troubleshooting

### Common Issues
1. **Function App Name Conflict**: Azure Function App names are globally unique
2. **Cold Start Delays**: First request after idle period may take 5-10 seconds
3. **Data Loading**: 33K+ zipcode dataset loads during function initialization

### Debugging Commands
```powershell
# View function app logs
func azure functionapp logstream zipcode-density-api --resource-group rg-zipcode-functions

# Test local development
func start --python

# Check Azure CLI authentication
az account show
```

### Monitoring URLs
- **Azure Portal**: https://portal.azure.com
- **Function App Metrics**: Portal > Function App > Monitoring
- **Application Insights**: Portal > Function App > Application Insights
- **GitHub Actions**: Repository > Actions tab

## API Documentation

### Endpoints
- **Health Check**: `GET /api/health`
- **Swagger UI**: `GET /api/docs`
- **Zipcode Stats**: `GET /api/zipcode/{zipcode}/stats`
- **Nearby Zipcodes**: `GET /api/zipcode/{zipcode}/nearby`
- **Density Assessment**: `POST /api/zipcode/density`

### Example Usage
```javascript
// Density assessment
const response = await fetch('https://zipcode-density-api.azurewebsites.net/api/zipcode/density', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ zipcode: '10001', radius_miles: 25 })
});

const assessment = await response.json();
console.log(assessment.density_score); // 0-100 density score
```

---
**Ready to deploy?** Run `.\setup-github.ps1` followed by `.\deploy-azure.ps1` to get started! 🚀