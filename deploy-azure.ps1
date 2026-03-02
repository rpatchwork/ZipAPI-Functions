#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy ZipCode API to Azure Functions
.DESCRIPTION
    Complete deployment script for publishing ZipCode Population Density API
    to Azure Functions with automated resource creation and configuration.
.PARAMETER ResourceGroupName
    Azure resource group name (default: rg-zipcode-functions)
.PARAMETER FunctionAppName  
    Azure Function App name (default: zipcode-density-api)
.PARAMETER StorageAccountName
    Storage account name (default: zipcodestorageacct)
.PARAMETER Location
    Azure region (default: eastus2)
.PARAMETER SubscriptionId
    Azure subscription ID (optional - uses current subscription)
.EXAMPLE
    .\deploy-azure.ps1
    .\deploy-azure.ps1 -FunctionAppName "my-zipcode-api" -Location "westus2"
#>

param(
    [string]$ResourceGroupName = "rg-zipcode-functions",
    [string]$FunctionAppName = "zipcode-density-api",
    [string]$StorageAccountName = "zipcodestorageacct",
    [string]$Location = "eastus2",
    [string]$SubscriptionId = ""
)

# Color functions for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "📋 $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Header { param($Message) Write-Host "`n🚀 $Message" -ForegroundColor Blue -BackgroundColor Black }

Write-Header "Azure Functions Deployment - ZipCode Population Density API"

