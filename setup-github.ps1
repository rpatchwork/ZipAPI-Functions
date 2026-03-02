#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Initialize GitHub repository for ZipCode API Functions
.DESCRIPTION
    Sets up GitHub repository with proper configuration for Azure Functions deployment
.PARAMETER RepoName
    GitHub repository name (default: ZipAPI-Functions)
.PARAMETER IsPrivate
    Create private repository (default: false)
.PARAMETER Description
    Repository description
.EXAMPLE
    .\setup-github.ps1
    .\setup-github.ps1 -RepoName "my-zipcode-api" -IsPrivate $true
#>

param(
    [string]$RepoName = "ZipAPI-Functions",
    [bool]$IsPrivate = $false,
    [string]$Description = "Azure Functions API for ZipCode Population Density Assessment - Serverless population density analysis with 33,000+ zipcodes"
)

# Color functions for output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "📋 $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Header { param($Message) Write-Host "`n🚀 $Message" -ForegroundColor Blue -BackgroundColor Black }

Write-Header "GitHub Repository Setup - ZipCode Population Density API"

try {
    # Check prerequisites
    Write-Info "[1/8] Checking prerequisites..."
    
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git not found. Please install Git first."
    }
    
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "GitHub CLI not found. Please install GitHub CLI first."
    }
    
    if (-not (Test-Path "host.json")) {
        throw "This script must be run from the Azure Functions project directory."
    }
    
    Write-Success "Prerequisites validated"

    # Check GitHub CLI authentication
    Write-Info "[2/8] Checking GitHub authentication..."
    
    try {
        $authStatus = gh auth status 2>&1
        Write-Success "GitHub CLI authenticated"
    } catch {
        Write-Info "Please authenticate with GitHub CLI..."
        gh auth login
        Write-Success "GitHub authentication completed"
    }

    # Initialize git repository if not already done
    Write-Info "[3/8] Initializing git repository..."
    
    if (-not (Test-Path ".git")) {
        git init
        Write-Success "Git repository initialized"
    } else {
        Write-Success "Git repository already exists"
    }

    # Create comprehensive .gitignore if it doesn't exist
    Write-Info "[4/8] Setting up .gitignore..."
    
    if (-not (Test-Path ".gitignore")) {
        $gitignoreContent = @"
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Azure Functions artifacts
bin
obj
appsettings.json
local.settings.json

# IDE files
.vscode/settings.json
.vscode/launch.json
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Azure deployment logs
.azure/
deployment/
"@
        Set-Content -Path ".gitignore" -Value $gitignoreContent
        Write-Success ".gitignore created"
    } else {
        Write-Success ".gitignore already exists"
    }

    # Add all files to git
    Write-Info "[5/8] Adding files to git..."
    
    git add .
    $status = git status --porcelain
    
    if ($status) {
        git commit -m "Initial commit: Azure Functions ZipCode Population Density API

Features:
- Comprehensive zipcode density assessment with 33,784+ zipcodes
- Geographic proximity analysis with configurable radius
- Population density scoring with national percentile ranking
- RESTful API with Swagger/OpenAPI documentation
- Azure Functions serverless architecture
- CI/CD pipeline with GitHub Actions
- Health monitoring and error handling

Endpoints:
- POST /api/zipcode/density - Comprehensive density assessment
- GET /api/zipcode/{zipcode}/stats - Basic zipcode statistics  
- GET /api/zipcode/{zipcode}/nearby - Find nearby zipcodes
- GET /api/health - Health check and system status
- GET /api/docs - Interactive Swagger documentation"

        Write-Success "Initial commit created"
    } else {
        Write-Success "No changes to commit"
    }

    # Create GitHub repository
    Write-Info "[6/8] Creating GitHub repository..."
    
    $visibilityFlag = if ($IsPrivate) { "--private" } else { "--public" }
    
    try {
        gh repo create $RepoName $visibilityFlag --description $Description --source . --remote origin --push
        Write-Success "GitHub repository '$RepoName' created and pushed"
    } catch {
        Write-Warning "Repository may already exist or there was an error: $($_.Exception.Message)"
        Write-Info "Attempting to add remote and push..."
        
        try {
            git remote add origin "https://github.com/$(gh api user --jq .login)/$RepoName.git" 2>$null
            git branch -M main
            git push -u origin main
            Write-Success "Code pushed to existing repository"
        } catch {
            Write-Error "Failed to push to repository: $($_.Exception.Message)"
        }
    }

    # Get repository URL
    $repoUrl = gh repo view --json url --jq .url
    Write-Success "Repository URL: $repoUrl"

    # Create repository topics/tags
    Write-Info "[7/8] Adding repository topics..."
    
    $topics = @("azure-functions", "python", "api", "zipcode", "population-density", "serverless", "geospatial", "demographics")
    
    try {
        gh repo edit --add-topic ($topics -join ",")
        Write-Success "Repository topics added"
    } catch {
        Write-Warning "Could not add topics: $($_.Exception.Message)"
    }

    # Setup GitHub Actions secrets information
    Write-Info "[8/8] GitHub Actions setup information..."
    
    Write-Header "Next Steps for Azure Deployment"
    
    Write-Host ""
    Write-Success "Repository created successfully! 🎉"
    Write-Host "  📍 Repository: $repoUrl" -ForegroundColor White
    Write-Host "  🔧 Topics: $($topics -join ', ')" -ForegroundColor White
    
    Write-Host ""
    Write-Warning "To enable automated Azure deployment via GitHub Actions:"
    Write-Host ""
    Write-Host "1. Create Azure Service Principal:" -ForegroundColor Yellow
    Write-Host "   az ad sp create-for-rbac --name `"$RepoName-deploy`" --role contributor --scopes /subscriptions/{subscription-id} --sdk-auth" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Add GitHub Secrets (Settings > Secrets and variables > Actions):" -ForegroundColor Yellow
    Write-Host "   • AZURE_CREDENTIALS - Service principal JSON from step 1" -ForegroundColor Gray
    Write-Host "   • AZURE_FUNCTIONAPP_NAME - Your Azure Function App name" -ForegroundColor Gray
    Write-Host "   • AZURE_FUNCTIONAPP_RESOURCE_GROUP - Your resource group name" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Manual deployment option:" -ForegroundColor Yellow
    Write-Host "   Run: .\deploy-azure.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Push changes to trigger GitHub Actions deployment:" -ForegroundColor Yellow
    Write-Host "   git push origin main" -ForegroundColor Gray
    
    Write-Host ""
    Write-Success "API Features Ready:"
    Write-Host "  🎯 Density Assessment - Comprehensive zipcode analysis" -ForegroundColor White
    Write-Host "  📊 Statistics - Basic zipcode information" -ForegroundColor White
    Write-Host "  🗺️  Proximity Search - Find nearby zipcodes" -ForegroundColor White
    Write-Host "  ❤️  Health Monitoring - System status and diagnostics" -ForegroundColor White
    Write-Host "  📖 Swagger UI - Interactive API documentation" -ForegroundColor White
    Write-Host "  📈 Dataset - 33,784+ zipcodes with population density data" -ForegroundColor White
    
    Write-Host ""

} catch {
    Write-Error "GitHub setup failed: $($_.Exception.Message)"
    Write-Host ""
    Write-Warning "Troubleshooting steps:"
    Write-Host "  1. Ensure Git is installed and configured" -ForegroundColor Gray
    Write-Host "  2. Install GitHub CLI: winget install --id GitHub.cli" -ForegroundColor Gray
    Write-Host "  3. Authenticate: gh auth login" -ForegroundColor Gray
    Write-Host "  4. Check repository name availability" -ForegroundColor Gray
    Write-Host ""
    exit 1
}