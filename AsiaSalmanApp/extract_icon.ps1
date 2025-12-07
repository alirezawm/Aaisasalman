# Extract PNG image from SVG file

$svgFile = "New Text Document.txt"
$outputFile = "app_icon.png"

Write-Host "Reading SVG file: $svgFile" -ForegroundColor Cyan

if (-not (Test-Path $svgFile)) {
    Write-Host "ERROR: File $svgFile not found!" -ForegroundColor Red
    exit 1
}

# Read SVG content
$svgContent = Get-Content $svgFile -Raw -Encoding UTF8

# Find base64 encoded image
$pattern = 'data:image/png;base64,([A-Za-z0-9+/=]+)'
$match = [regex]::Match($svgContent, $pattern)

if (-not $match.Success) {
    Write-Host "ERROR: PNG image not found in SVG file!" -ForegroundColor Red
    exit 1
}

$base64Data = $match.Groups[1].Value
Write-Host "SUCCESS: Base64 data found (length: $($base64Data.Length) characters)" -ForegroundColor Green

try {
    # Decode base64
    $pngBytes = [System.Convert]::FromBase64String($base64Data)
    Write-Host "SUCCESS: PNG image extracted (size: $($pngBytes.Length) bytes)" -ForegroundColor Green
    
    # Save PNG file
    $outputPath = Join-Path (Get-Location) $outputFile
    [System.IO.File]::WriteAllBytes($outputPath, $pngBytes)
    Write-Host "SUCCESS: Image saved to $outputFile" -ForegroundColor Green
    Write-Host ""
    Write-Host "Icon image extracted successfully: $outputFile" -ForegroundColor Green
    Write-Host "You can now use this file for the app icon." -ForegroundColor Yellow
} catch {
    Write-Host "ERROR processing image: $_" -ForegroundColor Red
    exit 1
}