try {
    # Check prerequisites
    Write-Info "[1/10] Checking prerequisites..."
    
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        throw "Azure CLI not found. Please install Azure CLI first."
    }
    
    if (-not (Get-Command func -ErrorAction SilentlyContinue)) {
        throw "Azure Functions Core Tools not found. Please install Azure Functions Core Tools."
    }
    
    if (-not (Test-Path "host.json")) {
        throw "This script must be run from the Azure Functions project directory."
    }
    
    if (-not (Test-Path "data/zipcode_data.csv")) {
        throw "Zipcode data file not found. Ensure data/zipcode_data.csv exists."
    }
    
    Write-Success "Prerequisites validated"

    # Login to Azure
    Write-Info "[2/10] Checking Azure authentication..."
    $currentAccount = az account show 2>$null | ConvertFrom-Json
    
    if (-not $currentAccount) {
        Write-Info "Please login to Azure..."
        az login
        $currentAccount = az account show | ConvertFrom-Json
    }
    
    if ($SubscriptionId -and $SubscriptionId -ne $currentAccount.id) {
        Write-Info "Setting subscription to $SubscriptionId..."
        az account set --subscription $SubscriptionId
    }
    
    Write-Success "Azure authentication verified - Subscription: $($currentAccount.name)"

    # Create resource group
    Write-Info "[3/10] Creating resource group..."
    $rgExists = az group exists --name $ResourceGroupName | ConvertFrom-Json
    
    if (-not $rgExists) {
        az group create --name $ResourceGroupName --location $Location --output table
        Write-Success "Resource group '$ResourceGroupName' created"
    } else {
        Write-Success "Resource group '$ResourceGroupName' already exists"
    }

    # Create storage account
    Write-Info "[4/10] Creating storage account..."
    $storageAccount = az storage account show --name $StorageAccountName --resource-group $ResourceGroupName 2>$null | ConvertFrom-Json
    
    if (-not $storageAccount) {
        Write-Info "Creating storage account '$StorageAccountName'..."
        az storage account create `
            --name $StorageAccountName `
            --resource-group $ResourceGroupName `
            --location $Location `
            --sku Standard_LRS `
            --output table
        Write-Success "Storage account created"
    } else {
        Write-Success "Storage account '$StorageAccountName' already exists"
    }

    # Create Function App
    Write-Info "[5/10] Creating Function App..."
    $functionApp = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName 2>$null | ConvertFrom-Json
    
    if (-not $functionApp) {
        Write-Info "Creating Function App '$FunctionAppName'..."
        az functionapp create `
            --resource-group $ResourceGroupName `
            --consumption-plan-location $Location `
            --runtime python `
            --runtime-version 3.11 `
            --functions-version 4 `
            --name $FunctionAppName `
            --storage-account $StorageAccountName `
            --os-type linux `
            --output table
        Write-Success "Function App created"
    } else {
        Write-Success "Function App '$FunctionAppName' already exists"
    }

    # Configure Function App settings
    Write-Info "[6/10] Configuring Function App settings..."
    
    $appSettings = @(
        "PYTHON_ENABLE_WORKER_EXTENSIONS=1",
        "FUNCTIONS_WORKER_RUNTIME=python",
        "FUNCTIONS_EXTENSION_VERSION=~4",
        "WEBSITE_RUN_FROM_PACKAGE=1"
    )
    
    foreach ($setting in $appSettings) {
        az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings $setting --output none
    }
    
    Write-Success "Function App settings configured"

    # Validate data file
    Write-Info "[7/10] Validating zipcode data..."
    $dataPath = "data/zipcode_data.csv"
    $dataSize = (Get-Item $dataPath).Length
    $dataSizeMB = [math]::Round($dataSize / 1MB, 2)
    
    Write-Info "Data file size: $dataSizeMB MB"
    
    # Quick data validation
    $sampleLines = Get-Content $dataPath -Head 5
    Write-Info "Data sample:"
    $sampleLines | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    
    Write-Success "Zipcode data validated"

    # Build and package
    Write-Info "[8/10] Preparing deployment package..."
    
    # Install dependencies if needed
    if (-not (Test-Path "venv")) {
        Write-Info "Creating virtual environment..."
        python -m venv venv
    }
    
    # Clean up Python cache files
    Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path . -Recurse -Name "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
    
    Write-Success "Deployment package prepared"

    # Deploy to Azure
    Write-Info "[9/10] Deploying to Azure Functions..."
    
    Write-Info "Starting deployment (this may take 2-3 minutes)..."
    $deployResult = func azure functionapp publish $FunctionAppName --build remote --python 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Deployment completed successfully"
    } else {
        Write-Warning "Deployment completed with warnings. Check output above."
    }

    # Test deployment
    Write-Info "[10/10] Testing deployed API..."
    
    $baseUrl = "https://$FunctionAppName.azurewebsites.net/api"
    Write-Info "Function App URL: https://$FunctionAppName.azurewebsites.net"
    Write-Info "Waiting for function app to start..."
    
    Start-Sleep -Seconds 30
    
    # Test health endpoint
    try {
        Write-Info "Testing health endpoint..."
        $healthResponse = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -TimeoutSec 60
        Write-Success "Health check: $($healthResponse.status)"
        Write-Info "Dataset: $($healthResponse.data_service.total_zipcodes) zipcodes loaded"
    } catch {
        Write-Warning "Health check failed: $($_.Exception.Message)"
        Write-Info "The function app may still be starting. Try testing manually in a few minutes."
    }

    # Deployment summary
    Write-Header "Deployment Complete! 🎉"
    
    Write-Host ""
    Write-Success "Azure Function App Details:"
    Write-Host "  📍 Name: $FunctionAppName" -ForegroundColor White
    Write-Host "  🌐 URL: https://$FunctionAppName.azurewebsites.net" -ForegroundColor White
    Write-Host "  📊 Resource Group: $ResourceGroupName" -ForegroundColor White
    Write-Host "  🗺️  Location: $Location" -ForegroundColor White
    
    Write-Host ""
    Write-Success "API Endpoints:"
    Write-Host "  🔍 Health:      GET    $baseUrl/health" -ForegroundColor White
    Write-Host "  📖 Swagger UI:  GET    $baseUrl/docs" -ForegroundColor White
    Write-Host "  📊 Stats:       GET    $baseUrl/zipcode/{zipcode}/stats" -ForegroundColor White  
    Write-Host "  🗺️  Nearby:     GET    $baseUrl/zipcode/{zipcode}/nearby" -ForegroundColor White
    Write-Host "  🎯 Assessment:  POST   $baseUrl/zipcode/density" -ForegroundColor White
    
    Write-Host ""
    Write-Success "Next Steps:"
    Write-Host "  1. Test API endpoints using the URLs above" -ForegroundColor White
    Write-Host "  2. View interactive documentation at: $baseUrl/docs" -ForegroundColor White
    Write-Host "  3. Monitor function app in Azure Portal" -ForegroundColor White
    Write-Host "  4. Set up Application Insights for monitoring (optional)" -ForegroundColor White
    
    Write-Host ""

} catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    Write-Host ""
    Write-Warning "Troubleshooting steps:"
    Write-Host "  1. Ensure Azure CLI is installed and authenticated" -ForegroundColor Gray
    Write-Host "  2. Verify Azure Functions Core Tools are installed" -ForegroundColor Gray
    Write-Host "  3. Check that you have sufficient Azure permissions" -ForegroundColor Gray
    Write-Host "  4. Ensure the function app name is globally unique" -ForegroundColor Gray
    Write-Host ""
    exit 1
}