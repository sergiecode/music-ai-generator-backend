# Test script for music generation and download
Write-Host "Testing Music Generation and Download..." -ForegroundColor Green

# Test 1: Generate music
Write-Host "`nStep 1: Generating music..." -ForegroundColor Yellow
$headers = @{"Content-Type" = "application/json"}
$body = @{
    prompt = "test music for download"
    duration = 30
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/music/generate" -Method POST -Headers $headers -Body $body
    Write-Host "Generation successful!" -ForegroundColor Green
    Write-Host "Track ID: $($response.track_id)" -ForegroundColor Cyan
    $trackId = $response.track_id
} catch {
    Write-Host "Generation failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Wait for completion
Write-Host "`nStep 2: Waiting for generation to complete..." -ForegroundColor Yellow
$maxWait = 60  # Maximum wait time in seconds
$waited = 0

do {
    Start-Sleep -Seconds 2
    $waited += 2
    
    try {
        $status = Invoke-RestMethod -Uri "http://127.0.0.1:8000/music/status/$trackId" -Method GET
        Write-Host "Progress: $($status.progress)% - Status: $($status.status)" -ForegroundColor Cyan
        
        if ($status.status -eq "completed") {
            Write-Host "Generation completed!" -ForegroundColor Green
            Write-Host "Download URL: $($status.download_url)" -ForegroundColor Cyan
            break
        } elseif ($status.status -eq "failed") {
            Write-Host "Generation failed!" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "Status check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
} while ($waited -lt $maxWait)

if ($waited -ge $maxWait) {
    Write-Host "Timeout waiting for generation to complete" -ForegroundColor Red
    exit 1
}

# Test 3: Test download endpoint
Write-Host "`nStep 3: Testing download endpoint..." -ForegroundColor Yellow
try {
    $downloadUrl = "http://127.0.0.1:8000/downloads/$trackId.mp3"
    Write-Host "Testing URL: $downloadUrl" -ForegroundColor Cyan
    
    # Use HEAD request to test if file exists
    $headResponse = Invoke-WebRequest -Uri $downloadUrl -Method HEAD
    Write-Host "Download endpoint responds with status: $($headResponse.StatusCode)" -ForegroundColor Green
    
    # Check if file exists locally
    $filePath = "downloads\$trackId.mp3"
    if (Test-Path $filePath) {
        $fileSize = (Get-Item $filePath).Length
        Write-Host "Local file exists: $filePath (Size: $fileSize bytes)" -ForegroundColor Green
    } else {
        Write-Host "Local file not found: $filePath" -ForegroundColor Red
    }
    
} catch {
    Write-Host "Download test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
}

Write-Host "`nTest completed!" -ForegroundColor Green
