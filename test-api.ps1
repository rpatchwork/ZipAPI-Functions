# Test the ZipCode Azure Functions API endpoints

Write-Host "🧪 Testing ZipCode Population Density API..." -ForegroundColor Green
Write-Host ""

$baseUrl = "http://localhost:7071/api"

# Test Health Check
Write-Host "1️⃣  Testing Health Check..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -TimeoutSec 30
    Write-Host "✅ Health Check: $($health.status)" -ForegroundColor Green
    Write-Host "   📊 Dataset: $($health.data_service.total_zipcodes) zipcodes loaded" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test Swagger/OpenAPI Documentation
Write-Host "2️⃣  Testing Swagger Documentation..." -ForegroundColor Cyan
try {
    $swagger = Invoke-WebRequest -Uri "$baseUrl/docs?format=json" -Method Get -TimeoutSec 30
    $swaggerSpec = $swagger.Content | ConvertFrom-Json
    Write-Host "✅ Swagger Documentation: OpenAPI $($swaggerSpec.openapi)" -ForegroundColor Green
    Write-Host "   📖 API Title: $($swaggerSpec.info.title)" -ForegroundColor White
    Write-Host "   🔗 Interactive Docs: http://localhost:7071/api/docs" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ Swagger Documentation Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test ZipCode Stats
Write-Host "3️⃣  Testing ZipCode Stats (NYC)..." -ForegroundColor Cyan
try {
    $stats = Invoke-RestMethod -Uri "$baseUrl/zipcode/10001/stats" -Method Get -TimeoutSec 30
    Write-Host "✅ ZipCode Stats: $($stats.zipcode)" -ForegroundColor Green
    Write-Host "   📍 Location: $($stats.location.city), $($stats.location.county_name)" -ForegroundColor White
    Write-Host "   📊 Density: $([math]::Round($stats.demographics.population_density, 1)) people/sq mi" -ForegroundColor White
    Write-Host "   🎯 Score: $($stats.density_analysis.density_score)/100" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ ZipCode Stats Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test Nearby ZipCodes
Write-Host "4️⃣  Testing Nearby ZipCodes (NYC area)..." -ForegroundColor Cyan
try {
    $nearby = Invoke-RestMethod -Uri "$baseUrl/zipcode/10001/nearby?radius=10&limit=5" -Method Get -TimeoutSec 30
    Write-Host "✅ Nearby ZipCodes: Found $($nearby.total_found), returned $($nearby.returned_count)" -ForegroundColor Green
    Write-Host "   📍 Center: $($nearby.center_zipcode.city) ($($nearby.center_zipcode.zipcode))" -ForegroundColor White
    if ($nearby.nearby_zipcodes.Count -gt 0) {
        Write-Host "   🗺️  Nearest: $($nearby.nearby_zipcodes[0].city) ($($nearby.nearby_zipcodes[0].zipcode)) - $($nearby.nearby_zipcodes[0].distance_miles) miles" -ForegroundColor White
    }
    Write-Host ""
} catch {
    Write-Host "❌ Nearby ZipCodes Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# Test Density Assessment
Write-Host "5️⃣  Testing Density Assessment (Beverly Hills)..." -ForegroundColor Cyan
try {
    $assessmentBody = @{
        zipcode = "90210"
        radius_miles = 25
    } | ConvertTo-Json
    
    $assessment = Invoke-RestMethod -Uri "$baseUrl/zipcode/density" -Method Post -Body $assessmentBody -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Density Assessment: $($assessment.zipcode)" -ForegroundColor Green
    Write-Host "   📍 Location: $($assessment.city), $($assessment.county_name)" -ForegroundColor White
    Write-Host "   📊 Density: $([math]::Round($assessment.population_density, 1)) people/sq mi" -ForegroundColor White
    Write-Host "   🎯 Score: $($assessment.density_score)/100 (Percentile: $($assessment.national_percentile)%)" -ForegroundColor White
    Write-Host "   🏠 Nearby: $($assessment.nearby_stats.nearby_count) zipcodes, $($assessment.nearby_stats.relative_score) density" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ Density Assessment Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "🎉 API Testing Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Available Endpoints:" -ForegroundColor Yellow
Write-Host "   🔍 Health:      GET    $baseUrl/health" -ForegroundColor White
Write-Host "   📖 Swagger UI:  GET    $baseUrl/docs" -ForegroundColor White  
Write-Host "   📊 Stats:       GET    $baseUrl/zipcode/{zipcode}/stats" -ForegroundColor White
Write-Host "   🗺️  Nearby:     GET    $baseUrl/zipcode/{zipcode}/nearby" -ForegroundColor White
Write-Host "   🎯 Assessment:  POST   $baseUrl/zipcode/density" -ForegroundColor White
Write-Host ""